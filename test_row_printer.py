from row_printer import ColumnSpec, RowCollection


class TestColumnSpec:
    def test_it_has_name_and_width(self):
        column = ColumnSpec('id', width=4)
        assert 'id' == column.name
        assert 4 == column.width

    def test_it_has_an_optional_func(self):
        column = ColumnSpec('id', width=4)
        assert 'hello' == column.func('hello')
        assert '' == column.func('')
        assert 7 == column.func(7)

        func = lambda x: x.upper()
        column = ColumnSpec('id', width=4, func=func)
        assert 'HELLO' == column.func('hello')


class TestRowCollection:
    @property
    def id_column(self):
        return ColumnSpec('id', width=4)

    @property
    def name_column(self):
        return ColumnSpec('name', width=8)

    @property
    def it(self):
        headers = ('id', 'name')
        column_specs = (self.id_column, self.name_column)
        return RowCollection('units', column_specs=column_specs, headers=headers)

    def test_it_takes_a_column_specs_list_and_headers_list(self):
        headers = ('id', 'name')
        column_specs = (self.id_column, self.name_column)
        rows = RowCollection('units', column_specs=column_specs, headers=headers)
        assert column_specs == rows.column_specs
        assert headers == rows.headers

    def test_it_creates_a_row_class_from_headers(self):
        rows = self.it
        assert 'hello' == rows.Row(id=1, name='hello').name
        assert 1 == rows.Row(id=1, name='hello').id

    def test_you_can_append_rows_to_it(self):
        rows = self.it
        rows.append({'name': 'Sam', 'id': 1})
        assert 1 == rows[0].id
        assert 'Sam' == rows[0].name

    def test_it_has_a_length(self):
        rows = self.it
        assert len(rows) == 0
        rows.append({'name': 'Sam', 'id': 1})
        assert len(rows) == 1

    def test_it_knows_how_to_format_the_header_row(self):
        rows = self.it
        assert '| id   | name     |' == rows.header_row

    def test_it_knows_how_to_format_break_lines(self):
        rows = self.it
        assert '| ---- | -------- |' == rows.break_line

    def test_it_knows_how_to_print_itself(self):
        rows = self.it
        rows.append({'name': 'Sam', 'id': 1})
        rows.append({'name': 'Layla', 'id': 2})
        rows.append({'name': 'Jack Gabriel', 'id': 3})
        expected = """\
| id   | name     |
| ---- | -------- |
| 1    | Sam      |
| 2    | Layla    |
| 3    | Jack Ga… |
| ---- | -------- |"""
        assert expected == str(rows)