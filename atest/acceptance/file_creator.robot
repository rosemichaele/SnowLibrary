*** Settings ***
Documentation    Acceptance tests for SnowLibrary.DataFile keywords
Library          SnowLibrary.DataFile
Library          OperatingSystem

*** Variables ***
${TEST_FILE_PATH}   %{SNOW_LIB_DIR}\\atest\\acceptance\\output\\reqs_1000.csv

*** Test Cases ***
Req File Should Be Created With 1000 Rows
    Generate Requisitions Import File   ${TEST_FILE_PATH}
    File Should Exist   ${TEST_FILE_PATH}
    File Should Contain Rows   1001
    Remove Data File
    File Should Not Exist   ${TEST_FILE_PATH}

*** Keywords ***
Generate Requisitions Import File 
    [Arguments]  ${absolute_file_name}
     Define File Name  ${absolute_file_name}  
     Define Delimiter  COMMA  
     Define Data Field  header=SUPPLIER_ID          min_length=15         max_length=15    data_type=integer  starts_with=3000
     Define Data Field  header=SUPPLIER_NUMBER      min_length=3          max_length=40    data_type=string   characters=digits
     Define Data Field  header=SUPPLIER_NAME        min_length=3          max_length=100   data_type=string
     Define Data Field  header=SUPPLIER_SITE_CODE   data_type=string      regexp=[A-Z]{3}_\\d{4}_\\d
     Define Data Field  header=REQ_STATUS           data_type=string      options=APPROVED, REJECTED, INCOMPLETE, RETURNED, PENDING APPROVAL, CANCELED, IN PROCESS, PRE-APPROVED, WITHDRAWN
     Define Data Field  header=CAPEX_PROJECT        required=False   min_length=3  max_length=5   data_type=string     characters=uppercase
     Number Of Detail Rows Is  1000
     Create Data File  
     Append Header Row   # This is not required  if you do not want a header row in your file. 
     Append Detail Rows