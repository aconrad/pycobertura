"""
Jinja2 filters meant to be used by templates.
"""

line_status_style = {
    True: "hit",
    False: "miss",
    None: "noop",
}


line_reason_html_icon = {
    "line-edit": "+",
    "cov-up": "&nbsp;",
    "cov-down": "&nbsp;",
    None: "&nbsp;",
}


def is_not_equal_to_dash(arg):
    return not (arg == "-")


def misses_color(arg):
    if arg.startswith("+") or arg[0].isdigit():
        return "red"
    return "green"


def line_status(line):
    return line_status_style[line.status]


def line_reason_icon(line):
    if line.status is None:
        return "&nbsp;"
    return line_reason_html_icon[line.reason]
