"""
This module contains the SolteqTandApp class, which
automates interactions with the SolteqTand application
using the UIAutomation library.
"""
import os
import time
import uiautomation as auto

from datetime import datetime


class ManualProcessingRequiredError(Exception):
    """
    Custom exception raised when the patient cannot be opened due incorrect SSN.
    """
    def __init__(self, message="Error occurred while opening the patient. There is no patient with the provided CPR number."):
        super().__init__(message)

class NotMatchingError(Exception):
    """
    Custom exception raised when inputted SSN does not match found SSN.
    """
    def __init__(self, in_msg=""):
        message = "Error occured while opening the patient. " + in_msg 
        super().__init__(message)
        
class PatientNotFoundError(Exception):
    """
    Custom exception raised when inputted SSN does not match any patient in registry.
    """
    def __init__(self, message = "Error occured while opening the patient. Patient not found"):
        super().__init__(message)

class SolteqTandApp:
    """
    A class to automate interactions with the SolteqTand application.
    """
    def __init__(self, app_path, username, password):
        """
        Initializes the SolteqTandApp object.

        Args:
            app_path (str): Path to the application.
            username (str): Username for login.
            password (str): Password for login.
            ssn (str): SSN for lookup.
        """
        self.app_path = app_path
        self.username = username
        self.password = password
        self.app_window = None

    def find_element_by_property(self, control, control_type=None, automation_id=None, name=None, class_name=None) -> auto.Control:
        """
        Uses GetChildren to traverse through controls and find an element based on the specified properties.

        Args:
            control (Control): The root control to search from (e.g., main window or pane).
            control_type (ControlType, optional): ControlType to search for.
            automation_id (str, optional): AutomationId of the target element.
            name (str, optional): Name of the target element.
            class_name (str, optional): ClassName of the target element.

        Returns:
            Control: The found element or None if no match is found.
        """
        children = control.GetChildren()

        for child in children:
            if (control_type is None or child.ControlType == control_type) and \
               (automation_id is None or child.AutomationId == automation_id) and \
               (name is None or child.Name == name) and \
               (class_name is None or child.ClassName == class_name):
                return child

            found = self.find_element_by_property(child, control_type, automation_id, name, class_name)
            if found:
                return found

        return None

    def wait_for_control(self, control_type, search_params, search_depth=1, timeout=30, retry_interval=0.5):
        """
        Waits for a given control type to become available with the specified search parameters.

        Args:
            control_type: The type of control, e.g., auto.WindowControl, auto.ButtonControl, etc.
            search_params (dict): Search parameters used to identify the control.
                                The keys must match the properties used in the control type, e.g., 'AutomationId', 'Name'.
            search_depth (int): How deep to search in the user interface.
            timeout (int): Maximum time to wait for the control, in seconds.
            retry_interval (float): Time to wait between retries, in seconds.

        Returns:
            Control: The control object if found, otherwise raises TimeoutError.

        Raises:
            TimeoutError: If the control is not found within the timeout period.
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                control = control_type(searchDepth=search_depth, **search_params)
                if control.Exists(0, 0):
                    return control
            except Exception as e:
                print(f"Error while searching for control: {e}")

            time.sleep(retry_interval)
            print(f"Retrying to find control: {search_params}...")

        raise TimeoutError(f"Control with parameters {search_params} was not found within the {timeout} second timeout.")

    def wait_for_control_to_disappear(self, control_type, search_params, search_depth=1, timeout=30):
        """
        Waits for a given control type to disappear with the specified search parameters.

        Args:
            control_type: The type of control, e.g., auto.WindowControl, auto.ButtonControl, etc.
            search_params (dict): Search parameters used to identify the control.
                                The keys must match the properties used in the control type, e.g., 'AutomationId', 'Name'.
            search_depth (int): How deep to search in the user interface.
            timeout (int): How long to wait, in seconds.

        Returns:
            bool: True if the control disappeared within the timeout period, otherwise False.
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                control = control_type(searchDepth=search_depth, **search_params)
                if not control.Exists(0, 0):
                    return True
            except Exception as e:
                print(f"Error while searching for control: {e}")

            time.sleep(0.5)
            print(f"Retrying to find control: {search_params}...")

        raise TimeoutError(f"Control with parameters {search_params} did not disappear within the timeout period.")

    def start_application(self):
        """
        Starts the application using the specified path.
        """
        os.startfile(self.app_path)

    def login(self):
        """
        Logs into the application by entering the username and password.
        Checks if the login window is open and ready.
        Checks if the main window is opened and ready.
        """
        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormLogin'},
            search_depth=3,
            timeout=60
        )
        self.app_window.SetFocus()

        username_box = self.app_window.EditControl(AutomationId="TextLogin")
        username_box.SendKeys(text=self.username)

        password_box = self.app_window.EditControl(AutomationId="TextPwd")
        password_box.SendKeys(text=self.password)

        login_button = self.app_window.PaneControl(AutomationId="ButtonLogin")
        login_button.SetFocus()
        login_button.SendKeys('{ENTER}')

        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormFront'},
            search_depth=2,
            timeout=60
        )

    def open_patient(self, ssn):
        """
        When the main window is open, presses Ctrl + O to open the 'Open Patient' window,
        searches for the SSN, and opens the patient.
        """
        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormFront'},
            search_depth=2,
            timeout=5
        )

        self.app_window.SetFocus()
        self.app_window.SendKeys('{Ctrl}o', waitTime=0)

        open_patient_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormOpenPatient'},
            search_depth=2
        )
        open_patient_window.SetFocus()

        ssn_input = open_patient_window.EditControl(AutomationId="TextBoxCpr")
        search_button = open_patient_window.PaneControl(AutomationId="ButtonOk")

        ssn_input.SendKeys(text=ssn)
        search_button.SetFocus()
        search_button.SendKeys('{ENTER}')

        # Here we handle possible error window popup.
        try: 
            patient_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormPatient'},
            timeout=5
            )
            self.app_window = patient_window
            
        except TimeoutError:
            error_window = self.wait_for_control(
                auto.WindowControl,
                {'Name': 'TMT - Åbn patient'},
                search_depth=2,
                timeout=10
            )

            if error_window is not None:
                error_window_button = error_window.ButtonControl(Name="OK")
                error_window_button.SetFocus()
                error_window_button.Click(simulateMove=False, waitTime=0)

                raise PatientNotFoundError


        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormPatient'},
            timeout=10
        )

        self.check_matching_ssn(ssn=ssn)

        self.app_window.Maximize()

    def open_sub_tab(self, sub_tab_name: str):
        """
        Opens a specific sub-tab in the patient's main card.

        Args:
            sub_tab_name (str): The name of the sub-tab to open (e.g., "Dokumenter").
        """
        sub_tab_button = self.app_window.TabItemControl(Name=sub_tab_name)
        is_sub_tab_selected = sub_tab_button.GetPattern(10010).IsSelected

        if not is_sub_tab_selected:
            sub_tab_button.SetFocus()
            sub_tab_button.SendKeys('{ENTER}')

    def open_tab(self, tab_name: str):
        """
        Opens a specific tab in the patient's main card.
        Poosibly functionality on other parts of Solteq with tabs as well.

        Args:
            tab_name (str): The name of the tab to open (e.g., "Frit valg").
        """
        match tab_name:
            case "Stamkort":
                tab_name_modified = "S&tamkort"
            case "Fritvalg":
                tab_name_modified = "F&ritvalg"
            case "Journal":
                tab_name_modified = "&Journal"
            case "Oversigt":
                tab_name_modified = "O&versigt"
            case _:
                tab_name_modified = tab_name

        tab_button = self.find_element_by_property(
            control=self.app_window,
            control_type=auto.ControlType.TabItemControl,
            name=tab_name_modified
        )
        is_tab_selected = tab_button.GetPattern(10010).IsSelected

        if not is_tab_selected:
            tab_button.SetFocus()
            tab_button.SendKeys('{ENTER}')

    def get_ssn_stamkort(self):
        self.open_tab("Stamkort")
        stamkort = self.wait_for_control(
            auto.PaneControl,
            search_params={
                'AutomationId': 'TabPageRecord'
            },
            search_depth=3
        )
        ssn = self.find_element_by_property(
            control=stamkort,
            control_type=50004,
            automation_id='TextPatientCprNumber'
        )
        ssn = ssn.GetValuePattern().Value
        return ssn

    def check_matching_ssn(self, ssn):
        # Navigate to stamkort
        found_ssn = self.get_ssn_stamkort()
        found_ssn = found_ssn.replace("-","")
        if found_ssn != ssn:
            raise NotMatchingError(in_msg=f"Found SSN {found_ssn} does not match input {ssn}")
        else:
            return True


    def create_document(self, document_full_path: str = None, document_type: str = None, document_description: str = None):
        """
        Creates a new document under the 'Dokumenter' tab.

        Args:
            document_full_path (str, optional): The full path of the document to upload.
            document_type (str, optional): The type of document to select from the dropdown.
        """
        self.open_tab("Stamkort")
        self.open_sub_tab("Dokumenter")

        document_list = self.find_element_by_property(
            control=self.app_window,
            control_type=auto.ControlType.ListControl,
            automation_id="cleverListView1"
        )
        document_list.RightClick(simulateMove=False, waitTime=0)

        document_list_menu = self.wait_for_control(
            auto.MenuControl,
            {'Name': 'Kontekst'},
            search_depth=2
        )

        menu_create_document = self.find_element_by_property(
            control=document_list_menu,
            control_type=auto.ControlType.MenuItemControl,
            name="Opret"
        )
        menu_create_document.Click(simulateMove=False, waitTime=0)

        create_document_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'UploadFile'},
            search_depth=2
        )
        file_path_textbox = self.find_element_by_property(
            control=create_document_window,
            control_type=auto.ControlType.EditControl,
            automation_id="textBoxLocalFilePath"
        )
        legacy_pattern = file_path_textbox.GetLegacyIAccessiblePattern()
        legacy_pattern.SetValue(document_full_path)

        if document_type:
            document_type_drop_down = self.find_element_by_property(
                control=create_document_window,
                control_type=auto.ControlType.ButtonControl,
                name="Åbn"
            )
            document_type_drop_down.Click(simulateMove=False, waitTime=0)

            document_type_button = self.find_element_by_property(
                control=create_document_window,
                control_type=auto.ControlType.ListItemControl,
                name=document_type
            )
            document_type_button.Click(simulateMove=False, waitTime=0)

        if document_description:
            description_text_field = self.find_element_by_property(
                control=create_document_window,
                control_type=auto.ControlType.DocumentControl,
                automation_id="richTextBoxDescription"
            )
            value_pattern = description_text_field.GetPattern(auto.PatternId.ValuePattern)
            value_pattern.SetValue(document_description)

        button_create_document = self.find_element_by_property(
            control=create_document_window,
            control_type=auto.ControlType.PaneControl,
            automation_id="buttonOpen"
        )
        button_create_document.Click(simulateMove=False, waitTime=0)

    def create_event(self, event_message: str, patient_clinic: str):
        """
        Creates an event for the given patient.

        Args:
            event_title (str): The title of the event to create.
            patient_clinic (str): The clinic associated with the patient.
        """
        self.open_tab("Stamkort")

        menu_funktioner = self.app_window.MenuItemControl(Name="Funktioner")
        menu_funktioner.Click(simulateMove=False, waitTime=0)

        henvis_patient = self.app_window.Control(
            Name="Henvis patient",
            ControlType=auto.ControlType.MenuItemControl
        )
        henvis_patient.Click(simulateMove=False, waitTime=0)

        clinic_list = self.wait_for_control(
            auto.WindowControl,
            {"AutomationId": "FormFindClinics"},
            search_depth=2
        )

        clinic_list_items = clinic_list.ListControl(AutomationId="ListClinics")
        clinic_list_item = clinic_list_items.Control(
            Name=patient_clinic,
            ControlType=auto.ControlType.ListItemControl
        )
        clinic_list_item.GetPattern(10017).ScrollIntoView()
        clinic_list_item.SetFocus()
        clinic_list_item.DoubleClick(simulateMove=False, waitTime=0)

        message_window = self.wait_for_control(
            auto.WindowControl,
            {"AutomationId": "VBInputBox"},
            search_depth=2
        )
        message_textbox = message_window.EditControl(AutmationId="TextBox")
        message_textbox_legacy_pattern = message_textbox.GetLegacyIAccessiblePattern()
        message_textbox_legacy_pattern.SetValue(event_message)
        message_textbox.SendKeys('{ENTER}')

        self.wait_for_control(
            self.app_window.TextControl,
            {'RegexName': '^Henvisning.*$'},
            search_depth=2
        )

        message_button = self.app_window.ButtonControl(Name="OK")
        message_button.Click(simulateMove=False, waitTime=0)

    def create_journal_note(self, note_message: str, checkmark_in_complete: bool):
        """
        Creates a journal note for the given patient.

        Args:
            note_message (str): The note message.
            checkmark_in_complete (bool): Checks the checkmark in 'Afslut'.
        """
        self.open_tab("Journal")

        self.wait_for_control(
            auto.DocumentControl,
            {"AutomationId": "RichTextBoxInput"},
            search_depth=19
            )

        input_box = self.app_window.DocumentControl(AutomationId="RichTextBoxInput")
        input_box_value_pattern = input_box.GetValuePattern()
        input_box_value_pattern.SetValue(value=note_message, waitTime=0)

        if checkmark_in_complete:
            checkbox = self.app_window.CheckBoxControl(AutomationId="CheckBoxAssignCompletionStatus")
            checkbox.SetFocus()
            checkbox.Click(simulateMove=False, waitTime=0)

        save_button = self.app_window.PaneControl(AutomationId="buttonSave")
        save_button.SetFocus()
        save_button.Click(simulateMove=False, waitTime=0)

    def set_extra_recipients(self, more_recepients: bool) -> None:
        """Set state of extra recipients. E.g. if patient is above 18
        
        Args:
            more_recipients (bool): Whether there should be more recipients. 
        
        """
        self.open_tab("Stamkort")
        stamkort = self.wait_for_control(
            auto.PaneControl,
            search_params={
                'AutomationId': 'TabPageRecord'
            },
            search_depth=3
        )
        msg_settings = self.find_element_by_property(
            control=stamkort,
            control_type=50033,
            automation_id='ButtonNemSMSSettings'
        )
        msg_settings.SendKeys('{ENTER}')
        settings_window = self.wait_for_control(
            control_type=auto.PaneControl,
            search_params={
                "AutomationId": "MessageSettingsControl"

            },
            search_depth=4
        )
        self.app_window = settings_window
        checkbox = self.find_element_by_property(
            control=settings_window,
            control_type=50002,
            automation_id="chkMoreRecipients"
        )
        # checkbox = self.wait_for_control(
        #     control_type=auto.CheckBoxControl,
        #     search_params={
        #         "AutomationId": "chkMoreRecipients"
        #     },
        #     search_depth=5
        # )
        if checkbox.GetTogglePattern().ToggleState != more_recepients:
            checkbox.GetTogglePattern().Toggle()

        ok_button = self.find_element_by_property(
            control=settings_window,
            control_type=50033,
            automation_id="btnOk"
        )
        ok_button.SendKeys('{ENTER}')

    def get_list_of_appointments(self) -> dict: 
        """
        Gets list of appointments as found in patient window

        Returns
            booking_list_dict (dict): Dictionary with appointments and informations
            booking_list_ctrls (list): List with the control related to each appointment

        Todo: Assure that view is on patient
        """
        # Open "Stamkort"
        self.open_tab("Stamkort")

        # Read elements in list and check that expected element exists
        # First get the list of appointments
        list_parent = self.find_element_by_property(
            control=self.app_window,
            automation_id='ControlBookingDay'
        )
        booking_list_ctrl = self.find_element_by_property(
            control=list_parent,
            control_type=50008
        )
        # Initiate dictionary for list elements
        booking_list = {'controls': []}
        # Initiate list to hold headers
        booking_list_keys = []
        rowcount = 0

        # Check for header
        if booking_list_ctrl.GetFirstChildControl().ControlType == 50034:
            # Loop through all elements in list
            for elem in booking_list_ctrl.GetChildren():
                # If header, then add each item to list of headers
                if elem.ControlType == 50034:
                    for colname in elem.GetChildren():
                        booking_list_keys.append(colname.Name)
                        booking_list[colname.Name] = []
                # If listitem, then add each item to dict
                if elem.ControlType == 50007:
                    booking_list['controls'].append(elem)  # Adds the control to accessed later
                    vals = elem.GetChildren()  # Extracts all information from control

                    for headercount, val in enumerate(vals):
                        booking_list[booking_list_keys[headercount]].append(val.Name)
                    rowcount += 1

        return booking_list
    
    def change_appointment_status(
            self,
            appointment_control: auto.ControlType,
            set_status: str,
            send_msg: bool = False
        ):
        """
        Changes status of appointment and optionally sends message

        Args:
            appointment_control (Control): Control element that identifies the appointment to be changed
            set_status (str): The status which the appointment should be changed to.
            send_msg (bool, optional): Indicates whether message should be sent when status is changed.
        """
        appointment_control.GetInvokePattern().Invoke()

        # Find booking control
        booking_control = self.wait_for_control(
            control_type=auto.PaneControl,
            search_params={
                'AutomationId': 'ManageBookingControl'
            },
            search_depth=3
        )

        # Find appointment status dropdown
        status_control = self.find_element_by_property(
            control=booking_control,
            control_type=50003,
            name='Status'
        )
        # Get current status to reset if warning on save
        current_status = status_control.GetValuePattern().Value

        # Open dropdown
        self.find_element_by_property(
            control=status_control,
            control_type=50000
        ).GetInvokePattern().Invoke()
        
        # Get list control for all status options
        status_list_ctrl = self.wait_for_control(
            control_type=auto.ListControl,
            search_params={
                'ClassName': 'ComboLBox'
            }
        )
        # Load status options into dict with controls, names and lowercase names
        status_dict = {
            'ctrls' : [elem for elem in status_list_ctrl.GetChildren() if elem.ControlType == 50007],
            'names' : [elem.Name for elem in status_list_ctrl.GetChildren() if elem.ControlType == 50007],
            'names_lo': [elem.Name.lower() for elem in status_list_ctrl.GetChildren() if elem.ControlType == 50007]
        }

        # Set new status if valid, otherwise return error
        if set_status.lower() in status_dict['names_lo']:
            list_no = status_dict['names_lo'].index(set_status.lower())
            status_dict['ctrls'][list_no].GetInvokePattern().Invoke()
            # Click "Gem og udsend"
            self.app_window = booking_control
            if send_msg:
                save_button = self.find_element_by_property(
                    control=booking_control,
                    automation_id = "ButtonSavePrint"
                )
            else:
                save_button = self.find_element_by_property(
                    control=booking_control,
                    automation_id = "ButtonOk"
                )
            save_button.SendKeys('{ENTER}')
            # Check for warning window pop up
            try:
                self.handle_error_on_booking_save(slct_button="ButtonChangeManual")
                # Wait for status list to reappear
                booking_control = self.wait_for_control(
                    control_type=auto.PaneControl,
                    search_params={
                        'AutomationId': 'ManageBookingControl'
                    },
                    search_depth=3
                )
                # Open dropdown
                self.find_element_by_property(
                    control=status_control,
                    control_type=50000
                ).GetInvokePattern().Invoke()
                # Reset to original value
                list_no = status_dict['names_lo'].index(current_status.lower())
                status_dict['ctrls'][list_no].GetInvokePattern().Invoke()
                # Save original status
                save_button = self.find_element_by_property(
                    control=booking_control,
                    automation_id = "ButtonOk"
                )
                save_button.SendKeys('{ENTER}')
                # Accept despite warning
                self.handle_error_on_booking_save(slct_button="ButtonOk")
               
                raise ManualProcessingRequiredError
            except TimeoutError:
                pass
            # Check for notification window pop up
            try:
                notification_ctrl = self.wait_for_control(
                    control_type=auto.PaneControl,
                    search_params={
                        'AutomationId': 'BookingNotificationsControl'
                    },
                    search_depth=3,
                    timeout=5
                )
                close_button = self.find_element_by_property(
                    control=notification_ctrl,
                    automation_id="ButtonCancel"
                )
                close_button.SendKeys('{ENTER}')
            except TimeoutError:
                pass
            
            #   If warning when sending: press "ret manuelt" -> "annuler" -> return warning error 

            return None
        else:
            print(f"{set_status} not in list. Possible status choices are: {', '.join(status_dict['names'])}")
            raise Exception

    def handle_error_on_booking_save(self, slct_button: str):
        """Handle error window when saving booking. Select button to press"""
        buttons = [
            "ButtonFindNewTimeSlot",
            "ButtonOk",
            "ButtonChangeManual"
        ]
        if slct_button not in buttons:
            print(f"{slct_button} not in buttons. Available buttons are {' '.join(buttons)}")
            raise ValueError
        warning_window = self.wait_for_control(
            control_type=auto.WindowControl,
            search_params={
                "AutomationId": "FormBookingWarnings"
            },
            search_depth=5
        )
        button = self.find_element_by_property(
            control=warning_window,
            control_type=50033,
            automation_id=slct_button
        )
        button.SendKeys("{ENTER}")
    
    def close_window(self, window_to_close = auto.WindowControl) -> None:
        """Closes sepcified window by """

        self.app_window = window_to_close
        self.app_window.SendKeys("^{{F4}}")

    def close_patient_window(self):
        """
        Closes the current patient's window and ensures the application returns to the main window.

        Raises:
            TimeoutError: If the patient window does not close within the expected time.
        """

        title_bar_window = self.app_window.TitleBarControl()
        title_bar_window.ButtonControl(Name="Luk").Click(simulateMove=False, waitTime=0)

        self.app_window = self.wait_for_control_to_disappear(
            auto.WindowControl,
            {'AutomationId': 'FormPatient'},
            search_depth=2
        )

        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormFront'},
            search_depth=2,
            timeout=5
        )

    def open_from_main_menu(self, menu_item: str) -> None:
        """
        Opens menu item from Solteq main menu"""

        # Find hyperlink
        menu_link = self.wait_for_control(
            control_type=auto.HyperlinkControl,
            search_params={
                'Name': menu_item
            },
            search_depth=5
        )

        menu_link.GetInvokePattern().Invoke()

        self.app_window = self.wait_for_control(
            control_type=auto.WindowControl,
            search_params={
                "AutomationId": "FormBooking"
            },
            search_depth=2
        )

    def set_date_in_aftalebog(self,from_date: datetime,to_date: datetime) -> None:
        """Set to and from dates in aftalebog oversigt"""
        import locale
        dt_picker_from = self.wait_for_control(
            control_type=auto.PaneControl,
            search_params={"AutomationId":"DateTimePickerFromDate"},
            search_depth=7)
        
        from_keys = (
            f"{from_date.day}" + 
            "{right}" + 
            f"{from_date.month}" + 
            "{right}" + 
            f"{from_date.year}"
        )

        dt_picker_from.SendKeys(from_keys)
        
        try:
            from_date.strftime(format="%d. %B %Y") == dt_picker_from.Name
        except:
            # Should maybe try a number of times until it hits right or ends in systemerror
            # End with raise error where resulting dates are printed
            print("Dates after insert not matching input")
            print((
                f"'From' input: {from_date.strftime(format="%d. %B %Y")} " +
                f"Current value: {dt_picker_from.Name}"))

        dt_picker_to = self.wait_for_control(
            control_type=auto.PaneControl,
            search_params={"AutomationId":"DateTimePickerToDate"},
            search_depth=7
        )

        to_keys = (
            f"{to_date.day}" + 
            "{right}" + 
            f"{to_date.month}" + 
            "{right}" + 
            f"{to_date.year}"
        )

        dt_picker_to.SendKeys(to_keys)

        locale.setlocale(locale.LC_TIME, 'da_dk.utf-8')

        try:
            to_date.strftime(format="%d. %B %Y") == dt_picker_to.Name
        except:
            print("Dates after insert not matching input")
            print((
                f"'To' input: {to_date.strftime(format="%d. %B %Y")} " +
                f"Current value: {dt_picker_to.Name}"))
            
    def pick_appointment_types_aftalebog(self, appointment_types: str | list):
        """Set one or more appointment types in aftalebog oversigt"""

        if isinstance(appointment_types, str):
            appointment_types = [appointment_types]

        # deselect all
        slct_none = self.wait_for_control(
            control_type=auto.PaneControl,
            search_params={
                "AutomationId": "ButtonToggleStatusList"
            },
            search_depth=7
        )
        slct_none.SetFocus()
        # If possible to select none click once, otherwise click twice
        try:
            assert slct_none.Name == "Vælge ingen"
            slct_none.SendKeys('{Enter}')
        except AssertionError:
            slct_none.SendKeys('{Enter}{Enter}')

        # Getting status controls
        status_list = self.wait_for_control(
            control_type=auto.ListControl,
            search_params={
                "AutomationId": "CheckedListBoxStatus"
            },
            search_depth=7
        )
        status_ctrls = [
            _child 
            for _child in status_list.GetChildren() 
            if _child.ControlType == 50002
        ]
        status_names = [
            _child.Name 
            for _child in status_list.GetChildren() 
            if _child.ControlType == 50002
        ]

        # Toggle all selected appointment types    
        for a_type in appointment_types:
            slct_idx = status_names.index(a_type)
            status_ctrls[slct_idx].GetTogglePattern().Toggle()

    def pick_clinic_aftalebog(self, clinic: str):
        """Set clinic in aftalebog oversigt"""

        ## UNFINISHED
        # Press clinic button
        clinic_button = self.wait_for_control(
            control_type=auto.PaneControl,
            search_params={
                'AutomationId': 'ButtonClinic'
            },
            search_depth=8
        )
        clinic_button.SetFocus()
        clinic_button.SendKeys('{Enter}')

        # Wait for popup window
        find_clinic = self.wait_for_control(
            control_type=auto.WindowControl,
            search_params={
                'AutomationId':'FormFindClinics'
            },
            search_depth=2
        )
        # Get list and select clinic
        clinic_list = self.find_element_by_property(
            control=find_clinic,
            automation_id='ListClinics'
        )
        clinic_ctrls = [
            _child
            for _child in clinic_list.GetChildren()
            if _child.ControlType == 50007
        ]
        clinic_names = [
            _child.Name
            for _child in clinic_list.GetChildren()
            if _child.ControlType == 50007
        ]
        try:
            slct_idx = clinic_names.index(clinic)
        except Exception as e:
            print(e)
            print(f"Chosen clinic: {clinic}")
            print("Possibilities: ")
            print(" \n".join(clinic_names[::-1]))
        # Search for the clinic if it is in the list (to get in focus)
        find_clinic.SendKeys(clinic)
        clinic_ctrls[slct_idx].SetFocus()
        clinic_ctrls[slct_idx].SendKeys('{Enter}')

    def get_appointments_aftalebog(
            self, 
            close_after: bool = False,
            headers_to_keep: list | None = None) -> dict:
        """Function to retrive data on appointments in view in aftalebog"""

        # Get list control
        list_box = self.wait_for_control(
            control_type=auto.GroupControl,
            search_params = {
                "AutomationId": "GroupBoxView"
            },
            search_depth=5
        )

        appointment_list = self.find_element_by_property(
            control=list_box,
            control_type=50008
        )

        # Extract headers
        appointment_headers = [
            header.Name
            for header in appointment_list.GetFirstChildControl().GetChildren()
        ]

        # Extract ListItem controls
        appointment_ctrls = [
            ctrl
            for ctrl in appointment_list.GetChildren()
            if ctrl.ControlType == 50007
        ]

        # Package data in dictionary
        # Keep only selected headers if any selected.
        if not headers_to_keep:
            headers_to_keep = appointment_headers

        appointment_data = {
            j: {
                k: v.Name
                for k, v in zip(appointment_headers, ctrl.GetChildren())
                if k in headers_to_keep
            }
            for j, ctrl in enumerate(appointment_ctrls)
        }

        if close_after:
            # Should maybe be in a method of its own?
            list_box.SendKeys('{Control}{F4}')
            self.wait_for_control_to_disappear(
                control_type=auto.WindowControl,
                search_params={
                    "AutomationId": "FormBooking"
                }
            )

        return appointment_data

    def close_solteq_tand(self):
        """
        Closes the SolteqTand application and confirms the closure.

        Raises:
            TimeoutError: If the application does not close within the expected time.
        """
        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormFront'},
            search_depth=2
        )
        self.app_window.SetFocus()
        title_bar_window = self.app_window.TitleBarControl()
        title_bar_window.ButtonControl(Name="Luk").Click(simulateMove=False, waitTime=0)

        self.app_window = self.wait_for_control(
            auto.ButtonControl,
            {'Name': 'Ja'},
            search_depth=3
        )

        self.app_window.Click(simulateMove=False)

        self.app_window = self.wait_for_control_to_disappear(
            auto.WindowControl,
            {'AutomationId': 'FormFront'},
            search_depth=2
        )
