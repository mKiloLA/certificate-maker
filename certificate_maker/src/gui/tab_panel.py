"""Class to display loading options.

Author: Zak Oster zcoster@ksu.edu
Version: 0.1
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog

from certificate_maker.src.data.emails import send_emails
from certificate_maker.src.data.certificate import create_certificates
from certificate_maker.src.data.on_demand.on_demand import create_on_demand_report
from certificate_maker.src.data.state_submission import create_state_submission_report
from certificate_maker.src.exception_types import *


class TabPanel(tk.Frame):
    """Class to display loading options."""

    def __init__(self, master, terminal, set_create_tab=False) -> None:
        """Constructor to initialize the menu panel."""
        self.__master = master
        ttk.Frame.__init__(self, master=self.__master)

        self.__zoom_file = None
        self.__webinar_file = None
        self.__json_file = None
        self.__attend_file = None
        self.__eval_file = None
        self.__on_demand_file = None
        self.__state_attendance_file = None
        self.__poll_file = None
        self.__zoom_survey_file = None
        self.terminal = terminal

        self.__loading_tabs: ttk.Notebook = ttk.Notebook(master=self)
        self.__file_labels = {}
        verification_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        create_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        state_submission_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        email_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        on_demand_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)

        # Keep tab registration in one place so new tabs only need a frame and title.
        self.__add_tab(verification_tab, "Verify")
        self.__add_tab(create_tab, "Create Certificates")
        self.__add_tab(state_submission_tab, "State Submissions")
        self.__add_tab(email_tab, "Send Emails")
        self.__add_tab(on_demand_tab, "On-Demand")
        self.__loading_tabs.pack(expand=1, fill="both")

        if set_create_tab:
            self.__loading_tabs.select(create_tab)

        self.__build_file_input_tab(
            verification_tab,
            [
                ("verify_zoom", "zoom", "Browse for Zoom File", "Zoom File"),
                ("verify_webinar", "webinar", "Browse for webinar File", "Webinar File"),
            ],
            [("Submit Files", "verify_files")],
        )

        self.__build_file_input_tab(
            create_tab,
            [
                ("create_zoom", "zoom", "Browse for Zoom File", "Zoom File"),
                ("create_webinar", "webinar", "Browse for webinar File", "Webinar File"),
            ],
            [("Submit Files", "submit")],
        )

        self.__build_file_input_tab(
            state_submission_tab,
            [
                ("state_json", "state_json", "Browse for Certificate JSON file", "JSON file"),
                ("poll", "poll", "Browse for Zoom Poll file", "Zoom Poll file"),
                ("zoom_survey", "zoom_survey", "Browse for Zoom Survey file", "Zoom Survey file"),
                ("state_attendance", "state_attendance", "Browse for Attendance Sheet", "Original Attendance Sheet"),
            ],
            [("Submit Files", "submit-state-submission")],
        )

        self.__build_file_input_tab(
            email_tab,
            [("email_json", "find_json", "Browse for Webinar JSON file", "JSON file")],
            [("Test Send Emails", "test_email"), ("Send Emails", "submit_email")],
        )

        self.__build_file_input_tab(
            on_demand_tab,
            [
                ("attend", "attend-file", "Browse for Submission File", "Submission File"),
                ("eval", "eval-file", "Browse for Evaluation File", "Evaluation File"),
                ("on_demand", "on-demand-file", "Browse for On-Demand File", "On-Demand File"),
            ],
            [("Submit Files", "submit-on-demand")],
        )


    def __add_tab(self, frame: ttk.Frame, title: str) -> None:
        """Register a tab in notebook order."""
        self.__loading_tabs.add(frame, text=title)

    def __build_file_input_tab(
        self,
        tab: ttk.Frame,
        fields: list[tuple[str, str, str, str]],
        actions: list[tuple[str, str]],
    ) -> None:
        """Build a tab made up of file selectors and configurable actions."""
        for row, (label_key, action, button_text, label_text) in enumerate(fields):
            tab.grid_rowconfigure(row, weight=1)
            self.__add_file_selector(tab, row, label_key, action, button_text, label_text)

        tab.grid_columnconfigure(0, weight=1, minsize=150)
        tab.grid_columnconfigure(1, weight=1, minsize=150)
        for row, (button_text, action) in enumerate(actions, start=len(fields)):
            tab.grid_rowconfigure(row, weight=1)
            button = tk.Button(
                tab,
                font=("Arial", 12),
                text=button_text,
                command=lambda action=action: self.action_performed(action),
                bg="gray",
                height=5,
                width=70,
            )
            button.grid(row=row, columnspan=2, padx=2, pady=2)

    def __add_file_selector(
        self,
        tab: ttk.Frame,
        row: int,
        label_key: str,
        action: str,
        button_text: str,
        label_text: str,
    ) -> None:
        """Add a file selector and bind its label to a named file field."""
        button = tk.Button(
            tab,
            font=("Arial", 10),
            text=button_text,
            command=lambda: self.action_performed(action),
            bg="light gray",
            height=5,
            width=20,
        )
        button.grid(row=row, column=0, padx=2, pady=2)

        label = tk.Label(
            tab,
            text=f"No {label_text} Selected",
            font=("Arial", 12),
            justify="left",
        )
        label.grid(row=row, column=1, padx=2, pady=2, sticky="W")
        self.__file_labels[label_key] = label

    def __select_file(self, label_key: str, title: str) -> str:
        selected_file = self.browse_for_file(title)
        if not selected_file:
            return ""
        filename = os.path.basename(selected_file)
        self.__file_labels[label_key].configure(text=f"{filename} selected.")
        self.terminal.print_message(f"{title}: {filename} selected.")
        return selected_file

    def action_performed(self, text: str) -> None:
        """Performs an action given a string.

        Args:
            text: str, string indicator of which action to perform

        Returns:
            None
        """
        # File actions update shared state and every tab that displays that file.
        if text == "zoom":
            self.__zoom_file = self.browse_for_file("Browse for zoom.csv file")
            if not self.__zoom_file:
                return
            filename = self.__zoom_file.split("/")[-1]
            self.__file_labels["create_zoom"].configure(text="{} selected.".format(filename))
            self.__file_labels["verify_zoom"].configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"Zoom file: {filename} selected.")
        elif text == "webinar":
            self.__webinar_file = self.browse_for_file("Browse for webinar.xlsx file")
            if not self.__webinar_file:
                return
            filename = self.__webinar_file.split("/")[-1]
            self.__file_labels["create_webinar"].configure(text="{} selected.".format(filename))
            self.__file_labels["verify_webinar"].configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"CLE file: {filename} selected.")
        # Processing actions validate inputs before calling the data layer.
        elif text == "submit":
            if self.__zoom_file is not None and self.__webinar_file is not None:
                try:
                    # Create certificates
                    self.terminal.print_message(f"Certificate creation started . . .")
                    self.__json_file = create_certificates(self.__zoom_file, self.__webinar_file)
                    self.terminal.print_message(f". . . Certificate creation finished!")

                    # Automatically select the json file
                    if self.__json_file:
                        filename = self.__json_file.split("/")[-1]
                        self.__file_labels["email_json"].configure(text="{} selected.".format(filename))
                        self.__file_labels["state_json"].configure(text="{} selected.".format(filename))
                        self.terminal.print_message(f"JSON file: {filename} selected.")
                    else:
                        self.terminal.print_message(f"Certificate creation failed: No JSON file was created.")
                except IncorrectDateTimeFormat as e:
                    self.terminal.print_message(f"Check time format: Failed to parse time information for `{e}`.")
                except IncorrectNumberOfBreaks as e:
                    self.terminal.print_message(f"Check Breaks: Zoom file asks for `{e}` breaks, but not enough times were given.")
                except IncorrectBreakDate as e:
                    self.terminal.print_message("Check Breaks: The date of the breaks does not match the date of the CLE.")
                except IncorrectWebinarTitle as e:
                    self.terminal.print_message(f"Check CLE name: There are no CLEs matching `{e}`.")
                except MasterListMissingHours as e:
                    self.terminal.print_message(f"Check Master CLE List: CLE list is missing total hours in `{e}`.")
                except MissingStateApproval as e:
                    e = str(e).split(", ")
                    temp = []
                    for entry in e:
                        name = "".join([x for x in entry if x not in ["(", ")", "'", ","]])
                        temp.append(name)
                    e = temp
                    self.terminal.print_message(f"Check State Approvals: `{e[0]}` has no approval infomation in the state of `{e[1]}`.")
                except AttorneyMissingState as e:
                    self.terminal.print_message(f"Check State: `{e}` has no state listed.")
                except AttorneyInvalidState as e:
                    self.terminal.print_message(f"Check State: `{e}` does not have a valid state listed.")
                except AttorneyMissingBarNumber as e:
                    self.terminal.print_message(f"Check Bar Number: `{e}` has no bar number listed.")
                except AttorneyInvalidBarNumber as e:
                    self.terminal.print_message(f"Check Bar Number: `{e}` does not have a valid bar number listed.")
                except MissingBreakRow:
                    self.terminal.print_message("Check Zoom File: There is no `Breaks` row in the CSV file.")
                except MissingStartRow:
                    self.terminal.print_message("Check Zoom File: There is no `Start` row in the CSV file.")
                except MismatchingStateAndBarNumbers as e:
                    self.terminal.print_message(f"Check Bar Number and State: `{e}` has a mismatching number of bar numbers and states.")
                except Exception as e:
                    self.terminal.print_message(
                        f"Unknown Error: double check that the information in the Zoom and Master CLE list is correct. Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
            if self.__zoom_file is None:
                self.__file_labels["create_zoom"].configure(text="You must select a file!")
            if self.__webinar_file is None:
                self.__file_labels["create_webinar"].configure(text="You must select a file!")
        elif text == "test_email":
            try:
                self.terminal.print_message(f"Sending test emails . . .")
                send_emails(self.__json_file, demo=True)
                self.terminal.print_message(f". . . Test emails sent!")
            except Exception as e:
                self.terminal.print_message(f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
        elif text == "submit_email":
            try:
                self.terminal.print_message(f"Sending emails . . .")
                send_emails(self.__json_file, demo=False)
                self.terminal.print_message(f". . . Emails sent!")
            except Exception as e:
                self.terminal.print_message(f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
        elif text == "find_json":
            self.__json_file = self.browse_for_file(title="Browse for JSON File")
            if not self.__json_file:
                return
            filename = self.__json_file.split("/")[-1]
            self.__file_labels["email_json"].configure(text="{} selected.".format(filename))
            self.__file_labels["state_json"].configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"JSON file: {filename} selected.")
        elif text == "state_json":
            self.__json_file = self.__select_file("state_json", "Browse for Certificate JSON file")
        elif text == "poll":
            self.__poll_file = self.__select_file("poll", "Browse for Zoom Poll file")
        elif text == "zoom_survey":
            self.__zoom_survey_file = self.__select_file(
                "zoom_survey", "Browse for Zoom Survey file"
            )
        elif text == "state_attendance":
            self.__state_attendance_file = self.__select_file(
                "state_attendance", "Browse for Original Attendance Sheet"
            )
        elif text == "submit-state-submission":
            required_files = [
                (self.__json_file, self.__file_labels["state_json"]),
                (self.__poll_file, self.__file_labels["poll"]),
                (self.__zoom_survey_file, self.__file_labels["zoom_survey"]),
                (self.__state_attendance_file, self.__file_labels["state_attendance"]),
            ]
            if all(file_path for file_path, _ in required_files):
                assert self.__json_file is not None
                assert self.__poll_file is not None
                assert self.__zoom_survey_file is not None
                try:
                    self.terminal.print_message("State submission report generation started . . .")
                    output_file = create_state_submission_report(
                        self.__json_file,
                        self.__poll_file,
                        self.__zoom_survey_file,
                        self.__state_attendance_file,
                    )
                    self.terminal.print_message(
                        f". . . State submission report created: {output_file}"
                    )
                except Exception as e:
                    self.terminal.print_message(
                        f"Unknown Error: Could not create the state submission report: `{e}`"
                    )
            else:
                for file_path, label in required_files:
                    if not file_path:
                        label.configure(text="You must select a file!")
        elif text == "verify_files":
            if self.__zoom_file is not None and self.__webinar_file is not None:
                try:
                    self.terminal.print_message(f"Certificate verification started . . .")
                    create_certificates(self.__zoom_file, self.__webinar_file, create=False)
                    self.terminal.print_message(f". . . Certificate verification finished!")
                except IncorrectDateTimeFormat as e:
                    self.terminal.print_message(f"Check time format: Failed to parse time information for `{e}`.")
                except IncorrectNumberOfBreaks as e:
                    self.terminal.print_message(f"Check Breaks: Zoom file asks for `{e}` breaks, but not enough times were given.")
                except IncorrectBreakDate as e:
                    self.terminal.print_message("Check Breaks: The date of the breaks does not match the date of the CLE.")
                except IncorrectWebinarTitle as e:
                    self.terminal.print_message(f"Check CLE name: There are no CLEs matching `{e}`.")
                except MasterListMissingHours as e:
                    self.terminal.print_message(f"Check Master CLE List: CLE list is missing total hours in `{e}`.")
                except MissingStateApproval as e:
                    e = str(e).split(", ")
                    temp = []
                    for entry in e:
                        name = "".join([x for x in entry if x not in ["(", ")", "'", ","]])
                        temp.append(name)
                    e = temp
                    self.terminal.print_message(f"Check State Approvals: `{e[0]}` has no approval infomation in the state of `{e[1]}`.")
                except AttorneyMissingState as e:
                    self.terminal.print_message(f"Check State: `{e}` has no state listed.")
                except AttorneyInvalidState as e:
                    self.terminal.print_message(f"Check State: `{e}` does not have a valid state listed.")
                except AttorneyMissingBarNumber as e:
                    self.terminal.print_message(f"Check Bar Number: `{e}` has no bar number listed.")
                except AttorneyInvalidBarNumber as e:
                    self.terminal.print_message(f"Check Bar Number: `{e}` does not have a valid bar number listed.")
                except MissingBreakRow:
                    self.terminal.print_message("Check Zoom File: There is no `Breaks` row in the CSV file.")
                except MissingStartRow:
                    self.terminal.print_message("Check Zoom File: There is no `Start` row in the CSV file.")
                except MismatchingStateAndBarNumbers as e:
                    self.terminal.print_message(f"Check Bar Number and State: `{e}` has a mismatching number of bar numbers and states.")
                except Exception as e:
                    self.terminal.print_message(
                        f"Unknown Error: double check that the information in the Zoom and Master CLE list is correct. Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
            if self.__zoom_file is None:
                self.__file_labels["verify_zoom"].configure(text="You must select a file!")
            if self.__webinar_file is None:
                self.__file_labels["verify_webinar"].configure(text="You must select a file!")
        elif text == "attend-file":
            self.__attend_file = self.browse_for_file("Browse for submission.csv file")
            if not self.__attend_file:
                return
            self.terminal.print_message(f"Submission file: {self.__attend_file} selected.")
            filename = self.__attend_file.split("/")[-1]
            self.__file_labels["attend"].configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"Submission file: {filename} selected.")
        elif text == "eval-file":
            self.__eval_file = self.browse_for_file("Browse for evaluation.csv file")
            if not self.__eval_file:
                return
            filename = self.__eval_file.split("/")[-1]
            self.__file_labels["eval"].configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"Evaluation file: {filename} selected.")
        elif text == "on-demand-file":
            self.__on_demand_file = self.browse_for_file("Browse for on-demand-reference.xlsx file")
            if not self.__on_demand_file:
                return
            filename = self.__on_demand_file.split("/")[-1]
            self.__file_labels["on_demand"].configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"On-Demand Reference file: {filename} selected.")
        elif text == "submit-on-demand":
            if self.__attend_file is not None and self.__eval_file is not None and self.__on_demand_file is not None:
                try:
                    self.terminal.print_message(f"On-Demand Report generation started . . .")
                    create_on_demand_report(self.__attend_file, self.__eval_file, self.__on_demand_file)
                    self.terminal.print_message(f". . . On-Demand Report generation finished!")
                except MalformedEvaluationQuestionResponse as e:
                    self.terminal.print_message(f"Check Evaluation Question Responses: `{e}` has a malformed response to an evaluation question.")
                except MalformedCROString as e:
                    self.terminal.print_message(f"Check Submitted CRO cell on Submission Report: `{e}` has a CRO string that is not in the format `State: BarNumber - Hours`.")
                except IncorrectDateTimeFormat as e:
                    self.terminal.print_message(f"Check time format: Failed to parse time information for `{e}`.")
                except ReferenceFileMissingSheet as e:
                    self.terminal.print_message(f"Check On-Demand Reference File: There is no sheet named `{e.args[0]}` in the reference file.")
                except MissingSubmissionData as e:
                    self.terminal.print_message(f"Submission Report missing data: `{e.args[0]}` is missing required data for course `{e.args[1]}`.")
                except MissingEvaluationData as e:
                    self.terminal.print_message(f"Evaluation Report missing data: `{e.args[0]}` is missing required data for course `{e.args[1]}`.")
                except ReferenceFileMissingCourse as e:
                    self.terminal.print_message(f"Check On-Demand Reference File: There is no course titled `{e.args[0]}` in the reference file for the state of `{e.args[1]}`.")
                except Exception as e:
                    self.terminal.print_message(f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
            if self.__attend_file is None:
                self.__file_labels["attend"].configure(text="You must select a file!")
            if self.__eval_file is None:
                self.__file_labels["eval"].configure(text="You must select a file!")
            if self.__on_demand_file is None:
                self.__file_labels["on_demand"].configure(text="You must select a file!")
        else:
            pass

    def browse_for_file(self, title):
        return filedialog.askopenfilename(
            title=title,
        )
