from collections import namedtuple
from datetime import datetime
from decimal import Decimal


class ColumnSpec:
    def __init__(self, name, width=10, func=lambda x: x):
        self.name = name
        self.type = type
        self.func = func
        self.width = width

    def transform(self, item):
        if item is None:
            item = '∅'
        transformed = self.func(item)
        if type(transformed) != str:
            transformed = str(transformed)
        if len(transformed) <= self.width:
            return transformed.ljust(self.width)
        else:
            truncated = transformed[: self.width - 1] + '…'
            return truncated.ljust(self.width)


class RowCollection:
    def __init__(self, name, column_specs, headers):
        self.column_specs = column_specs
        self.headers = headers
        if len(headers) != len(column_specs):
            raise Exception('Header, column_spec length mismatch')
        self.Row = namedtuple(name.capitalize(), headers)
        self._rows = []

    def append(self, row_dict):
        row = self.Row(**row_dict)
        self._rows.append(row)

    def _join_items_to_pipes(self, items):
        inner_cols = ' | '.join(i for i in items)
        return f'| {inner_cols} |'

    @property
    def header_row(self):
        header_row_items = []
        for col_spec, header in zip(self.column_specs, self.headers):
            width = col_spec.width
            if len(header) <= width:
                header_row_items.append(header.ljust(width))
            else:
                truncated_header = header[: width - 1] + '…'
                header_row_items.append(truncated_header.ljust(width))
        return self._join_items_to_pipes(header_row_items)

    @property
    def break_line(self):
        break_line_items = []
        for col_spec in self.column_specs:
            col_break_line = '-' * col_spec.width
            break_line_items.append(col_break_line)
        return self._join_items_to_pipes(break_line_items)

    def make_printable_row(self, row):
        row_items = []
        for col_spec, item in zip(self.column_specs, row):
            row_items.append(col_spec.transform(item))
        return self._join_items_to_pipes(row_items)

    @property
    def printable_rows(self):
        return '\n'.join(self.make_printable_row(row) for row in self._rows)

    def __str__(self):
        return f"""\
{self.header_row}
{self.break_line}
{self.printable_rows}
{self.break_line}"""

    def __getitem__(self, position):
        return self._rows[position]

    def __len__(self):
        return len(self._rows)


def pretty_date(d: datetime) -> str:
    hours_minutes_seconds = d.strftime('%H:%M:%S')
    pretty = d.strftime(f'%Y-%m-%d {hours_minutes_seconds}')
    return pretty.ljust(19)


def pretty_money(amount) -> str:
    rounded_str = '${0:,.2f}'.format(amount)
    return rounded_str


def pretty_generic_decimal(amount) -> str:
    rounded_str = '{0:,.2f}'.format(amount)
    return rounded_str


def pretty_int(amount) -> str:
    rounded_str = '{0:,.0f}'.format(amount)
    return rounded_str


def get_max_width_of_items(items):
    max_width = 0
    for item in items:
        if len(str(item)) > max_width:
            max_width = len(str(item))
    return max_width


def guess_row_collection(rows):
    col_specs = []
    column_names = rows[0].keys()
    for column_name in column_names:
        column_type = type(rows[0][column_name])
        values = [r[column_name] for r in rows if r[column_name] is not None]
        # spec = ColumnSpec(
        #     column_name, width=get_max_width_of_items([column_name] + values)
        # )
        if column_type == datetime:
            spec = ColumnSpec(column_name, width=19, func=pretty_date)
        if column_type in (Decimal, float):
            spec = ColumnSpec(
                column_name,
                width=get_max_width_of_items([column_name] + values) + 6,
                func=pretty_generic_decimal,
            )
        if column_type == int:
            spec = ColumnSpec(
                column_name, width=get_max_width_of_items([column_name] + values)
            )
        else:
            spec = ColumnSpec(
                column_name, width=get_max_width_of_items([column_name] + values)
            )
        col_specs.append(spec)
    return RowCollection(
        'GuessedRowCollection', column_specs=col_specs, headers=column_names
    )
