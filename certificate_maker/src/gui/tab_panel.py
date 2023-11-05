"""Class to display loading options.

Author: Zak Oster zcoster@ksu.edu
Version: 0.1
"""
import tkinter as tk
from tkinter import ttk, filedialog

from certificate_maker.src.data.emails import send_emails
from certificate_maker.src.data.certificate import create_certificates
from certificate_maker.src.exception_types import (
    IncorrectWebinarTitle,
    AttorneyMissingBarNumber,
    IncorrectDateTimeFormat,
    MasterListMissingHours,
    MissingStateApproval,
    AttorneyMissingState,
    IncorrectNumberOfBreaks,
    AttorneyInvalidState,
    AttorneyInvalidBarNumber,
    MissingBreakRow,
    MissingStartRow,
    MismatchingStateAndBarNumbers
)


class TabPanel(tk.Frame):
    """Class to display loading options."""

    def __init__(self, master, terminal, set_create_tab=False) -> None:
        """Constructor to initialize the menu panel."""
        self.__master = master
        ttk.Frame.__init__(self, master=self.__master)

        self.__zoom_file = None
        self.__webinar_file = None
        self.__email_folder = "/Users/zakoster/Certificates/Output Certificates" # None
        self.terminal = terminal

        self.__loading_tabs: ttk.Notebook = ttk.Notebook(master=self)
        instructions_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        create_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        email_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)

        self.__loading_tabs.add(instructions_tab, text="Instructions")
        self.__loading_tabs.add(create_tab, text="Create Certificates")
        self.__loading_tabs.add(email_tab, text="Send Emails")
        self.__loading_tabs.pack(expand=1, fill="both")

        instructions_tab.grid_columnconfigure(0, weight=1)
        create_tab.grid_columnconfigure(0, weight=1)
        email_tab.grid_columnconfigure(0, weight=1)

        if set_create_tab:
            self.__loading_tabs.select(create_tab)

        # ----- Create the Instructions Tab -----

        instructions_tab.grid_rowconfigure(0, weight=1)
        instructions_tab.grid_rowconfigure(1, weight=1)
        instructions_tab.grid_rowconfigure(2, weight=1)
        instructions_tab.grid_rowconfigure(3, weight=1)

        # instruction_p1 = (
        #     "Welcome to the CLE Certificate Maker! \n\n"
        #     "To use this program, you will need two different files: \n "
        #     "\t- a Zoom .csv file\n\t- the webinar master list .xlsx file\n\n"
        #     "The master webinar list can be left as is, but the zoom.csv file needs some changes.\n"
        #     "Open up the csv file and insert two rows underneath the title of the webinar.\n"
        #     "In the first cell, type the word `Start` and in the cell beneath it type `Breaks`.\n"
        #     "In the cell next to `Start`, insert the start time and date using the format of:\n"
        #     "\t- month/day/year hour:minute\n\t- 6/23/2023 13:00\n\n"
        #     "Next, in the cell next to `Breaks` enter the number of breaks in the class (0, 1, etc.).\n"
        #     "Now, using the same format as the Start time, enter the start time of the first break \n"
        #     "in the adjacent cell. Then, in the next cell, enter the end time. Continue this process \n"
        #     "for each break."
        # )
        instruction_p1 = "Under construction."
        text1 = tk.Label(
            master=instructions_tab,
            text=instruction_p1,
            font=8,
            wraplength=1000,
            justify="left",
        )
        text1.grid(row=0, column=0, padx=2, pady=2, sticky="NW")

        # ----- Create the Create Tab -----
        create_tab.grid_rowconfigure(0, weight=1)
        create_tab.grid_rowconfigure(1, weight=1)
        create_tab.grid_rowconfigure(2, weight=1)

        create_tab.grid_columnconfigure(0, weight=1, minsize=150)
        create_tab.grid_columnconfigure(1, weight=1, minsize=150)

        zoom_file = tk.Button(
            create_tab,
            font=("Arial", 10),
            text="Browse for Zoom File",
            command=lambda: self.action_performed("zoom"),
            bg="light gray",
            height=5,
            width=20,
        )
        zoom_file.grid(row=0, column=0, padx=2, pady=2)

        self.zoom_label = tk.Label(
            master=create_tab,
            text="No File Selected",
            font=("Arial", 12),
            justify="left",
        )
        self.zoom_label.grid(row=0, column=1, padx=2, pady=2, sticky="W")

        webinar_file = tk.Button(
            create_tab,
            font=("Arial", 10),
            text="Browse for webinar File",
            command=lambda: self.action_performed("webinar"),
            bg="light gray",
            height=5,
            width=20
        )
        webinar_file.grid(row=1, column=0, padx=2, pady=2)

        self.webinar_label = tk.Label(
            master=create_tab,
            text="No File Selected",
            font=("Arial", 12),
            justify="left",
        )
        self.webinar_label.grid(row=1, column=1, padx=2, pady=2, sticky="W")

        submit = tk.Button(
            create_tab,
            font=("Arial", 12),
            text="Submit Files",
            command=lambda: self.action_performed("submit"),
            bg="gray",
            height="5",
            width="70",
            justify="left"
        )
        submit.grid(row=2, columnspan=2, padx=2, pady=2)                                                                                                            


        # ----- Create the Email Tab -----
        email_tab.grid_rowconfigure(0, weight=1)
        email_tab.grid_rowconfigure(1, weight=1)
        email_tab.grid_rowconfigure(2, weight=1)

        email_tab.grid_columnconfigure(0, weight=1)
        email_tab.grid_columnconfigure(1, weight=1)

        email_file = tk.Button(
            email_tab,
            font=("Arial", 10),
            text="Browse for Email Folder",
            command=lambda: self.action_performed("email"),
            bg="light gray",
            height=5,
            width=20
        )
        email_file.grid(row=0, column=0, padx=2, pady=2)

        self.email_label = tk.Label(
            master=email_tab,
            text="No File Selected",
            font=("Arial", 12),
            justify="left",
        )
        self.email_label.grid(row=0, column=1, padx=2, pady=2)

        test_submit = tk.Button(
            email_tab,
            font=("Arial", 10),
            text="Test Send Emails",
            command=lambda: self.action_performed("test_email"),
            bg="light gray",
            height=5,
            width=50
        )
        test_submit.grid(row=1, column=0, columnspan=2, padx=2, pady=2)

        submit = tk.Button(
            email_tab,
            font=("Arial", 10),
            text="Send Emails to Attorneys",
            command=lambda: self.action_performed("submit_email"),
            bg="light gray",
            height=5,
            width=50
        )
        submit.grid(row=2, column=0, columnspan=2, padx=2, pady=2)

    def action_performed(self, text: str) -> None:
        """Performs an action given a string.

        Args:
            text: str, string indicator of which action to perform

        Returns:
            None
        """
        if text == "zoom":
            self.__zoom_file = self.browse_for_file("Browse for zoom.csv file")
            filename = self.__zoom_file.split("/")[-1]
            self.zoom_label.configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"Zoom file: {filename} selected.")
        elif text == "webinar":
            self.__webinar_file = self.browse_for_file("Browse for webinar.xlsx file")
            filename = self.__webinar_file.split("/")[-1]
            self.webinar_label.configure(
                text="{} selected.".format(filename)
            )
            self.terminal.print_message(f"CLE file: {filename} selected.")
        elif text == "submit":
            if self.__zoom_file is not None and self.__webinar_file is not None:
                try:
                    self.terminal.print_message(f"Certificate creation started . . .")
                    create_certificates(self.__zoom_file, self.__webinar_file)
                    self.terminal.print_message(f". . . Certificate creation finished!")
                except IncorrectDateTimeFormat as e:
                    self.terminal.print_message(f"Check time format: Failed to parse time information for `{e}`.")
                except IncorrectNumberOfBreaks as e:
                    self.terminal.print_message(f"Check Breaks: Zoom file asks for `{e}` breaks, but not enough times were given.")
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
                self.zoom_label.configure(text="You must select a file!")
            if self.__webinar_file is None:
                self.webinar_label.configure(text="You must select a file!")
        elif text == "test_email":
            try:
                self.terminal.print_message(f"Sending test emails . . .")
                send_emails(self.__email_folder, demo=True)
                self.terminal.print_message(f". . . Test emails sent!")
            except Exception as e:
                self.terminal.print_message(f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
        elif text == "submit_email":
            try:
                self.terminal.print_message(f"Sending emails . . .")
                send_emails(self.__email_folder, demo=False)
                self.terminal.print_message(f". . . Emails sent!")
            except Exception as e:
                self.terminal.print_message(f"Unknown Error: Email the files and the following error message to Zak so he can add error checks for it in the future: `{e}`")
        elif text == "email":
            self.__email_folder = filedialog.askdirectory(title="Browse for email folder")
            filename = self.__email_folder.split("/")[-1]
            self.email_label.configure(text="{} selected.".format(filename))
            self.terminal.print_message(f"Email folder: {filename} selected.")
        else:
            pass

    def browse_for_file(self, title):
        return filedialog.askopenfilename(
            title=title,
        )

    def reset_labels(self):
        self.__webinar_file = None
        self.__zoom_file = None
        self.webinar_label.configure(text="No File Selected.")
        self.zoom_label.configure(text="No File Selected.")
