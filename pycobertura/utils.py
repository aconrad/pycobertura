import colorama
import difflib


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
