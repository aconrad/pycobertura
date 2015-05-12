import colorama
import difflib
import functools


# https://gist.github.com/267733/8f5d2e3576b6a6f221f6fb7e2e10d395ad7303f9
class memoize(object):
    def __init__(self, func):
        self.func = func
        self.memoized = {}
        self.method_cache = {}

    def __call__(self, *args):
        return self.cache_get(self.memoized, args, lambda: self.func(*args))

    def __get__(self, obj, objtype):
        return self.cache_get(
            self.method_cache, obj,
            lambda: self.__class__(functools.partial(self.func, obj))
        )

    def cache_get(self, cache, key, func):
        try:
            return cache[key]
        except KeyError:
            v = cache[key] = func()
            return v


def colorize(text, color):
    color_code = getattr(colorama.Fore, color.upper())
    return '%s%s%s' % (color_code, text, colorama.Fore.RESET)


def red(text):
    return colorize(text, 'red')


def green(text):
    return colorize(text, 'green')


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

    SAME = '  '
    ADDED = '+ '
    REMOVED = '- '
    INFO = '? '

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
