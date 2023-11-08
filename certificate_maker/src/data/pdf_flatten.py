import time
from selenium import webdriver
import json
import os

def pdf_flatten(json_filepath):
    # Get the file information for making flatten pdfs
    with open(json_filepath, 'r') as openfile:
        webinar_dict = json.load(openfile)

    foldername = webinar_dict["filepath"]
    save_location = webinar_dict["desiredpath"]

    # Create chrome driver options to automate saving
    chrome_options = webdriver.ChromeOptions()
    settings = {
        "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
    
    prefs = {
        "printing.print_preview_sticky_settings.appState": json.dumps(settings),
        "savefile.default_directory": save_location
    }

    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')
    driver = webdriver.Chrome(options=chrome_options)

    file_locations = [os.path.join(foldername, x) for x in os.listdir(foldername) if x.endswith(".pdf")]

    for file in file_locations:
        driver.get(f"file://{file}")
        time.sleep(2)
        driver.execute_script('window.print();')
        time.sleep(2)
    driver.quit()

    for attendee in webinar_dict["attendees"]:
        os.rename(attendee["filename"], attendee["desiredname"])