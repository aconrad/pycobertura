"""
Jinja2 filters meant to be used by templates.
"""

from pycobertura.utils import green, red

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

def total_misses_span(total_misses):
    return total_misses != '-'

def misses_color(arg):
    return "red" if arg == '+' else "green"

def line_status(line):
    return line_status_style[line.status]


def line_reason_icon(line):
    if line.status is None:
        return "&nbsp;"
    return line_reason_html_icon[line.reason]
