"""Class to display loading options.

Author: Zak Oster zc9oster@gmail.com
Version: 0.1
"""

import os
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk, filedialog
from typing import Any

from certificate_maker.src.gui.theme import (
    ACCENT,
    ACCENT_HOVER,
    ACCENT_PRESSED,
    BACKGROUND,
    SURFACE,
    SURFACE_RAISED,
    SURFACE_HOVER,
    TEXT_SECONDARY,
)
from certificate_maker.src.gui.file_selector import FileSelector
from certificate_maker.src.exception_types import (
    AttorneyInvalidBarNumber,
    AttorneyInvalidState,
    AttorneyMissingBarNumber,
    AttorneyMissingState,
    IncorrectBreakDate,
    IncorrectDateTimeFormat,
    IncorrectNumberOfBreaks,
    IncorrectWebinarTitle,
    MalformedCROString,
    MalformedEvaluationQuestionResponse,
    MasterListMissingHours,
    MissingBreakRow,
    MissingEvaluationData,
    MissingStartRow,
    MissingStateApproval,
    MissingSubmissionData,
    MismatchingStateAndBarNumbers,
    ReferenceFileMissingCourse,
    ReferenceFileMissingSheet,
    StateSubmissionFileNotFound,
    StateSubmissionInvalidJson,
    StateSubmissionMissingData,
    StateSubmissionMissingPollData,
    StateSubmissionMissingSurveyData,
)
from certificate_maker.src.gui.widgets import RoundedButton


class TabPanel(tk.Frame):
    """Class to display loading options."""

    def __init__(
        self,
        master: Any,
        terminal: Any,
        set_create_tab: bool = False,
        *,
        show_status_banner: Callable[[str, bool], None],
    ) -> None:
        """Constructor to initialize the menu panel."""
        super().__init__(master)
        self.configure(bg=BACKGROUND)

        self.__zoom_file: str | None = None
        self.__webinar_file: str | None = None
        self.__json_file: str | None = None
        self.__attend_file: str | None = None
        self.__eval_file: str | None = None
        self.__on_demand_file: str | None = None
        self.__state_attendance_file: str | None = None
        self.__poll_file: str | None = None
        self.__zoom_survey_file: str | None = None
        self.terminal = terminal
        self.__show_status_banner = show_status_banner
        self.__submit_step_names = {
            "submit": "Certificate creation",
            "verify_files": "File verification",
            "test_email": "Test email delivery",
            "submit_email": "Email delivery",
            "submit-state-submission": "State submission report",
            "submit-on-demand": "On-Demand report",
        }

        self.__tab_bar = tk.Frame(self, bg=BACKGROUND)
        self.__tab_bar.grid(row=0, column=0, padx=20, pady=(0, 8), sticky="EW")
        self.__content = ttk.Frame(self)
        self.__content.grid(row=1, column=0, sticky="NSEW")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.__content.grid_columnconfigure(0, weight=1)
        self.__content.grid_rowconfigure(0, weight=1)

        self.__tab_buttons: list[tuple[ttk.Frame, RoundedButton]] = []
        self.__selected_tab: ttk.Frame | None = None
        self.__file_selectors: dict[str, FileSelector] = {}
        verification_tab: ttk.Frame = ttk.Frame(self.__content)
        create_tab: ttk.Frame = ttk.Frame(self.__content)
        state_submission_tab: ttk.Frame = ttk.Frame(self.__content)
        email_tab: ttk.Frame = ttk.Frame(self.__content)
        on_demand_tab: ttk.Frame = ttk.Frame(self.__content)

        # Keep tab registration in one place so new tabs only need a frame and title.
        self.__add_tab(verification_tab, "Verify")
        self.__add_tab(create_tab, "Create Certificates")
        self.__add_tab(state_submission_tab, "State Submissions")
        self.__add_tab(email_tab, "Send Emails")
        self.__add_tab(on_demand_tab, "On-Demand")

        self.__build_file_input_tab(
            verification_tab,
            "Verify source files",
            "Check the Zoom and webinar files before creating certificates.",
            [
                ("verify_zoom", "zoom", "Zoom File"),
                ("verify_webinar", "webinar", "Webinar File"),
            ],
            [("Submit Files", "verify_files")],
        )

        self.__build_file_input_tab(
            create_tab,
            "Create certificates",
            "Choose the Zoom and webinar files used to generate attendee certificates.",
            [
                ("create_zoom", "zoom", "Zoom File"),
                ("create_webinar", "webinar", "Webinar File"),
            ],
            [("Submit Files", "submit")],
        )

        self.__build_file_input_tab(
            state_submission_tab,
            "Prepare state submission",
            "Choose the certificate JSON and supporting attendance files.",
            [
                ("state_json", "state_json", "Certificate JSON"),
                ("poll", "poll", "Zoom Poll File"),
                ("zoom_survey", "zoom_survey", "Zoom Survey File"),
                ("state_attendance", "state_attendance", "Original Attendance Sheet"),
            ],
            [("Create Submission Report", "submit-state-submission")],
        )

        self.__build_file_input_tab(
            email_tab,
            "Send certificate emails",
            "Choose the webinar JSON file to test or send attendee emails.",
            [("email_json", "find_json", "Webinar JSON")],
            [("Test Send Emails", "test_email"), ("Send Emails", "submit_email")],
        )

        self.__build_file_input_tab(
            on_demand_tab,
            "Prepare an on-demand report",
            "Choose the attendance, evaluation, and reference files for this report.",
            [
                ("attend", "attend-file", "Submission File"),
                ("eval", "eval-file", "Evaluation File"),
                ("on_demand", "on-demand-file", "On-Demand Reference File"),
            ],
            [("Create On-Demand Report", "submit-on-demand")],
        )

        self.__select_tab(create_tab if set_create_tab else verification_tab)

    def __add_tab(self, frame: ttk.Frame, title: str) -> None:
        """Register a page and its equal-width navigation button."""
        column = len(self.__tab_buttons)
        frame.grid(row=0, column=0, sticky="NSEW")
        self.__tab_bar.grid_columnconfigure(column, weight=1, uniform="tabs")
        button = RoundedButton(
            self.__tab_bar,
            text=title,
            command=lambda frame=frame: self.__select_tab(frame),
            background=SURFACE,
            foreground=TEXT_SECONDARY,
            hover_background=SURFACE_HOVER,
            active_background=SURFACE_RAISED,
            selected_background=SURFACE_HOVER,
            selected_foreground=ACCENT,
            canvas_background=BACKGROUND,
            height=44,
            radius=14,
            font=("Arial", 12, "bold"),
        )
        button.grid(row=0, column=column, padx=4, sticky="EW")
        self.__tab_buttons.append((frame, button))

    def __select_tab(self, selected_frame: ttk.Frame) -> None:
        self.__selected_tab = selected_frame
        selected_frame.grid(row=0, column=0, sticky="NSEW")
        selected_frame.tkraise()
        for frame, button in self.__tab_buttons:
            button.set_selected(frame is selected_frame)
        self.after_idle(self.__hide_inactive_tabs)

    def __hide_inactive_tabs(self) -> None:
        for frame, _ in self.__tab_buttons:
            if frame is not self.__selected_tab:
                frame.grid_remove()

    def __build_file_input_tab(
        self,
        tab: ttk.Frame,
        title: str,
        description: str,
        fields: list[tuple[str, str, str]],
        actions: list[tuple[str, str]],
    ) -> None:
        """Build a tab made up of file selectors and configurable actions."""
        tab.grid_columnconfigure(0, weight=1)

        page_title = ttk.Label(tab, text=title, style="PageTitle.TLabel")
        page_title.grid(row=0, column=0, padx=20, pady=(12, 3), sticky="W")
        page_description = ttk.Label(
            tab, text=description, style="PageDescription.TLabel"
        )
        page_description.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="W")

        for row, (label_key, action, label_text) in enumerate(fields, start=2):
            self.__add_file_selector(tab, row, label_key, action, label_text)

        action_row = len(fields) + 2
        action_bar = tk.Frame(tab, bg=BACKGROUND)
        action_bar.grid(row=action_row, column=0, padx=20, pady=(10, 6), sticky="EW")

        for column, (button_text, action) in enumerate(actions):
            is_test_action = action == "test_email"
            button = RoundedButton(
                action_bar,
                text=button_text,
                command=lambda action=action: self.action_performed(action),
                background=ACCENT,
                foreground=BACKGROUND,
                hover_background=ACCENT_HOVER,
                active_background=ACCENT_PRESSED,
                canvas_background=BACKGROUND,
                height=42 if is_test_action else 46,
                radius=13,
                font=("Arial", 13 if is_test_action else 14, "bold"),
            )
            button.grid(
                row=0,
                column=column,
                padx=(0, 10 if column < len(actions) - 1 else 0),
                sticky="EW",
            )
            action_bar.grid_columnconfigure(column, weight=1, uniform="actions")

        tab.grid_rowconfigure(action_row + 1, weight=1)

    def __add_file_selector(
        self,
        tab: ttk.Frame,
        row: int,
        label_key: str,
        action: str,
        label_text: str,
    ) -> None:
        """Add a file selector and bind it to a named file field."""
        selector = FileSelector(
            tab,
            label_text,
            on_file_selected=lambda selected_file, action=action: self.action_performed(
                action, selected_file=selected_file
            ),
            log_message=self.terminal.print_message,
        )
        selector.grid(row=row, column=0, padx=20, pady=4, sticky="EW")
        self.__file_selectors[label_key] = selector

    def __set_file_status(
        self,
        label_key: str,
        filename: str,
        metadata: str,
        *,
        selected: bool = False,
    ) -> None:
        self.__file_selectors[label_key].set_file_status(
            filename,
            metadata,
            selected=selected,
        )

    def __set_file_selected(self, label_key: str, selected_file: str) -> None:
        filename = os.path.basename(selected_file)
        extension = os.path.splitext(filename)[1].lstrip(".").upper() or "FILE"
        try:
            size = os.path.getsize(selected_file)
        except OSError as error:
            self.terminal.print_message(
                f"Could not read the size of `{filename}`: {error}"
            )
            size_text = "size unavailable"
        else:
            size_text = self.__format_file_size(size)

        self.__set_file_status(
            label_key,
            filename,
            f"{extension}  |  {size_text}",
            selected=True,
        )

    @staticmethod
    def __format_file_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"

        size_in_units = float(size)
        for unit in ("KB", "MB", "GB", "TB"):
            size_in_units /= 1024
            if size_in_units < 1024 or unit == "TB":
                return f"{size_in_units:.1f} {unit}"
        return f"{size} B"

    def __choose_file(self, title: str, selected_file: str | None) -> str:
        if selected_file is not None:
            return selected_file
        return self.browse_for_file(title)

    def __select_file(
        self, label_key: str, title: str, selected_file: str | None = None
    ) -> str:
        selected_file = self.__choose_file(title, selected_file)
        if not selected_file:
            return ""
        filename = os.path.basename(selected_file)
        self.__set_file_selected(label_key, selected_file)
        self.terminal.print_message(f"{title}: {filename} selected.")
        return selected_file

    def __log_certificate_error(self, error: Exception) -> None:
        if isinstance(error, IncorrectDateTimeFormat):
            self.terminal.print_message(
                f"Check time format: Failed to parse time information for `{error}`."
            )
        elif isinstance(error, IncorrectNumberOfBreaks):
            self.terminal.print_message(
                f"Check Breaks: Zoom file asks for `{error}` breaks, but not enough times were given."
            )
        elif isinstance(error, IncorrectBreakDate):
            self.terminal.print_message(
                "Check Breaks: The date of the breaks does not match the date of the CLE."
            )
        elif isinstance(error, IncorrectWebinarTitle):
            self.terminal.print_message(
                f"Check CLE name: There are no CLEs matching `{error}`."
            )
        elif isinstance(error, MasterListMissingHours):
            self.terminal.print_message(
                f"Check Master CLE List: CLE list is missing total hours in `{error}`."
            )
        elif isinstance(error, MissingStateApproval):
            entries = str(error).split(", ")
            names = [
                "".join(character for character in entry if character not in "()',")
                for entry in entries
            ]
            self.terminal.print_message(
                f"Check State Approvals: `{names[0]}` has no approval infomation in the state of `{names[1]}`."
            )
        elif isinstance(error, AttorneyMissingState):
            self.terminal.print_message(f"Check State: `{error}` has no state listed.")
        elif isinstance(error, AttorneyInvalidState):
            self.terminal.print_message(
                f"Check State: `{error}` does not have a valid state listed."
            )
        elif isinstance(error, AttorneyMissingBarNumber):
            self.terminal.print_message(
                f"Check Bar Number: `{error}` has no bar number listed."
            )
        elif isinstance(error, AttorneyInvalidBarNumber):
            self.terminal.print_message(
                f"Check Bar Number: `{error}` does not have a valid bar number listed."
            )
        elif isinstance(error, MissingBreakRow):
            self.terminal.print_message(
                "Check Zoom File: There is no `Breaks` row in the CSV file."
            )
        elif isinstance(error, MissingStartRow):
            self.terminal.print_message(
                "Check Zoom File: There is no `Start` row in the CSV file."
            )
        elif isinstance(error, MismatchingStateAndBarNumbers):
            self.terminal.print_message(
                f"Check Bar Number and State: `{error}` has a mismatching number of bar numbers and states."
            )
        else:
            self.terminal.print_message(
                f"Unknown Error: double check that the information in the Zoom and Master CLE list is correct. Email the files and the following error message to Zak so he can add error checks for it in the future: `{error}`"
            )

    def __run_certificate_action(self, *, create: bool) -> bool:
        succeeded = False
        if self.__zoom_file is not None and self.__webinar_file is not None:
            action_name = "creation" if create else "verification"
            try:
                self.terminal.print_message(f"Certificate {action_name} started . . .")
                from certificate_maker.src.data.certificate import (
                    create_certificates,
                )

                result = create_certificates(
                    self.__zoom_file,
                    self.__webinar_file,
                    create=create,
                )
                if create:
                    self.__json_file = result
                self.terminal.print_message(
                    f". . . Certificate {action_name} finished!"
                )
                if create:
                    if self.__json_file:
                        filename = os.path.basename(self.__json_file)
                        self.__set_file_selected("email_json", self.__json_file)
                        self.__set_file_selected("state_json", self.__json_file)
                        self.terminal.print_message(f"JSON file: {filename} selected.")
                        succeeded = True
                    else:
                        self.terminal.print_message(
                            "Certificate creation failed: No JSON file was created."
                        )
                else:
                    succeeded = True
            except Exception as error:
                self.__log_certificate_error(error)

        page = "create" if create else "verify"
        if self.__zoom_file is None:
            self.__set_file_status(
                f"{page}_zoom",
                "Select a Zoom file",
                "Drop a file here or choose Browse",
            )
        if self.__webinar_file is None:
            self.__set_file_status(
                f"{page}_webinar",
                "Select a webinar file",
                "Drop a file here or choose Browse",
            )
        return succeeded

    def __send_emails(self, *, demo: bool) -> bool:
        if self.__json_file is None:
            self.terminal.print_message("You must select a JSON file!")
            return False

        action_name = "test " if demo else ""
        finished_message = ". . . Test emails sent!" if demo else ". . . Emails sent!"
        try:
            self.terminal.print_message(f"Sending {action_name}emails . . .")
            from certificate_maker.src.data.emails import send_emails

            send_emails(self.__json_file, demo=demo)
            self.terminal.print_message(finished_message)
            return True
        except Exception as error:
            self.terminal.print_message(
                f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{error}`"
            )
            return False

    def __run_state_submission(self) -> bool:
        succeeded = False
        required_files = [
            (self.__json_file, "state_json", "Select a certificate JSON file"),
            (self.__poll_file, "poll", "Select a Zoom poll file"),
            (self.__zoom_survey_file, "zoom_survey", "Select a Zoom survey file"),
            (
                self.__state_attendance_file,
                "state_attendance",
                "Select an attendance sheet",
            ),
        ]
        if all(file_path for file_path, _, _ in required_files):
            assert self.__json_file is not None
            assert self.__poll_file is not None
            assert self.__zoom_survey_file is not None
            assert self.__state_attendance_file is not None
            try:
                self.terminal.print_message(
                    "State submission report generation started . . ."
                )
                from certificate_maker.src.data.state_submission import (
                    create_state_submission_report,
                )

                output_file = create_state_submission_report(
                    self.__json_file,
                    self.__poll_file,
                    self.__zoom_survey_file,
                    self.__state_attendance_file,
                )
                self.terminal.print_message(
                    f". . . State submission report created: {output_file}"
                )
                succeeded = True
            except StateSubmissionFileNotFound as error:
                self.terminal.print_message(
                    f"State Submission File Missing: `{error.args[0]}` was not found."
                )
            except StateSubmissionInvalidJson as error:
                self.terminal.print_message(
                    f"State Submission JSON Error: `{error.args[0]}` is not valid certificate JSON."
                )
            except StateSubmissionMissingData as error:
                self.terminal.print_message(f"State Submission Data Error: `{error}`")
            except StateSubmissionMissingPollData as error:
                self.terminal.print_message(f"State Submission Poll Error: `{error}`")
            except StateSubmissionMissingSurveyData as error:
                self.terminal.print_message(f"State Submission Survey Error: `{error}`")
            except Exception as error:
                self.terminal.print_message(
                    f"Unknown Error: Could not create the state submission report: `{error}`"
                )
        else:
            for file_path, label_key, prompt in required_files:
                if not file_path:
                    self.__set_file_status(
                        label_key,
                        prompt,
                        "Drop a file here or choose Browse",
                    )
        return succeeded

    def __run_on_demand_report(self) -> bool:
        succeeded = False
        if (
            self.__attend_file is not None
            and self.__eval_file is not None
            and self.__on_demand_file is not None
        ):
            try:
                self.terminal.print_message("On-Demand Report generation started . . .")
                from certificate_maker.src.data.on_demand.on_demand import (
                    create_on_demand_report,
                )

                create_on_demand_report(
                    self.__attend_file, self.__eval_file, self.__on_demand_file
                )
                self.terminal.print_message(
                    ". . . On-Demand Report generation finished!"
                )
                succeeded = True
            except MalformedEvaluationQuestionResponse as error:
                self.terminal.print_message(
                    f"Check Evaluation Question Responses: `{error}` has a malformed response to an evaluation question."
                )
            except MalformedCROString as error:
                self.terminal.print_message(
                    f"Check Submitted CRO cell on Submission Report: `{error}` has a CRO string that is not in the format `State: BarNumber - Hours`."
                )
            except IncorrectDateTimeFormat as error:
                self.terminal.print_message(
                    f"Check time format: Failed to parse time information for `{error}`."
                )
            except ReferenceFileMissingSheet as error:
                self.terminal.print_message(
                    f"Check On-Demand Reference File: There is no sheet named `{error.args[0]}` in the reference file."
                )
            except MissingSubmissionData as error:
                self.terminal.print_message(
                    f"Submission Report missing data: `{error.args[0]}` is missing required data for course `{error.args[1]}`."
                )
            except MissingEvaluationData as error:
                self.terminal.print_message(
                    f"Evaluation Report missing data: `{error.args[0]}` is missing required data for course `{error.args[1]}`."
                )
            except ReferenceFileMissingCourse as error:
                self.terminal.print_message(
                    f"Check On-Demand Reference File: There is no course titled `{error.args[0]}` in the reference file for the state of `{error.args[1]}`."
                )
            except Exception as error:
                self.terminal.print_message(
                    f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{error}`"
                )

        if self.__attend_file is None:
            self.__set_file_status(
                "attend",
                "Select a submission file",
                "Drop a file here or choose Browse",
            )
        if self.__eval_file is None:
            self.__set_file_status(
                "eval",
                "Select an evaluation file",
                "Drop a file here or choose Browse",
            )
        if self.__on_demand_file is None:
            self.__set_file_status(
                "on_demand",
                "Select a reference file",
                "Drop a file here or choose Browse",
            )
        return succeeded

    def action_performed(self, text: str, selected_file: str | None = None) -> None:
        """Performs an action given a string.

        Args:
            text: str, string indicator of which action to perform

        Returns:
            None
        """
        succeeded = False
        # File actions update shared state and every tab that displays that file.
        if text == "zoom":
            self.__zoom_file = self.__choose_file(
                "Browse for zoom.csv file", selected_file
            )
            if not self.__zoom_file:
                return
            filename = os.path.basename(self.__zoom_file)
            self.__set_file_selected("create_zoom", self.__zoom_file)
            self.__set_file_selected("verify_zoom", self.__zoom_file)
            self.terminal.print_message(f"Zoom file: {filename} selected.")
        elif text == "webinar":
            self.__webinar_file = self.__choose_file(
                "Browse for webinar.xlsx file", selected_file
            )
            if not self.__webinar_file:
                return
            filename = os.path.basename(self.__webinar_file)
            self.__set_file_selected("create_webinar", self.__webinar_file)
            self.__set_file_selected("verify_webinar", self.__webinar_file)
            self.terminal.print_message(f"CLE file: {filename} selected.")
        # Processing actions validate inputs before calling the data layer.
        elif text == "submit":
            succeeded = self.__run_certificate_action(create=True)
        elif text in {"test_email", "submit_email"}:
            succeeded = self.__send_emails(demo=text == "test_email")
        elif text == "find_json":
            self.__json_file = self.__choose_file("Browse for JSON File", selected_file)
            if not self.__json_file:
                return
            filename = os.path.basename(self.__json_file)
            self.__set_file_selected("email_json", self.__json_file)
            self.__set_file_selected("state_json", self.__json_file)
            self.terminal.print_message(f"JSON file: {filename} selected.")
        elif text == "state_json":
            self.__json_file = self.__select_file(
                "state_json", "Browse for Certificate JSON file", selected_file
            )
        elif text == "poll":
            self.__poll_file = self.__select_file(
                "poll", "Browse for Zoom Poll file", selected_file
            )
        elif text == "zoom_survey":
            self.__zoom_survey_file = self.__select_file(
                "zoom_survey", "Browse for Zoom Survey file", selected_file
            )
        elif text == "state_attendance":
            self.__state_attendance_file = self.__select_file(
                "state_attendance",
                "Browse for Original Attendance Sheet",
                selected_file,
            )
        elif text == "submit-state-submission":
            succeeded = self.__run_state_submission()
        elif text == "verify_files":
            succeeded = self.__run_certificate_action(create=False)
        elif text == "attend-file":
            self.__attend_file = self.__choose_file(
                "Browse for submission.csv file", selected_file
            )
            if not self.__attend_file:
                return
            filename = os.path.basename(self.__attend_file)
            self.__set_file_selected("attend", self.__attend_file)
            self.terminal.print_message(f"Submission file: {filename} selected.")
        elif text == "eval-file":
            self.__eval_file = self.__choose_file(
                "Browse for evaluation.csv file", selected_file
            )
            if not self.__eval_file:
                return
            filename = os.path.basename(self.__eval_file)
            self.__set_file_selected("eval", self.__eval_file)
            self.terminal.print_message(f"Evaluation file: {filename} selected.")
        elif text == "on-demand-file":
            self.__on_demand_file = self.__choose_file(
                "Browse for on-demand-reference.xlsx file", selected_file
            )
            if not self.__on_demand_file:
                return
            filename = os.path.basename(self.__on_demand_file)
            self.__set_file_selected("on_demand", self.__on_demand_file)
            self.terminal.print_message(
                f"On-Demand Reference file: {filename} selected."
            )
        elif text == "submit-on-demand":
            succeeded = self.__run_on_demand_report()

        step_name = self.__submit_step_names.get(text)
        if step_name is not None:
            message = (
                f"{step_name} was successful!"
                if succeeded
                else f"{step_name} failed. See Activity Logs."
            )
            self.__show_status_banner(message, succeeded)

    def browse_for_file(self, title: str) -> str:
        """Open a file picker and return the selected path."""
        return filedialog.askopenfilename(
            title=title,
        )
