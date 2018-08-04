import os
import string
import re

import pytest

from SnowLibrary.keywords.file_creator import DataFile, DataRow, DataField


class TestDataFile:
    def test_define_file_name(self):
        f = DataFile()
        if os.path.sep == "\\":
            f.define_file_name("C:\\User\\mrose\\ws")
            assert f.absolute_name == "C:\\User\\mrose\\ws"
        else:
            f2 = DataFile("/My/File/Name.py")
            assert f2.absolute_name == "/My/File/Name.py"

    def test_file_name_is_not_absolute(self):
        f = DataFile()
        with pytest.raises(AssertionError) as e:
            f.define_file_name("path/is/not/absolute")
        assert "The file name must be absolute." in str(e)

    def test_data_file_has_new_row_definition(self):
        f = DataFile()
        assert isinstance(f.row_definition, DataRow)
        assert f.row_definition.field_count == 0

    def test_define_data_field(self):
        f = DataFile()
        f.define_data_field("Boolean", "BOOL_HEADER", options="Not Bool, Other Thing, True")
        assert f.row_definition.field_count == 1

    def test_invalid_delimiter_definition(self):
        f = DataFile()
        with pytest.raises(AssertionError) as e:
            f.define_delimiter("PERCENT")
        assert "Invalid delimiter.  Delimiter must be COMMA, PIPE, TAB, COLON, or SEMICOLON." in str(e)

    def test_valid_delimiter_definition_ignores_case(self):
        f = DataFile()
        f.define_delimiter("tab")
        assert f.delimiter == "\t"

    def test_number_of_detail_rows_must_be_positive(self):
        f = DataFile()
        with pytest.raises(AssertionError) as e:
            f.number_of_detail_rows_is(-1)
        assert "Number of details rows must be a positive integer." in str(e)

    def test_number_of_detail_rows_must_be_integer(self):
        f = DataFile()
        with pytest.raises(AssertionError) as e:
            f.number_of_detail_rows_is("Michael")
        assert "Failed attempting to convert input to an integer." in str(e)

    def test_set_valid_number_of_detail_rows(self):
        f = DataFile()
        f.number_of_detail_rows_is(1000)
        assert f.number_of_rows == 1000

    def test_append_header_row_no_data_file(self):
        f = DataFile()
        with pytest.raises(AssertionError) as e:
            f.append_header_row()
        assert "The data file has not been created. Use the 'Create Data File' keyword to create it." in str(e)

    def test_append_detail_rows_no_data_file(self):
        f = DataFile()
        with pytest.raises(AssertionError) as e:
            f.append_detail_rows()
        assert "The data file has not been created. Use the 'Create Data File' keyword to create it." in str(e)

    def test_append_detail_rows_no_detail_rows(self):
        f = DataFile()
        f._exists = True    # To simulate to the object that a file has been created
        with pytest.raises(AssertionError) as e:
            f.append_detail_rows()
        assert "The number of detail rows has not been defined. Use the `Number Of Detail Rows Is` keyword first." in str(e)


class TestDataRow:
    # Create a test field for each major type of data for testing.
    integer_field = DataField("integer", "INT_HEADER", min_length=3, max_length=20)
    boolean_field = DataField("Boolean", "BOOL_HEADER", options="Not Bool, Other Thing, True")
    string_field = DataField("STRING", "STRING_HEADER", min_length=10, max_length=50, characters="letters")
    options_field = DataField("string", "OPTIONS_HEADER", options="Not Bool, Other Thing, True")
    regexp_field = DataField("STRING", "REGEXP_HEADER", regexp="\\d{1,2}/\\d{1,2}/\\d{4}")
    test_fields = [integer_field, boolean_field, string_field, options_field, regexp_field]
    not_data_field = "Michael test"

    def test_add_data_field(self):
        row = DataRow()
        for field in self.test_fields:
            row.add_data_field(field)
        assert row.field_count == 5
        assert len(row.fields) == 5

    def test_add_not_data_field_fails(self):
        row = DataRow()
        with pytest.raises(AssertionError) as e:
            row.add_data_field(self.not_data_field)
        assert "Only objects of type SnowLibrary.keywords.file_creator.DataField can be added. Instead got: <class 'str'>" in str(e)

    def test_create_header_row(self):
        row = DataRow()
        for field in self.test_fields:
            row.add_data_field(field)
        header_row = row.create_header_row()
        for f in row.fields:
            assert f.header in header_row
        assert isinstance(header_row, list)

    def test_create_detail_row(self):
        row = DataRow()
        for field in self.test_fields:
            row.add_data_field(field)
        detail_row = row.create_detail_row()
        for f in row.fields:
            assert f.header not in detail_row
        assert isinstance(detail_row, list)

    def test_data_row_has_no_fields(self):
        """Don't create a row if no fields have been specified. Raise an AssertionError."""
        row = DataRow()
        with pytest.raises(AssertionError) as e:
            h = row.create_header_row()
        assert "No data fields have been added to the data row. Header row would be empty." in str(e)
        with pytest.raises(AssertionError) as e:
            h = row.create_detail_row()
        assert "No data fields have been added to the data row. Detail row would be empty." in str(e)


class TestDataField:
    def test_invalid_data_type(self):
        with pytest.raises(AssertionError) as e:
            f = DataField("test_no_data", "test_field_name")
        assert "Invalid data type specified.  Expected either integer, string, or boolean, but `test_no_data` was " \
               "provided." in str(e)

    def test_invalid_characters(self):
        with pytest.raises(AssertionError) as e:
            f = DataField("string", "test_field_name", characters="junk")
        assert "Invalid character type specified: `junk`." in str(e)

    def test_invalid_regexp(self):
        with pytest.raises(AssertionError) as e:
            f = DataField("string", "test_field_name", regexp="[]", characters="urlsafe")
        assert "Invalid regular expression syntax `[]`: " in str(e)

    def test_get_integer_data(self):
        integer_field = DataField("integer", "INT_HEADER", min_length=3, max_length=20)
        integer_data = integer_field.get_data()
        assert isinstance(int(integer_data), int)
        assert 3 <= len(integer_data) <= 20

    def test_get_boolean_data(self):
        boolean_field = DataField("boolean", "BOOL_HEADER", options="Not Bool, Other Thing, True")
        boolean_data = boolean_field.get_data()
        assert isinstance(boolean_data, str)
        assert boolean_data == "TRUE" or boolean_data == "FALSE"

    def test_get_string_data_no_characters(self):
        string_field = DataField("STRING", "STRING_HEADER")
        string_data = string_field.get_data()
        assert 1 <= len(string_data) <= 1000
        for char in string_data:
            assert char in string.printable

    def test_get_string_data_with_characters(self):
        string_field = DataField("STRING", "STRING_HEADER", min_length=10, max_length=50, characters="letters")
        string_data = string_field.get_data()
        assert 10 <= len(string_data) <= 50
        for char in string_data:
            assert char in string.ascii_letters

    def test_get_options_data(self):
        int_options_field = DataField("INTEGER", "OPTIONS_HEADER", options="1, 2, 3, 4, 5, 6, 7, 8, 9, 0",
                                      regexp="\\d{1,2}/\\d{1,2}/\\d{4}")
        int_options_data = int_options_field.get_data()
        assert int_options_data in string.digits
        assert isinstance(int(int_options_data), int)

        string_options_field = DataField("STRING", "OPTIONS_HEADER", options="1, 2, 3, 4, 5, 6, 7, 8, 9, 0",
                                         regexp="\\d{1,2}/\\d{1,2}/\\d{4}")
        string_options_data = string_options_field.get_data()
        assert string_options_data in string.digits
        assert isinstance(string_options_data, str)

    def test_get_regexp_data(self):
        regexp_field = DataField("STRING", "REGEXP_HEADER", regexp="\\d{1,2}/\\d{1,2}/\\d{4}")
        regexp_data = regexp_field.get_data()
        pattern = re.compile(regexp_field.regexp)
        match_object = re.match(pattern, regexp_data)
        try:
            match_object.group()
        except AttributeError:
            pytest.fail("Generated data did not match regular expression pattern: {}".format(regexp_data))

    def test_get_int_starts_with(self):
        int_field = DataField("INTEGER", "INT_HEADER", starts_with=3000, min_length=15, max_length=15)
        int_data = int_field.get_data()
        assert isinstance(int(int_data), int)
        assert len(int_data) == 15
        assert int_data[:4] == "3000"

    def test_get_str_starts_with(self):
        str_field = DataField("STRING", "STRING_HEADER", starts_with="Michael", min_length=10, max_length=12)
        str_data = str_field.get_data()
        assert isinstance(str_data, str)
        assert 10 <= len(str_data) <= 12
        assert str_data.index("Michael") == 0
