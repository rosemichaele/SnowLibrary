QA - Robot Framework -SnowLibrary
=================================

This project contains the keyword libraries for ServiceNow automated testing. The Python-based testing tool used
for this project is `Robot Framework <http://robotframework.org/>`_.

Prerequisites
_____________

- The Python package manager pip.exe must be installed and on the system PATH, along with Python 3.4 or greater.

Environment / User Variables
____________________________

Set the following environment or user variables on the machine used for testing:

    - AD_USER = Your (or any valid) ADMIN username
    - AD_PASS = Your (or any valid) ADMIN password
    - SNOW_TEST_URL = The host URL for your ServiceNow test instance (e.g. https://iceuat.service-now.com for UAT)
    - SNOW_PROD_URL = The host URL for your ServiceNow production instance (e.g. https://ice.service-now.com for ICE)
    - SNOW_LIB_DIR = The path to this project's root on your machine (e.g. C:\\Users\\mrose\\ws\\robotframework\\SnowRF)
    - SNOW_REST_USER = A user with permission to make REST calls to ServiceNow
    - SNOW_REST_PASS = The password for that user
    - SNOW_SIDE_DOOR_USER = The side door user name of an ADMIN user
    - SNOW_SIDE_DOOR_PWD = The side door password of that user

Installation
____________

Clone or copy this repository into a new empty directory. Run the below command in that directory. Best practice is
to use virtual environments to isolate Python packages for development. This also helps avoid permissions issues  in
the default Python installation locations on standard ICE machines.  Learn more about Python venv `here <https://docs.python.org/3/tutorial/venv.html>`_.::

    > pip install .


Running Keyword Library Acceptance Tests
________________________________________

From the project's root directory, run the following command to execute all of the automated ServiceNow acceptance tests::

    > robot --outputdir atest\output\ atest\acceptance


Running Unit and Acceptance Tests
_________________________________

From the project's root directory, run the following command to run Python unit tests::

    > pytest -v utest\
