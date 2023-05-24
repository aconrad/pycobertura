import difflib
import os
import re
import fnmatch
from functools import partial

from typing import List, Tuple, Union

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal

ANSI_ESCAPE_CODES = {
    "green": "\x1b[32m",
    "red": "\x1b[31m",
    "reset": "\x1b[39m",
}


# Recipe from
# https://github.com/ActiveState/code/blob/master/recipes/Python/577452_memoize_decorator_instance/recipe-577452.py
class memoize:
    """cache the return value of a method

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj:
        @memoize
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached
    """

    def __init__(self, func):
        self.target_func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.target_func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        target_self = args[0]
        try:
            cache = target_self.__cache
        except AttributeError:
            cache = target_self.__cache = {}
        key = (self.target_func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.target_func(*args, **kw)
        return res


def colorize(text, color):
    color_code = ANSI_ESCAPE_CODES[color]
    return f'{color_code}{text}{ANSI_ESCAPE_CODES["reset"]}'


def red(text):
    return colorize(text, "red")


def green(text):
    return colorize(text, "green")


LineStatus = Literal["hit", "miss", "partial"]
LineStatusTuple = Tuple[int, LineStatus]
LineTupleWithStatusNone = Tuple[int, Union[LineStatus, None]]
LineRangeWithStatusNone = Tuple[int, int, Union[LineStatus, None]]


def rangify_by_status(line_statuses: List[LineTupleWithStatusNone]):
    """
    Returns a list of range tuples that represent continuous segments by status,
    such as `(range_start, range_end, status)` given a list of sorted
    non-continuous integers `line_statuses` with their status.

    For example: [(1, "hit"), (2, "hit"), (3, "miss"), (4, "hit")]
    Would return: [(1, 2, "hit"), (3, 3, "miss"), (4, 4, "hit")]
    """
    ranges: List[LineRangeWithStatusNone] = []
    if not line_statuses:
        return ranges

    range_start, *_ = prev_num, prev_status = line_statuses[0]
    for num, status in line_statuses[1:]:
        if num != (prev_num + 1) or status != prev_status:
            ranges.append((range_start, prev_num, prev_status))
            range_start = num
        prev_num = num
        prev_status = status

    ranges.append((range_start, prev_num, prev_status))
    return ranges


def stringify(line_statuses):
    """Assumes the list is sorted."""
    rangified_list = rangify_by_status(line_statuses)

    stringified_list = []
    for line_start, line_stop, status in rangified_list:
        prefix = "~" if status == "partial" else ""
        if line_start == line_stop:
            stringified = f"{prefix}{line_start}"
        else:
            stringified = f"{prefix}{line_start}-{line_stop}"
        stringified_list.append(stringified)

    return ", ".join(stringified_list)


def extrapolate_coverage(lines_w_status):
    """
    Given the following input:

    >>> lines_w_status = [
        (1, "hit"),
        (4, "hit"),
        (7, "miss"),
        (9, "miss"),
    ]

    Return expanded lines with their extrapolated line status.

    >>> extrapolate_coverage(lines_w_status) == [
        (1, "hit"),
        (2, "hit"),
        (3, "hit"),
        (4, "hit"),
        (5, None),
        (6, None),
        (7, "miss"),
        (8, "miss"),
        (9, "miss"),
    ]

    """
    lines: List[LineTupleWithStatusNone] = []

    prev_lineno = 0
    prev_status = "hit"
    for lineno, status in lines_w_status:
        while (lineno - prev_lineno) > 1:
            prev_lineno += 1
            if prev_status == status:
                lines.append((prev_lineno, status))
            else:
                lines.append((prev_lineno, None))
        lines.append((lineno, status))
        prev_lineno = lineno
        prev_status = status

    return lines


def reconcile_lines(lines1, lines2):
    """
    Return a dict `{lineno1: lineno2}` which reconciles line numbers `lineno1`
    of list `lines1` to line numbers `lineno2` of list `lines2`. Only lines
    that are common in both sets are present in the dict, lines unique to one
    of the sets are omitted.
    """
    differ = difflib.Differ()
    diff = differ.compare(lines1, lines2)

    SAME = "  "
    ADDED = "+ "
    REMOVED = "- "
    INFO = "? "

    lineno_map = {}  # {lineno1: lineno2, ...}
    lineno1_offset = 0
    lineno2 = 1

    for diffline in diff:
        if diffline.startswith(INFO):
            continue

        if diffline.startswith(SAME):
            lineno1 = lineno2 + lineno1_offset
            lineno_map[lineno1] = lineno2

        elif diffline.startswith(ADDED):
            lineno1_offset -= 1

        elif diffline.startswith(REMOVED):
            lineno1_offset += 1
            continue

        lineno2 += 1

    return lineno_map


def hunkify_lines(lines, context=3):
    """
    Return a list of line hunks given a list of lines `lines`. The number of
    context lines can be control with `context` which will return line hunks
    surrounded with `context` lines before and after the code change.
    """
    # Find contiguous line changes
    ranges = []
    range_start = None
    for i, line in enumerate(lines):
        if line.status is not None:
            if range_start is None:
                range_start = i
                continue
        elif range_start is not None:
            range_stop = i
            ranges.append((range_start, range_stop))
            range_start = None
    else:
        # Append the last range
        if range_start is not None:
            range_stop = i
            ranges.append((range_start, range_stop))

    # add context
    ranges_w_context = []
    for range_start, range_stop in ranges:
        range_start = range_start - context
        range_start = range_start if range_start >= 0 else 0
        range_stop = range_stop + context
        ranges_w_context.append((range_start, range_stop))

    # merge overlapping hunks
    merged_ranges = ranges_w_context[:1]
    for range_start, range_stop in ranges_w_context[1:]:
        prev_start, prev_stop = merged_ranges[-1]
        if range_start <= prev_stop:
            range_start = prev_start
            merged_ranges[-1] = (range_start, range_stop)
        else:
            merged_ranges.append((range_start, range_stop))

    # build final hunks
    hunks = []
    for range_start, range_stop in merged_ranges:
        hunk = lines[range_start:range_stop]
        hunks.append(hunk)

    return hunks


def get_dir_from_file_path(file_path):
    return os.path.dirname(file_path) or "."


def get_non_empty_non_commented_lines_from_file_in_ascii(file_path, comment_character):
    with open(file_path, "rb") as f:  # read in binary (more secure)
        result = [
            line.decode("ascii").strip()
            for line in f.readlines()
            if not line.decode("ascii").startswith(comment_character)
        ]
        return [res for res in result if res != ""]


def get_filenames_that_do_not_match_regex(
    filenames, regex_param, comment_character="#"
):
    if os.path.isfile(regex_param):
        ignore_patterns = get_non_empty_non_commented_lines_from_file_in_ascii(
            regex_param, comment_character
        )
        remove_filenames = [
            filename
            for igp in ignore_patterns
            for filename in fnmatch.filter(filenames, igp)
        ]
    else:
        remove_filenames = list(filter(re.compile(regex_param).match, filenames))
    return [fname for fname in filenames if fname not in remove_filenames]


def get_line_status(line):
    """
    Returns the line status as "hit", "miss", or "partial". Line is an XML
    Element from a Cobertura report of type `line`.
    """
    condition = line.get("condition-coverage")
    status: LineStatus
    if condition:
        if condition.startswith("100%"):
            status = "hit"
        elif condition.startswith("0%"):
            status = "miss"
        else:
            status = "partial"
    else:
        status: LineStatus = "miss" if line.get("hits") == "0" else "hit"

    return status


def calculate_line_rate(total_statements: int, total_misses: int):
    return (
        (total_statements - total_misses) / total_statements if total_statements else 1
    )
