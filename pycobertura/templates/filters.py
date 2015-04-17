"""
Jinja2 filters meant to be used by templates.
"""

line_status_style_class = {
    True: 'hit',
    False: 'miss',
    None: 'noop',
}


line_reason_html_icon = {
    'line-edit': '+',
    'cov-up': '&nbsp;',
    'cov-down': '&nbsp;',
    None: '&nbsp;',
}


def line_status_class(line):
    return line_status_style_class[line.status]


def line_reason_icon(line):
    if line.status is None:
        return '&nbsp;'
    return line_reason_html_icon[line.reason]
