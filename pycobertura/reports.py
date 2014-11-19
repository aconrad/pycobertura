from tabulate import tabulate


def format_row(row):
    class_name, total_lines, total_misses, line_rate, missed_ranges = row

    line_rate = '%.2f%%' % (line_rate * 100)

    missed_lines = []
    for line_start, line_stop in missed_ranges:
        if line_start == line_stop:
            missed_lines.append('%s' % line_start)
        else:
            missed_lines.append('%s-%s' % (line_start, line_stop))
    missed_lines = ', '.join(missed_lines)

    row = [
        class_name,
        total_lines,
        total_misses,
        line_rate,
        missed_lines,
    ]

    return row


def make_footer_row(lines):
    total_statements = 0
    total_misses = 0
    line_rates = []

    for class_name, total_lines, misses, line_rate, missed_lines in lines:
        total_statements += total_lines
        total_misses += misses
        line_rates.append(line_rate)

    avg_line_rate = sum(line_rates) / len(line_rates)

    footer = [
        'TOTAL',
        total_statements,
        total_misses,
        avg_line_rate,
        [],  # dummy missed lines
    ]

    return footer


class TextReport(object):
    def __init__(self, cobertura):
        self.cobertura = cobertura

    def get_report_row_by_class(self, class_name):
        total_lines = self.cobertura.total_lines(class_name)
        line_rate = self.cobertura.line_rate(class_name)
        total_misses = self.cobertura.total_misses(class_name)
        missed_ranges = self.cobertura.line_misses_ranges(class_name)

        row = [
            class_name,
            total_lines,
            total_misses,
            line_rate,
            missed_ranges,
        ]

        return row

    def get_report_lines(self):
        lines = []

        for class_name in self.cobertura.classes():
            row = self.get_report_row_by_class(class_name)
            lines.append(row)

        footer = make_footer_row(lines)
        lines.append(footer)

        return lines

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = []
        for row in lines:
            formatted_row = format_row(row)
            formatted_lines.append(formatted_row)

        report = tabulate(
            formatted_lines,
            headers=['Name', 'Stmts', 'Miss', 'Cover', 'Missing']
        )

        return report
