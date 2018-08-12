import os
import re
import random
import csv

import rstr
from robot.libraries.OperatingSystem import OperatingSystem
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from robot.api.deco import keyword


class DataFile:
    """
    This library implements keywords for creating test data files for integration testing in ServiceNow. Keywords can be
    used in your test suite by importing SnowLibrary.DataFile as a Library. This is an example of the usage to create
    a test import file for the Oracle Cloud Requisitions Integration:
    
    *Generate Requisitions Import File*
    *[Arguments]*  ``${absolute_file_name}`` 
    | Define File Name | ${absolute_file_name} | 
    | Define Delimiter | COMMA | 
    | Define Field | header=SUPPLIER_ID         | min_length=15       |  max_length=15  |  data_type=integer | starts_with=3000  | 
    | Define Field | header=SUPPLIER_NUMBER     | min_length=3        |  max_length=40  |  data_type=string  | characters=digits |
    | Define Field | header=SUPPLIER_NAME       | min_length=3        |  max_length=100 |  data_type=string  | 
    | Define Field | header=SUPPLIER_SITE_CODE  | data_type=string    |  regexp=[A-Z]{3}_\\d{4}_\\d          | 
    | Define Field | header=REQ_STATUS          | data_type=string    |  options=APPROVED, REJECTED, INCOMPLETE, RETURNED, PENDING APPROVAL, CANCELED, IN PROCESS, PRE-APPROVED, WITHDRAWN   | 
    | Define Field | header=CAPEX_PROJECT       | required=False |  min_length=3 | max_length=100  | data_type=string |
    | Number Of Detail Rows Is | 1000 | 
    | Create Data File | 
    | Append Header Row |  # This is not required  if you do not want a header row in your file. |
    | Append Details Rows | 
    """
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    VALID_DELIMITERS = {"COMMA": ",", "PIPE": "|", "TAB": "\t", "COLON": ":", "SEMICOLON": ";"}

    def __init__(self, name=None):
        """
        Initialize the data file instance. The default delimter is set to comma on instantiation.  This cna be changed using the
        `Define Delimiter` keyword.
        :param name:   Optionally provide the *absolute* name of the file.
        """
        self.absolute_name = name
        self.delimiter = ","
        self.row_definition = DataRow()
        self.number_of_rows = 0
        self._exists = False

    def _append(self, data):
        """Private method to write to the data file."""
        with open(self.absolute_name, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=self.delimiter, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data)
            logger.info("Writing data to file: {}".format(data))

    @keyword
    def define_file_name(self, name):
        """Define the absolute name of the file, which includes the full path to its location on the machine
         running this test. The file will not be created until the `Create Data File` keyword is used.
         """
        if not os.path.isabs(name):
            raise AssertionError("The file name must be absolute. It should begin with a slash (/) character or a drive"
                                 "specification, such as C:\.")
        else:
            self.absolute_name = name

    @keyword
    def define_data_field(self, data_type, header, **kwargs):
        """Define a data field which will be included in this file.  Required arguments are the type of data, which can
        be integer, string, or boolean. Optional keyword arguments include:
        
        - ``required``:  Specify whether or not the field must always include data. True by default. Currently, does nothing with False.
        - ``min_length``: The minimum length of the data in this field. Defaults to 1 and only used if `options` is not provided.
        - ``max_length``: The maximum length of the data in this field. Defaults to 1000 and only used if `options` is not provided.
        - ``options``: A comma-separated string of options for the values in this field, one of which will be used at random to populate the field in each row of data.
        - ``regexp``:  Specify a regular expression string with which to generate data for this field.
        - ``starts_with``:  Specify a string of characters that the data field should always begin with.  This is useful 
        record numbers in ServiceNow. For example, TKT5554821 starts with TKT. If provided, any regex passed in will be ignored.
        - ``characters``: Indicate if the data field can only contains characters from a specific subtype.  Valid subtypes 
        are letters, uppercase, lowercase, digits, printable, punctuation, nonwhitespace, nondigits, nonletters, 
        normal, postalsafe, urlsafe, domainsafe. CREDIT - `rstr module<https://pypi.org/project/rstr/ >`_.
        """
        f = DataField(data_type, header, **kwargs)
        self.row_definition.add_data_field(f)

    @keyword
    def define_delimiter(self, delimiter):
        """Define the delimiter that should be used when creating the file.  If unspecified, this will be defaulted to
        COMMA.  The keyword expects the string name of the delimiter, so valid values are COMMA, PIPE, TAB, COLON, 
        or SEMICOLON (case-insensitive). This is converted to the proper character when writing to the file."""
        if delimiter.upper() not in self.VALID_DELIMITERS:
            raise AssertionError("Invalid delimiter.  Delimiter must be COMMA, PIPE, TAB, COLON, or SEMICOLON.")
        else:
            self.delimiter = self.VALID_DELIMITERS[delimiter.upper()]

    @keyword
    def create_data_file(self):
        """Create a file with the given name.  The file name must be defined first using `Define File Name` keyword. 
        This keyword leverages the Robot Framework OperatingSystem library keyword `Create File`, so if the directory
        for the file does not exist, it is created, along with missing intermediate directories."""
        if self.absolute_name is None:
            raise AssertionError("The file name has not been defined.  Define it using the 'Define File Name' keyword")
        else:
            operating_sys = OperatingSystem()
            try:
                operating_sys.create_file(self.absolute_name)
                self._exists = True
            except PermissionError as e:
                logger.error(e.strerror)
                raise

    @keyword
    def number_of_detail_rows_is(self, rows):
        """Define the number of details rows that should be added to the file.  This should be a positive integer."""
        try:
            int_rows = int(rows)
        except ValueError:
            raise AssertionError("Failed attempting to convert input to an integer.")
        if int_rows < 0:
            raise AssertionError("Number of details rows must be a positive integer.")
        else:
            self.number_of_rows = int(rows)

    @keyword
    def append_header_row(self):
        """Append the header row to an already existing data file.  If the file has not yet been created, an error will
        be raised.  Use the `Create Data File` keyword first to avoid this."""
        if not self._exists:
            raise AssertionError("The data file has not been created. Use the 'Create Data File' keyword to create it.")
        else:
            headers = self.row_definition.create_header_row()
            self._append(headers)

    @keyword
    def append_detail_rows(self):
        """Append ALL required detail rows to an already existing data file.  If the file has not yet been created or
        the number of details rows has not been specified, an error will be raised.  Use the `Create Data File` and 
        `Number Of Detail Rows Is` keywords first to avoid this."""
        if not self._exists:
            raise AssertionError("The data file has not been created. Use the 'Create Data File' keyword to create it.")
        elif self.number_of_rows == 0:
            raise AssertionError("The number of detail rows has not been defined. Use the `Number Of Detail Rows Is` keyword first.")
        else:
            for i in range(self.number_of_rows):
                detail_row = self.row_definition.create_detail_row()
                self._append(detail_row)

    @keyword
    def remove_data_file(self):
        """Remove a file with the given name.  The file name must be defined first using `Define File Name` keyword. 
        This keyword leverages the Robot Framework OperatingSystem library keyword `Remove File`. If the file does not
        exist, nothing will happen."""
        if self.absolute_name is None:
            raise AssertionError("The file name has not been defined.  Define it using the 'Define File Name' keyword")
        else:
            operating_sys = OperatingSystem()
            try:
                operating_sys.remove_file(self.absolute_name)
                self._exists = False
            except PermissionError as e:
                logger.error(e.strerror)
                raise

    @keyword
    def file_should_contain_rows(self, expected_rows):
        """Compares the number of lines in the data file to ``expected_rows`` and fails if they are not equal as
        integers. The file name must be defined first using `Define File Name` keyword."""
        if self.absolute_name is None:
            raise AssertionError("The file name has not been defined.  Define it using the 'Define File Name' keyword")
        else:
            with open(self.absolute_name, 'r') as f:
                actual_rows = len(f.readlines())
        bi = BuiltIn()
        if actual_rows != bi.convert_to_integer(expected_rows):
            bi.fail("Expected file to contain {e} rows, but found {a} rows instead.".format(e=expected_rows, a=actual_rows))
        else:
            logger.info("Actual number of rows in file matches the expected number of rows.")


class DataRow:
    """This class acts as a bucket to manage all of the fields in a data file. Fields can be can be added to the data
     row definition, and header / details rows can be generated according to the current definition."""

    def __init__(self):
        self.field_count = 0
        self.fields = list()
        self._has_fields = False

    def add_data_field(self, data_field):
        """Add `data_field` to the list of fields in the row. Increment the field count and adjust the private 
        _has_fields indicator if necessary.
        """
        assert isinstance(data_field, DataField), "Only objects of type SnowLibrary.keywords.file_creator.DataField can be added. Instead got: {}".format(type(data_field))
        self.fields.append(data_field)
        self.field_count += 1
        if not self._has_fields:
            self._has_fields = True

    def create_header_row(self):
        """Returns the header row of a file with the fields in this data row, in list form."""
        if not self._has_fields:
            raise AssertionError("No data fields have been added to the data row. Header row would be empty.")
        else:
            header_list = [f.header for f in self.fields]
            return header_list

    def create_detail_row(self):
        """Returns a detail row of a file with the fields in this data row, in list form."""
        if not self._has_fields:
            raise AssertionError("No data fields have been added to the data row. Detail row would be empty.")
        else:
            detail_list = [f.get_data() for f in self.fields]
            return detail_list


class DataField:
    """Files are made up of rows of data, which are made up of data fields.  This class is used to track attributes of data fields,
    so that they can be quickly created and written to a data row, which will then be written to the file.
    """

    VALID_DATA_TYPES = ["INTEGER", "STRING", "BOOLEAN"]
    CHARACTER_TYPES = {"LETTERS": rstr.letters, "UPPERCASE": rstr.uppercase, "PRINTABLE": rstr.printable,
                       "PUNCTUATION": rstr.punctuation,
                       "NONWHITESPACE": rstr.nonwhitespace, "LOWERCASE": rstr.lowercase, "DIGITS": rstr.digits,
                       "NONDIGITS": rstr.nondigits,
                       "NONLETTERS": rstr.nonletters, "NORMAL": rstr.normal, "POSTALSAFE": rstr.postalsafe,
                       "URLSAFE": rstr.urlsafe,
                       "DOMAINSAFE": rstr.domainsafe
                       }

    def __init__(self, data_type, header, required=True, min_length=1, max_length=1000, options=None, regexp=None,
                 starts_with=None, characters=None):
        """
        Initialize the data field instance.
        :param data_type:  The type of data that will be contained in the field, e.g. integer, string, boolean.
        :param header:  The content of the header row that for the column that contains this data field.
        :param required:  Specify whether or not the field must always include data. True by default. Currently, does nothing with False.
        :param min_length: The minimum length of the data in this field. Defaults to 1 and only used if `options` is not provided.
        :param max_length: The maximum length of the data in this field. Defaults to 1000 and only used if `options` is not provided.
        :param options: A comma-separated string of options for the values in this field, one of which will be used at random to populate the field in each row of data.
        :param regexp:  Specify a regular expression string with which to generate data for this field.
        :param starts_with:  Specify a string of characters that the data field should always begin with.  This is useful 
               record numbers in ServiceNow. For example, TKT5554821 starts with TKT. If provided, any regex passed in will be ignored.
        :param characters: Indicate if the data field can only contains characters from a specific subtype.  Valid subtypes 
               are letters, uppercase, lowercase, digits, printable, punctuation, nonwhitespace, nondigits, nonletters, 
               normal, postalsafe, urlsafe, domainsafe. CREDIT - `rstr module<https://pypi.org/project/rstr/ >`_.
        """
        self.data_type = data_type
        self.header = header
        self.required = required
        self.min_length = int(min_length)
        self.max_length = int(max_length)
        if options is not None:
            self.options = [option.strip() for option in options.split(",")]
        else:
            self.options = options
        self.regexp = regexp
        if starts_with is not None:
            starts_with_length = len(str(starts_with))
            self.min_length -= starts_with_length
            self.max_length -= starts_with_length
            self.starts_with = str(starts_with)
        else:
            self.starts_with = starts_with
        if characters is None and data_type.upper() == "STRING":
            self.characters = "POSTALSAFE" # If string data type, and no character group was chosen, default to postal safe characters.
        elif data_type.upper() == "INTEGER":
            self.characters = "DIGITS"  # If integer data type, choose digits character set.
        elif data_type.upper() == "BOOLEAN":
            self.options = ["TRUE", "FALSE"]   # If boolean data type, set options to TRUE and FALSE
            self.characters = characters
        else:
            self.characters = characters   # Otherwise, use the specified characters set.
        self._validate()

    def _validate(self):
        """Validate the defined instance attributes."""
        self._validate_data_type()
        self._validate_characters()
        self._validate_regexp()
        logger.debug("Instance attributes passed validation.")

    def _validate_characters(self):
        """Ensures that the input `characters` is one of CHARACTER_TYPES."""
        if self.characters is not None:
            if self.characters.upper() not in self.CHARACTER_TYPES:
                raise AssertionError("Invalid character type specified: `{}`.".format(self.characters))
            else:
                logger.debug("Valid character type provided on instantiation.")
        else:
            logger.debug("No character type provided on instantiation.")

    def _validate_data_type(self):
        """Ensures that the input `data_type` is one of VALID_DATA_TYPES."""
        if self.data_type.upper() not in self.VALID_DATA_TYPES:
            raise AssertionError(
                "Invalid data type specified.  Expected either integer, string, or boolean, but `{}` was provided.".format(
                    self.data_type))
        else:
            logger.debug("Valid data type provided on instantiation.")

    def _validate_regexp(self):
        """Leverages Python's re module to validate the regular expression string `regexp`."""
        if self.regexp is not None:
            try:
                re.compile(self.regexp)
                logger.debug("Valid regular expression provided on instantiation.")
            except re.error as e:
                raise AssertionError("Invalid regular expression syntax `{regexp}`: {error}".format(regexp=self.regexp, error=e.msg))
        else:
            logger.debug("No regular expression provided on instantiation.")

    def get_data(self):
        """Generate and return data that fits the attributes of this field."""
        # If options are provided for this field, choose one of them, other things aren't relevant.
        if self.options is not None:
            data = random.choice(self.options)
        # If starts_with is provided, make a string that starts with this attribute. Update min_length and max_length accordingly.
        elif self.starts_with is not None:
            data = self.starts_with + self.CHARACTER_TYPES[self.characters.upper()](self.min_length, self.max_length)
        # If regexp is provided, return a string matching the expression.
        elif self.regexp is not None:
            return rstr.xeger(self.regexp)
        # Otherwise, get a string between min_length and max_length using the given character type.
        else:
            data = self.CHARACTER_TYPES[self.characters.upper()](self.min_length, self.max_length)
        return data
