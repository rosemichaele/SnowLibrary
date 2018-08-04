*** Settings ***
Documentation    Acceptance tests for SnowLibrary.DataFile keywords
Library          SnowLibrary.DataFile
Library          OperatingSystem

*** Variables ***
${REQ_TEST_FILE_PATH}   %{SNOW_LIB_DIR}/atest/acceptance/output/reqs_1000.csv
${PO_TEST_FILE_PATH}   %{SNOW_LIB_DIR}/atest/acceptance/output/pos_5000.csv

*** Test Cases ***
Req File Should Be Created With 1000 Rows
    Generate Requisitions Import File   ${REQ_TEST_FILE_PATH}
    File Should Exist   ${REQ_TEST_FILE_PATH}
    File Should Contain Rows   1001
    Remove Data File
    File Should Not Exist   ${REQ_TEST_FILE_PATH}

PO File Should Be Created With 5000 Rows
    Generate PO Import File   ${PO_TEST_FILE_PATH}
    File Should Exist   ${PO_TEST_FILE_PATH}
    File Should Contain Rows   5001
    Remove Data File
    File Should Not Exist   ${PO_TEST_FILE_PATH}

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

Generate PO Import File
    [Arguments]  ${absolute_file_name}
     Define File Name   ${absolute_file_name}
     Define Delimiter   COMMA
     Define Data Field  header=PO_HEADER_ID             min_length=1         max_length=15    data_type=integer
     Define Data Field  header=PO_LINE_ID               min_length=2         max_length=15    data_type=integer
     Define Data Field  header=PO_LINE_LOCATIOn_ID      min_length=2         max_length=15    data_type=integer
     Define Data Field  header=PO_DISTRIBUTION_ID       min_length=2         max_length=15    data_type=integer
     Define Data Field  header=SOLD_TO_LE_ID            data_type=integer    min_length=15    max_length=15
     Define Data Field  header=TO_ORG_ID                data_type=integer    min_length=15    max_length=15
     Define Data Field  header=BU_ID                    data_type=integer    min_length=15    max_length=15
     Define Data Field  header=REQUESTOR_ID             data_type=integer    min_length=15    max_length=15
     Define Data Field  header=SHIP_TO_ORG_ID           data_type=integer    min_length=15    max_length=15
     Define Data Field  header=SUPPLIER_ID              data_type=integer    min_length=15    max_length=15
     Define Data Field  header=SUPPLIER_SITE_ID         data_type=integer    min_length=15    max_length=15
     Define Data Field  header=SUPPLIER_NUMBER          data_type=integer    min_length=4     max_length=5
     Define Data Field  header=SUPPLIER_NAME            data_type=string     min_length=10    max_length=50
     Define Data Field  header=SUPPLIER_SITE_CODE       data_type=string     regexp=[A-Z]{3}_\\d{4}_\\d
     Define Data Field  header=LEGAL_ENTITY_IDENTIFIER  data_type=integer    min_length=5     max_length=5
     Define Data Field  header=INVENTORY_ORG_CODE       data_type=integer    min_length=5     max_length=5
     Define Data Field  header=PO_NUMBER                data_type=string     regexp=\\d{5}-\\d{5,10}
     Define Data Field  header=PO_LINE_NBR              data_type=integer    min_length=1     max_length=3
     Define Data Field  header=REQUESTOR                data_type=string     regexp=[A-Z]{3,40},[A-Z]{3,20}
     Define Data Field  header=REQUESTOR_EMPL_NUMBER    data_type=integer    min_length=4     max_length=5
     Define Data Field  header=BUYER                    data_type=string     regexp=[A-Z]{3,40},[A-Z]{3,20}
     Define Data Field  header=BUYER_EMPL_NUMBER        data_type=integer    min_length=4     max_length=5
     Define Data Field  header=PO_QTY                   data_type=integer    min_length=1     max_length=4
     Define Data Field  header=UNIT_OF_MEASURE          data_type=string     options=Each
     Define Data Field  header=CURRENCY_CD              data_type=string     min_length=2     max_length=3      characters=uppercase
     Define Data Field  header=MERCHANDISE_AMT          data_type=string     regexp=\\d{2,6}.\\d{1,2}
     Define Data Field  header=CHNG_ORD_SEQ             data_type=string     options=${EMPTY},1
     Define Data Field  header=PO_DATE                  data_type=string     regexp=\\d{1,2}/\\d{1,2}/\\d{4}
     Define Data Field  header=DATETIME_DISP            data_type=string     regexp=\\d{4}-\\d{2}-\\d{2}[T]\\d{2}:\\d{2}:\\d{2}\\.000000
     Define Data Field  header=PO_LINE_DESCRIPTION      data_type=string     min_length=20     max_length=500   characters=normal
     Define Data Field  header=LAST_UPDATE_DTTM         data_type=string     regexp=\\d{4}-\\d{2}-\\d{2}[T]\\d{2}:\\d{2}:\\d{2}\\.000000
     Define Data Field  header=PO_STATUS                data_type=string     options=CLOSED FOR RECEIVING, OPEN, INCOMPLETE, CANCELED, CLOSED
     Define Data Field  header=PO_DISTRIBUTION_NBR      data_type=integer    min_length=1     max_length=1
     Define Data Field  header=REQ_NUMBER               required=False       data_type=string     regexp=[A-Z]{3}_\\d{4}_\\d
     Define Data Field  header=REQ_LINE_NUMBER          data_type=integer    min_length=1     max_length=3
     Define Data Field  header=SHIP_TO_LOCATION         data_type=string     min_length=2     max_length=10      characters=uppercase
     Number Of Detail Rows Is  5000
     Create Data File
     Append Header Row   # This is not required  if you do not want a header row in your file.
     Append Detail Rows