from robot.api.deco import keyword

class NotificationHelper:
    """
    This library implements keywords for checking SMS and Email notification format in ServiceNow. Keywords can be
    used in your test suite by importing SnowLibrary.NotificationHelper as a Library. 
    *Expected OIR Notification Format*
    *SMS*
    [OIR number with digit only]|[severity]|[business]|[state]|...
    *Email"
    [OIR number] [severity] [business] [state] [application]|...
    """

    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    @keyword
    def get_expected_notification_message(self, number, state, business, application, severity, description, type, work_note=None):
        """
        Used to get the beginning part of expected message format.
        :param number: The transformed OIR number.
        :param state: The transformed state.
        :param business: The business OIR is related to.
        :param application: The application OIR is related to.
        :param severity: The transformed severity.
        :param description: The oir description.
        :param type: The message type: email or sms.
        :return: The expected message format. 
        """
        # Transform the number to expected format
        if (len(number) != 10):
            raise AssertionError("Please enter the correct number, which is expected to have 10 digits.")
        else:
            self.sms_number = number[3:]
        #Transform the severity to expected format
        if (severity == "5"):
            self.sev = "SEV5"
        elif (severity == "4"):
            self.sev = "SEV4"
        elif (severity == "3"):
            self.sev = "SEV3"
        elif (severity == "2"):
            self.sev = "SEV2"
        elif (severity == "1"):
            self.sev = "SEV1"
        else:
            raise AssertionError("Please enter the correct severity, which is the number from 1~5.")
        #Transform the state to expected format
        if (state == "Work in Progress"):
            self.stat = "WIP"
        elif (state == "Root Cause Pending"):
            self.stat = "RCP"
        else:
            raise AssertionError("Please enter the correct state, which is Work in Progress or Root Cause Pending.")
        #Get the expected message format
        if(work_note==None):
            if(type=="sms"):
                return self.sms_number + "|" + self.sev + "|" + business + "|" + self.stat + "|" + description
            elif(type=="email"):
                return number + " " + self.sev + " " + business + " " + self.stat + " " + application + " | " + description
            else:
                raise AssertionError("Please enter the correct type, which is sms or email.")
        else:
            if (type == "sms"):
                return self.sms_number + "|" + self.sev + "|" + business + "|" + self.stat + "|" + work_note
            elif (type == "email"):
                return number + " " + self.sev + " " + business + " " + self.stat + " " + application + " | " + work_note
            else:
                raise AssertionError("Please enter the correct type, which is sms or email.")

    @keyword
    def get_user_phone_number(self,info):
        """
        Used to get user's phone number. 
        :param info: The info get from Notification Preferences page.
        :return: User's telephone number.
        """
        number = info.split(" ")
        return number[1]

