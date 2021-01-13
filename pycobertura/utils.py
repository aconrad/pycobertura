import difflib
import os

from functools import partial

ANSI_ESCAPE_CODES = {
    "green": "\x1b[32m",
    "red": "\x1b[31m",
    "reset": "\x1b[39m",
}


# Recipe from https://github.com/ActiveState/
# code/recipes/Python/577452_memoize_decorator_instance/recipe-577452.py
class memoize(object):
    """cache the return value of a method

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj(object):
        @memoize
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res


def colorize(text, color):
    color_code = ANSI_ESCAPE_CODES[color]
    return "%s%s%s" % (color_code, text, ANSI_ESCAPE_CODES["reset"])


def red(text):
    return colorize(text, "red")


def green(text):
    return colorize(text, "green")


def rangify(number_list):
    """Assumes the list is sorted."""
    if not number_list:
        return number_list

    ranges = []

    range_start = prev_num = number_list[0]
    for num in number_list[1:]:
        if num != (prev_num + 1):
            ranges.append((range_start, prev_num))
            range_start = num
        prev_num = num

    ranges.append((range_start, prev_num))
    return ranges


def extrapolate_coverage(lines_w_status):
    """
    Given the following input:

    >>> lines_w_status = [
        (1, True),
        (4, True),
        (7, False),
        (9, False),
    ]

    Return expanded lines with their extrapolated line status.

    >>> extrapolate_coverage(lines_w_status) == [
        (1, True),
        (2, True),
        (3, True),
        (4, True),
        (5, None),
        (6, None),
        (7, False),
        (8, False),
        (9, False),
    ]

    """
    lines = []

    prev_lineno = 0
    prev_status = True
    for lineno, status in lines_w_status:
        while (lineno - prev_lineno) > 1:
            prev_lineno += 1
            if prev_status is status:
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
