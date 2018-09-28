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

    def _oir_number_transform(self,number):
        """
        Used to transfer number to expected format.
        :param number: The OIR record number.
        :return: The number only with digits. 
        """
        if (len(number) != 10):
            raise AssertionError("Please enter the correct number, which is expected to have 10 digits.")
        else:
            self.expected_number = number[3:]
        return self.expected_number

    def _oir_severity_transform(self,severity):
        """
        Used to transfer severity to expected format.
        :param severity: The OIR record severity.
        :return: The expected format to present severity in notification message.
        """
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
        return self.sev

    def _oir_state_transform(self,state):
        """
        Used to transfer state to expected format.
        :param state: The OIR record state.
        :return: The expected format to present state in notification message.
        """
        if (state == "Work in Progress"):
            self.stat = "WIP"
        elif (state == "Root Cause Pending"):
            self.stat = "RCP"
        else:
            raise AssertionError("Please enter the correct state, which is Work in Progress or Root Cause Pending.")
        return self.stat

    def _active_bridge_number_transform(self,domestic,access_code,pin_code):
        """
        Used to transfer active bridge number to expected format.
        :param domestic: Domestic number of reserved bridge.
        :param access_code: Access code of reserved bridge.
        :param pin_code: Pin code of reserved bridge.
        :return: The expected format to present bridge info in notification message.
        """
        if((domestic==None) or (access_code==None) or (pin_code==None)):
            raise AssertionError("Please enter domestic number, access code and pin code")
        else:
            self.bridge_number=domestic + ",,"+access_code+"#,,"+pin_code+"#"
        return self.bridge_number

    @keyword
    def get_expected_notification_message(self, number, state, business, application, severity, description, type, work_note=None):
        """
        Used to get the expected automatic notification message format.
        :param number: The transformed OIR number.
        :param state: The transformed state.
        :param business: The business OIR is related to.
        :param application: The application OIR is related to.
        :param severity: The transformed severity.
        :param description: The oir description.
        :param type: The message type: email or sms.
        :return: The expected message format. 
        """
        self.sms_number=self._oir_number_transform(number)
        self.stat=self._oir_state_transform(state)
        self.sev=self._oir_severity_transform(severity)

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
        self.number = info.split(" ")
        return self.number[1]

    @keyword
    def get_expected_send_notification_message(self,number,state,severity,business,application,description,domestic,access_code,pin_code,type):
        """
        Used to get the expected send notification message format.
        :param number: OIR record number
        :param state: OIR record state
        :param severity: OIR record severity
        :param business: OIR record business
        :param description: OIR record description
        :param application: OIR record application.
        :param bridge_number: OIR record reserved bridge number.
        :param type: notification message type: sms or email.
        :return: The expected message format.
        """
        self.sms_number = self._oir_number_transform(number)
        self.stat = self._oir_state_transform(state)
        self.sev = self._oir_severity_transform(severity)
        self.bridge_number = self._active_bridge_number_transform(domestic,access_code,pin_code)

        if (type == "sms"):
            return self.sms_number + "|" + self.sev + "|" + business + "|" + self.stat + "||" + self.bridge_number
        elif (type == "email"):
            return number + " " + self.sev + " " + business + " " + self.stat + " " + application + " | " + description
        else:
            raise AssertionError("Please enter the correct type, which is sms or email.")

    def get_expected_special_notification_message(self,number,state,severity,business,application,description,note,type):
        """
        Used to get the expected notification message format for special conditions.
        :param number: OIR record number.
        :param state: OIR record state.
        :param severity: OIR record severity.
        :param business: OIR record business.
        :param application: OIR record application.
        :param description: OIR record description.
        :param note: OIR record work note.
        :param type: notification message type: sms or email.
        :return: The expected message format.
        """
        self.sms_number = self._oir_number_transform(number)
        self.stat = self._oir_state_transform(state)
        self.sev = self._oir_severity_transform(severity)

        if (type == "sms"):
            return self.sms_number + "|" + self.sev + "|" + business + "|" + self.stat + "|" + note
        elif (type == "email"):
            return number + " " + self.sev + " " + business + " " + self.stat + " " + application + " | " + description
        else:
            raise AssertionError("Please enter the correct type, which is sms or email.")


