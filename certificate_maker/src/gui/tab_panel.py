"""Class to display loading options.

Author: Zak Oster zcoster@ksu.edu
Version: 0.1
"""
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk, Image


class TabPanel(tk.Frame):
    """Class to display loading options."""
    def __init__(self, master, set_create_tab=False) -> None:
        """Constructor to initialize the menu panel."""
        self.__master = master
        ttk.Frame.__init__(self, master=self.__master)

        self.__zoom_file = None
        self.__webinar_file = None

        self.__loading_tabs: ttk.Notebook = ttk.Notebook(master=self)
        instructions_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        create_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)
        email_tab: ttk.Frame = ttk.Frame(self.__loading_tabs)

        self.__loading_tabs.add(instructions_tab, text='Instructions')
        self.__loading_tabs.add(create_tab, text='Create Certificates')
        self.__loading_tabs.add(email_tab, text='Send Emails')
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

        instruction_p1 = ("Welcome to the CLE Certificate Maker! \n\n"
                          "To use this program, you will need two different files: \n "
                          "\t- a Zoom .csv file\n\t- the webinar master list .xlsx file\n\n"
                          "The master webinar list can be left as is, but the zoom.csv file needs some changes.\n"
                          "Open up the csv file and insert two rows underneath the title of the webinar.\n"
                          "In the first cell, type the word `Start` and in the cell beneath it type `Breaks`.\n"
                          "In the cell next to `Start`, insert the start time and date using the format of:\n"
                          "\t- month/day/year hour:minute\n\t- 6/23/2023 13:00\n\n"
                          "Next, in the cell next to `Breaks` enter the number of breaks in the class (0, 1, etc.).\n"
                          "Now, using the same format as the Start time, enter the start time of the first break \n"
                          "in the adjacent cell. Then, in the next cell, enter the end time. Continue this process \n"
                          "for each break.")
        text1 = tk.Label(
            master=instructions_tab,
            text=instruction_p1,
            font=8,
            wraplength=1000,
            justify='left')
        text1.grid(row=0, column=0, padx=2, pady=2, sticky='NW')

        image1 = Image.open('certificate_maker/src/static/sample_excel.png')
        width, height = image1.size
        image1 = image1.resize(
            (width//3, height//3))
        sample_excel_image = ImageTk.PhotoImage(image1)
        sample_problem = tk.Label(
            master=instructions_tab,
            image=sample_excel_image)
        sample_problem.image = sample_excel_image
        sample_problem.grid(row=1, column=0, padx=2, pady=2, sticky='NSEW')

        # ----- Create the Create Tab -----
        create_tab.grid_rowconfigure(0, weight=1)
        create_tab.grid_rowconfigure(1, weight=1)
        create_tab.grid_rowconfigure(2, weight=1)

        create_tab.grid_columnconfigure(0, weight=1)
        create_tab.grid_columnconfigure(1, weight=4)

        zoom_file = tk.Button(
            create_tab,
            font=("Arial",10),
            text="Browse for Zoom File",
            command=lambda: self.action_performed('zoom'),
            bg="light gray",
        )
        zoom_file.grid(row=0, column=0, padx=2, pady=30, sticky='NSEW')

        self.zoom_label = tk.Label(
            master=create_tab,
            text="No File Selected",
            font=("Arial",12),
            justify='left')
        self.zoom_label.grid(row=0, column=1, padx=2, pady=2, sticky='W')

        webinar_file = tk.Button(
            create_tab,
            font=("Arial",10),
            text="Browse for webinar File",
            command=lambda: self.action_performed('webinar'),
            bg="light gray",
        )
        webinar_file.grid(row=1, column=0, padx=2, pady=30, sticky='NSEW')

        self.webinar_label = tk.Label(
            master=create_tab,
            text="No File Selected",
            font=("Arial",12),
            justify='left')
        self.webinar_label.grid(row=1, column=1, padx=2, pady=2, sticky='W')

        submit = tk.Button(
            create_tab,
            font=("Arial",12),
            text="Submit Files",
            command=lambda: self.action_performed('submit'),
            bg="gray",
        )
        submit.grid(row=2, columnspan=2, padx=2, pady=30, sticky='NSEW')

        # ----- Create the Email Tab -----
        email_tab.grid_rowconfigure(0, weight=1)
        email_tab.grid_rowconfigure(1, weight=1)

        email_tab.grid_columnconfigure(0, weight=1)
        email_tab.grid_columnconfigure(1, weight=4)

        email_file = tk.Button(
            email_tab,
            font=("Arial",10),
            text="Browse for Zoom File",
            command=lambda: self.action_performed('email'),
            bg="light gray",
        )
        email_file.grid(row=0, column=0, padx=2, pady=30, sticky='NSEW')

        self.email_label = tk.Label(
            master=email_tab,
            text="No File Selected",
            font=("Arial",12),
            justify='left')
        self.email_label.grid(row=0, column=1, padx=2, pady=2, sticky='W')

        submit = tk.Button(
            email_tab,
            font=("Arial",12),
            text="Submit Files",
            command=lambda: self.action_performed('submit_email'),
            bg="gray",
        )
        submit.grid(row=2, columnspan=2, padx=2, pady=30, sticky='NSEW')

    def action_performed(self, text: str) -> None:
        """Performs an action given a string.

        Args:
            text: str, string indicator of which action to perform

        Returns:
            None
        """
        if text == 'zoom':
            self.__zoom_file = self.browse_for_file("Browse for zoom.csv file")
            self.zoom_label.configure(text="{} selected.".format(self.__zoom_file))
        elif text == 'webinar':
            self.__webinar_file = self.browse_for_file("Browse for webinar.xlsx file")
            self.webinar_label.configure(text="{} selected.".format(self.__webinar_file))
        elif text == 'submit':
            print("submit")
        else:
            pass

    def browse_for_file(self, title):
        return filedialog.askopenfilename(
            title=title,
        )
