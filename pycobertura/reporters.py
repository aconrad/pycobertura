from jinja2 import Environment, PackageLoader
from pycobertura.utils import green, rangify, red
from pycobertura.cobertura import CoberturaDiff
from tabulate import tabulate


env = Environment(loader=PackageLoader('pycobertura', 'templates'))


def get_class_summary_row(cobertura, class_name):
    if not cobertura.has_class(class_name):
        return None

    row = [
        class_name,
        cobertura.total_statements(class_name),
        cobertura.total_misses(class_name),
        cobertura.line_rate(class_name),
        cobertura.missed_lines(class_name),
    ]
    return row


class Reporter(object):
    def __init__(self, cobertura):
        self.cobertura = cobertura

    def get_report_row_by_class(self, class_name):
        total_lines = self.cobertura.total_statements(class_name)
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

    def get_footer_row(self):
        total_statements = self.cobertura.total_statements()
        total_misses = self.cobertura.total_misses()
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

        footer = self.get_footer_row()
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
    def __init__(self, *args, **kwargs):
        super(HtmlReporter, self).__init__(*args, **kwargs)

    def get_source(self, class_name):
        lines = self.cobertura.class_source(class_name)
        status_map = {True: 'hit', False: 'miss', None: 'noop'}
        return [(lno, src, status_map[status]) for lno, src, status in lines]

    def generate(self):
        lines = self.get_report_lines()

        formatted_lines = []
        for row in lines:
            formatted_row = self.format_row(row)
            formatted_lines.append(formatted_row)

        sources = []
        for class_name in self.cobertura.classes():
            source = self.get_source(class_name)
            filename = self.cobertura.filename(class_name)
            sources.append((class_name, filename, source))

        template = env.get_template('html.jinja2')
        return template.render(
            lines=formatted_lines[:-1],
            footer=formatted_lines[-1],
            sources=sources
        )


class DeltaReporter(object):
    def __init__(self, cobertura1, cobertura2):
        self.differ = CoberturaDiff(cobertura1, cobertura2)

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

    def get_footer_row(self):
        total_statements = self.differ.diff_total_statements()
        total_misses = self.differ.diff_total_misses()
        total_line_rate = self.differ.diff_line_rate()

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

        classes1 = self.differ.cobertura1.classes()
        classes2 = self.differ.cobertura2.classes()
        all_classes = set(classes1).union(set(classes2))
        for class_name in sorted(all_classes):
            row1 = get_class_summary_row(self.differ.cobertura1, class_name)
            row2 = get_class_summary_row(self.differ.cobertura2, class_name)
            row = self.get_diff_line(row1, row2)
            lines.append(row)

        footer = self.get_footer_row()
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
    def get_source_hunks(self, class_name):
        hunks = self.differ.class_source_hunks(class_name)
        status_map = {True: 'hit', False: 'miss', None: 'noop'}
        new_hunks = []
        for hunk in hunks:
            new_hunk = []
            for lno, src, status in hunk:
                new_hunk.append((lno, src, status_map[status]))
            new_hunks.append(new_hunk)
        return new_hunks

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

        sources = []
        for class_name in self.differ.cobertura2.classes():
            source_hunks = self.get_source_hunks(class_name)
            if not source_hunks:
                continue
            filename = self.differ.cobertura2.filename(class_name)
            sources.append((class_name, filename, source_hunks))

        template = env.get_template('html-delta.jinja2')
        return template.render(
            lines=formatted_lines[:-1],
            footer=formatted_lines[-1],
            sources=sources
        )
