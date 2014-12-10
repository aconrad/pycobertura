import colorama


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
