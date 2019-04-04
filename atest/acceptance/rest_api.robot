*** Settings ***
Documentation    Acceptance tests for SNOW REST API keywords
Library          SnowLibrary.RESTQuery
Library          SnowLibrary.RESTInsert
Library          Collections

*** Test Cases ***
Test REST Query Conditions
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

Test REST Query Date Conditions
    [Tags]  rest    query   dates
    Query Table Is  proc_po
    Required Query Parameter Is  sys_created_on     BETWEEN      2018-08-01 00:00:00    2018-08-15 23:59:59     is_date_field=True
    Execute Query
    ${num_records}=                 Get Response Record Count
    Should Be Equal As Integers     ${num_records}  1
    ${short_description}=   Get Individual Response Field   short_description
    Should Not Be Empty     ${short_description}


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

Test Insert Record validate table
    [Tags]  rest    insert  table
    ${msg}=                    Run Keyword And Expect Error    *   Insert Table Is                  tickt
    Should Contain             ${msg}   Insert table not found, please check the table name

Test Insert Record Parameters Requires Insert Table
    [Tags]  rest    insert   table
    ${values}=                 create dictionary            short description       this is a test
    ${msg}=                    Run Keyword And Expect Error    *   Insert Record Parameters     ${values}
    Should Contain             ${msg}   Insert table must already be specified in this test case, but is not

Test Insert Record Parameters validate field
    [Tags]  rest    insert  table
    Insert Table Is                  change_request
    ${values}=                 create dictionary            short_description       this is a test          u_business     ICE Inc.            Catgory       Software
    ${msg}=                    Run Keyword And Expect Error    *   Insert Record Parameters     ${values}
    Should Contain             ${msg}   Field not found in response from change_request: Catgory

Test Insert Record
    [Tags]  rest    insert  record
    Insert Table Is                  u_customer_contact_rest
    ${values}=                 create dictionary            u_assignment_group      **ICE Link Account Management      u_caller      John O'Rourke      u_caller_email     john.orourke1234@citimax.com
    ...                                                     u_caller_phone        1-888-555-5555        u_company      Citigroup Global Markets Limited To The Max      u_company_address       1 Park Ave
    ...                                                     u_company_city        New York      u_company_country      USA      u_company_state     NY      u_customer_urgency      Medium
    ...                                                     u_description         This is the detailed description     u_do_not_email    true       u_environment     Prod      u_issue_type    Request
    ...                                                     u_send_from           icelinkhelp@theice.com           u_business       ICE Link        u_service         ICELink - Multiple        u_task_categorization       API
    ...                                                     u_short_description     Short Description for Customer Contact      u_template      ICE NUEF Customer Request       u_watch_list    karen.johnson@theice.com,yuting.wang@theice.com
    Insert Record Parameters        ${values}
    ${Sys_id}=             Insert Record
    Should Not Be Empty     ${Sys_id}

Test REST Query Can Return Multiple Records
    [Tags]  rest    multiple
    Query Table Is                  cmdb_ci_zone
    Required Query Parameter Is     operational_status  EQUALS  1   # Operational
    Add Query Parameter             AND     location.type   CONTAINS    Datacenter Zone     # Example query parameters that should contain multiple results
    Execute Query                   multiple=${TRUE}   # Optional flag, default is False
    ${num_records}=                 Get Response Record Count
    Should Be True                  ${num_records} > 1

Test Robot Error For Get Response Record Count When Query Not Yet Executed
    [Tags]  rest    multiple
    Run Keyword And Expect Error    QueryNotExecuted: No query has been executed. Use the Execute Query keyword to retrieve records.      Get Response Record Count

Test Get Record Details From Response When Multiple Is True
    [Tags]  rest    multiple
    Query Table Is                  cmdb_ci_zone
    Required Query Parameter Is     operational_status  EQUALS  1
    Add Query Parameter             AND     location.type   CONTAINS    Datacenter Zone     # Example query parameters that should contain multiple results
    Include Fields In Response      location.name   sys_created_by
    Execute Query                   multiple=${TRUE}
    @{location_names}=              Get Response Field Values   location.name
    @{location_creators}=           Get Response Field Values   sys_created_by
    ${loc_names_length}=            Get Length      ${location_names}
    ${loc_creators_length}=         Get Length      ${location_creators}
    Should Be True                  ${loc_names_length} > 1
    Should Be Equal                 ${loc_creators_length}      ${loc_names_length}

Test Sort Multiple Query Results By Created Date (Ascending)
    [Tags]  rest    multiple
    Query Table Is                  cmdb_ci_zone
    Required Query Parameter Is     operational_status  EQUALS  1
    Add Query Parameter             AND     location.type   CONTAINS    Datacenter Zone     # Example query parameters that should contain multiple results
    Add Sort                        sys_created_on
    Include Fields In Response      sys_created_on      sys_updated_on
    Execute Query                   multiple=${TRUE}
    @{created_dates}=               Get Response Field Values   sys_created_on
    @{list_copy}=                   Copy List   ${created_dates}
    Sort List                       ${created_dates}
    Lists Should Be Equal           ${created_dates}    ${list_copy}

Test Sort Multiple Query Results By Created Date (Descending)
    [Tags]  rest    multiple
    Query Table Is                  cmdb_ci_zone
    Required Query Parameter Is     operational_status  EQUALS  1
    Add Query Parameter             AND     location.type   CONTAINS    Datacenter Zone     # Example query parameters that should contain multiple results
    Add Sort                        sys_created_on  ascending=${FALSE}
    Include Fields In Response      sys_created_on      sys_updated_on
    Execute Query                   multiple=True
    @{created_dates}=               Get Response Field Values   sys_created_on
    @{list_copy}=                   Copy List   ${created_dates}
    Sort List                       ${created_dates}
    Run Keyword And Expect Error    Lists are different:*     Lists Should Be Equal     ${created_dates}    ${list_copy}
