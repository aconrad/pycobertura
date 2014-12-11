from jinja2 import Environment, PackageLoader
from pycobertura.utils import green, rangify, red
from tabulate import tabulate


env = Environment(loader=PackageLoader('pycobertura', 'templates'))


def get_class_summary_row(cobertura, class_name):
    if not cobertura.has_class(class_name):
        return None

    row = [
        class_name,
        cobertura.total_lines(class_name),
        cobertura.total_misses(class_name),
        cobertura.line_rate(class_name),
        cobertura.missed_lines(class_name),
    ]
    return row


class Reporter(object):
    def __init__(self, cobertura):
        self.cobertura = cobertura

    def get_report_row_by_class(self, class_name):
        total_lines = self.cobertura.total_lines(class_name)
        line_rate = self.cobertura.line_rate(class_name)
        total_misses = self.cobertura.total_misses(class_name)
        missed_lines = self.cobertura.missed_lines(class_name)

        row = [
            class_name,
            total_lines,
            total_misses,
            line_rate,
            missed_lines,
        ]

        return row

    def get_footer_row(self, lines):
        total_statements = 0
        total_misses = 0
        line_rates = []

        for class_name, total_lines, misses, line_rate, missed_lines in lines:
            total_statements += total_lines
            total_misses += misses
            line_rates.append(line_rate)

        total_line_rate = self.cobertura.line_rate()

        footer = [
            'TOTAL',
            total_statements,
            total_misses,
            total_line_rate,
            [],  # dummy missed lines
        ]

        return footer

    def get_report_lines(self):
        lines = []

        for class_name in self.cobertura.classes():
            row = get_class_summary_row(self.cobertura, class_name)
            lines.append(row)

        footer = self.get_footer_row(lines)
        lines.append(footer)

        return lines


class TextReporter(Reporter):
    def format_row(self, row):
        class_name, total_lines, total_misses, line_rate, missed_lines = row

        line_rate = '%.2f%%' % (line_rate * 100)

        formatted_missed_lines = []
        for line_start, line_stop in rangify(missed_lines):
            if line_start == line_stop:
                formatted_missed_lines.append('%s' % line_start)
            else:
                line_range = '%s-%s' % (line_start, line_stop)
                formatted_missed_lines.append(line_range)
        formatted_missed_lines = ', '.join(formatted_missed_lines)

        row = [
            class_name,
            total_lines,
            total_misses,
            line_rate,
            formatted_missed_lines,
        ]

        return row

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = []
        for row in lines:
            formatted_row = self.format_row(row)
            formatted_lines.append(formatted_row)

        report = tabulate(
            formatted_lines,
            headers=['Name', 'Stmts', 'Miss', 'Cover', 'Missing']
        )

        return report


class HtmlReporter(TextReporter):

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = []
        for row in lines:
            formatted_row = self.format_row(row)
            formatted_lines.append(formatted_row)

        template = env.get_template('html.jinja2')
        return template.render(
            lines=formatted_lines[:-1],
            footer=formatted_lines[-1]
        )


class DeltaReporter(object):
    def __init__(self, cobertura1, cobertura2):
        self.cobertura1 = cobertura1
        self.cobertura2 = cobertura2

    def get_diff_line(self, line1, line2):
        if line1 is not None:
            (class_name1,
             total_lines1,
             total_misses1,
             line_rate1,
             missed_lines1) = line1
            class_name = class_name1
        if line2 is not None:
            (class_name2,
             total_lines2,
             total_misses2,
             line_rate2,
             missed_lines2) = line2
            class_name = class_name2

        if None not in (line1, line2):
            added_lines = set(missed_lines2).difference(missed_lines1)
            removed_lines = set(missed_lines1).difference(missed_lines2)
            all_lines = sorted(added_lines.union(removed_lines))
        elif line1 is None:
            added_lines = all_lines = missed_lines2
        elif line2 is None:
            added_lines = set()
            all_lines = missed_lines1

        # Early return if line2 is None, the class doesn't exist anymore in
        # the latest version.
        if line2 is None:
            return [
                class_name,
                -total_lines1,  # negate line number of previous coverage
                0,  # total misses not applicable
                0,  # line rate not applicable
                [],  # missing lines not applicable
            ]

        formatted_lines = []
        for line in all_lines:
            sign = '+' if line in added_lines else '-'
            formatted_line = (sign, line)
            formatted_lines.append(formatted_line)

        if None not in (line1, line2):
            diff_line = [
                class_name,
                total_lines2 - total_lines1,
                total_misses2 - total_misses1,
                line_rate2 - line_rate1,
                formatted_lines,
            ]
        elif line1 is None:
            diff_line = [
                class_name,
                total_lines2,
                total_misses2,
                line_rate2,
                formatted_lines,
            ]

        return diff_line

    def get_footer_row(self, lines):
        total_statements = 0
        total_misses = 0
        line_rates = []

        for class_name, total_lines, misses, line_rate, missed_lines in lines:
            total_statements += total_lines
            total_misses += misses
            line_rates.append(line_rate)

        total_line_rate1 = self.cobertura1.line_rate()
        total_line_rate2 = self.cobertura2.line_rate()
        total_line_rate = total_line_rate2 - total_line_rate1

        footer = [
            'TOTAL',
            total_statements,
            total_misses,
            total_line_rate,
            [],  # dummy missed lines
        ]

        return footer

    def get_report_lines(self):
        lines = []

        classes1 = self.cobertura1.classes()
        classes2 = self.cobertura2.classes()
        all_classes = set(classes1).union(set(classes2))
        for class_name in sorted(all_classes):
            row1 = get_class_summary_row(self.cobertura1, class_name)
            row2 = get_class_summary_row(self.cobertura2, class_name)
            row = self.get_diff_line(row1, row2)
            lines.append(row)

        footer = self.get_footer_row(lines)
        lines.append(footer)

        return lines


class TextReporterDelta(DeltaReporter):
    def __init__(self, *args, **kwargs):
        """
        Takes the same arguments as `DeltaReporter` but also takes the keyword
        argument `color` which can be set to True or False depending if the
        generated report should be colored or not (default `color=False`).
        """
        self.color = kwargs.pop('color', False)
        super(TextReporterDelta, self).__init__(*args, **kwargs)

    def format_row(self, row):
        class_name, total_lines, total_misses, line_rate, missed_lines = row

        total_lines = '%+d' % total_lines if total_lines else '-'
        total_misses = '%+d' % total_misses if total_misses else '-'
        line_rate = '%+.2f%%' % (line_rate * 100) if line_rate else '-'
        missed_lines = ['%s%d' % l for l in missed_lines]

        if self.color is True:
            missed_lines_colored = []
            for line in missed_lines:
                colorize = [green, red][line[0] == '+']
                colored_line = colorize(line)
                missed_lines_colored.append(colored_line)
        else:
            missed_lines_colored = missed_lines

        missed_lines = ', '.join(missed_lines_colored)

        row = [
            class_name,
            total_lines,
            total_misses,
            line_rate,
            missed_lines,
        ]

        return row

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = []
        for row in lines:
            formatted_row = self.format_row(row)
            formatted_lines.append(formatted_row)

        report = tabulate(
            formatted_lines,
            headers=['Name', 'Stmts', 'Miss', 'Cover', 'Missing']
        )

        return report


class HtmlReporterDelta(TextReporterDelta):
    def format_row(self, row):
        class_name, total_lines, total_misses, line_rate, missed_lines = row

        total_lines = '%+d' % total_lines if total_lines else '-'
        total_misses = '%+d' % total_misses if total_misses else '-'
        line_rate = '%+.2f%%' % (line_rate * 100) if line_rate else '-'
        missed_lines = ['%s%d' % l for l in missed_lines]

        missed_lines_colored = []
        for line in missed_lines:
            colorize = [green, red][line[0] == '+']
            colored_line = colorize(line)
            missed_lines_colored.append(colored_line)

        row = [
            class_name,
            total_lines,
            total_misses,
            line_rate,
            missed_lines,
        ]

        return row

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = []
        for row in lines:
            formatted_row = self.format_row(row)
            formatted_lines.append(formatted_row)

        template = env.get_template('html-delta.jinja2')
        return template.render(
            lines=formatted_lines[:-1],
            footer=formatted_lines[-1]
        )
