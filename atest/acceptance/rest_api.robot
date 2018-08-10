*** Settings ***
Documentation    Acceptance tests for SNOW REST API keywords
Library          SnowLibrary.RESTQuery

*** Test Cases ***
Test All REST Query Conditions
    [Tags]  rest    query   parameters
    Query Table Is  ticket
    Required Query Parameter Is     contact_type        EQUALS  Service Catalog
    Add Query Parameter     AND     state               EQUALS  7
    Add Query Parameter     AND     approval            CONTAINS    Yet
    Add Query Parameter     AND     description         STARTS WITH     Req
    Add Query Parameter     AND     description         ENDS WITH       .
    Add Query Parameter     AND     sys_mod_count       LeSs THaN       500
    Add Query Parameter     AND     sys_mod_count       greater than    1
    Add Query Parameter     AND     reassignment_count  BETWEEN     -1   100
    Add Query Parameter     AND     number              DOES NOT CONTAIN    TKT555
    Add Query Parameter     AND     u_task_categorization    IS EMPTY
    Execute Query
    ${contact_type}=    Get Individual Response Field    contact_type
    ${state}=      Get Individual Response Field    state
    ${approval}=      Get Individual Response Field    approval
    ${number}=      Get Individual Response Field    number
    ${description}=      Get Individual Response Field    description
    ${sys_mod_count}=      Get Individual Response Field    sys_mod_count
    ${reassignment_count}=      Get Individual Response Field    sys_mod_count
    ${u_task_categorization}=      Get Individual Response Field    u_task_categorization
    Should Be Equal As Strings     ${contact_type}    Service Catalog
    Should Be Equal As Strings     ${state}    7
    Should Not Contain     ${number}    TKT555
    Should Contain         ${approval}     Yet
    Should Start With      ${description}   Req
    Should End With      ${description}   .
    Should Be True      ${sys_mod_count} < 500
    Should Be True      ${sys_mod_count} > 1
    Should Be True      ${reassignment_count} <= 101
    Should Be True      ${reassignment_count} >= -1
    Should Be Empty     ${u_task_categorization}

Test Get Records Created In Date Range
    [Tags]  rest    query   dates
    Query Table Is  proc_po
    ${start_time}=             Set Variable    2018-06-01 00:00:01                # The date can be provided directly if desired.
    ${end_time}=               Get Time                                            # Returns YYYY-MM-DD hh:mm:ss
    ${actual_num}=             Get Records Created In Date Range  ${start_time}    ${end_time}
    Should Be True             ${actual_num} > 0

Test Get Records Created In Date Range Validates Input
    [Tags]  rest    query   dates
    Query Table Is  proc_po
    ${start_time}=      Set Variable     michael String
    ${end_time}=               Get Time                                            # Returns YYYY-MM-DD hh:mm:ss
    ${msg}=                    Run Keyword And Expect Error     *   Get Records Created In Date Range       ${start_time}    ${end_time}
    Should Contain             ${msg}   Input date arguments were not provided in the correct format
    ${msg}=                    Run Keyword And Expect Error     *   Get Records Created In Date Range       ${end_time}    ${start_time}
    Should Contain             ${msg}   Input date arguments were not provided in the correct format

Test Get Records Created In Date Range Requires Query Table
    [Tags]  rest    query   dates
    ${start_time}=             Get Time         2018-06-01 00:00:01                # The date can be provided directly if desired.
    ${end_time}=               Get Time                                            # Returns YYYY-MM-DD hh:mm:ss
    ${msg}=                    Run Keyword And Expect Error     *   Get Records Created In Date Range  ${start_time}    ${end_time}
    Should Contain             ${msg}   Query table must already be specified in this test case, but is not.

Test Get Records Created Before
    [Tags]  rest    query   dates
    Query Table Is  proc_po
    ${time}=                   Set Variable     2016-06-07 00:00:01
    ${actual_num}=             Get Records Created Before  ${time}
    Should Be True             ${actual_num} > 0

Test Get Records Created After
    [Tags]  rest    query   dates
    Query Table Is  proc_po
    ${time}=                   Set Variable     2018-06-01 00:00:01
    ${actual_num}=             Get Records Created After  ${time}
    Should Be True             ${actual_num} > 0
