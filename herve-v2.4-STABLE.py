"""
Requirements to install with pip3 :
    - selenium
    - chromedriver (Chrome) OR geckodriver (Firefox)
    - requests
"""

"""
CHANGELOG

Version 2.4:
    - Added feature: Retrieving availability days and sending them as an additional notification

Version 2.3:
    - Fixed bug: Where it could notify even with no appointments available,
      test is now based on "dayValueId" and no longer on "hourValueSelect"
    - Fixed bug: Where driver does not close after exception
    - Refactored code: Notification call is now in an "alert" function

Version 2.2:
    - Added feature: Custom exception handling for DialogBox events
    - Fixed bug: Notifies when popup is detected

Version 2.1:
    - Added feature: Automatically creates a 'screens' folder for screenshots if it doesn't exist.

Version 2.0:
    - Added feature: Search by day and month.
    - Added feature: Save a screenshot of available dates.
    - Added feature: Headless mode.
    - Improved: Error handling.
    
Version 1.0:
    - Initial version: Scraping and notifying when appointments are available.
"""

import time
import requests
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://rdv-etrangers-94.interieur.gouv.fr/eAppointmentpref94/element/jsp/specific/pref94.jsp"

# Arguments
headless = 1
search_month = "Décembre"
search_day = "15"
screenshots_folder = 'screenshots'


def main():
    # Declare options
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')  # Run Chrome in headless mode

    create_folder_if_not_exists(screenshots_folder)

    while True:
        try:
            # 1. open url
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # 2. enter "94800" in a text box whose id is #CPId
            cpid_input = driver.find_element(By.ID, "CPId") # find_element_by_id("CPId")
            cpid_input.send_keys("94800")

            # 3. click on an input which has type "button" and value "Continuer"
            button = driver.find_element(By.CSS_SELECTOR, 'input[type="button"][value="Continuer"]')
            button.click()

            # 4. wait for next page to load
            # You can use WebDriverWait to wait for a specific element to be present on the page
            wait = WebDriverWait(driver, 5)  # waits for 5 seconds
            wait.until(EC.presence_of_element_located((By.NAME, "selectedMotiveKeyList")))

            # 5. check the "Retrait de titre" checkbox
            selected_motive_input = driver.find_element(By.CSS_SELECTOR, 'input[name="selectedMotiveKeyList"][value="20"]')
            selected_motive_input.click()

            # 6. click on the button whose id is "nextButtonId"
            # Wait for it to be available
            wait = WebDriverWait(driver, 3)  # waits for 3 seconds
            wait.until(EC.presence_of_element_located((By.ID, "nextButtonId")))

            # Click on it
            next_button = driver.find_element(By.ID, "nextButtonId")
            next_button.click()

            # 7. accept dialog box if present
            # Wait for the dialog to be present on the page
            wait = WebDriverWait(driver, 5)  # waits for 5 seconds
            try:
                dialog = wait.until(EC.alert_is_present())
            except Exception: # TimeoutError
                pass
            else:
                driver.switch_to.alert.accept()
                raise DialogBoxException("Popup detected, no appointments.") 

            # 8. Check if dayValueId is displayed and enabled
            time.sleep(3)  # waits for x seconds
            if driver.find_element(By.ID, 'dayValueId').is_displayed() and driver.find_element(By.ID, 'dayValueId').is_enabled():
                # Select is enabled, there are appointments, notify and save screenshot
                alert("RDV24-OK")
                driver.save_screenshot(screenshots_folder + "/form-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + '.png')

                # 9. Check for specific conditions in the datepicker groups
                wait = WebDriverWait(driver, 3)  # waits for 3 seconds
                try:
                    # Wait for at least one div with class "ui-datepicker-group" to be present on the page
                    datepicker_groups = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-datepicker-group")))

                    # Save screenshots of available dates
                    driver.save_screenshot(screenshots_folder + "/dates-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + '.png')

                    appointment_days = ""
                    # Check conditions in each datepicker group
                    for datepicker_group in datepicker_groups:
                        # Check if there is a span with class "ui-datepicker-month" and inner text search_month
                        month_span = datepicker_group.find_element(By.CLASS_NAME, "ui-datepicker-month")
                        # Extract all available days in each month and store them in a string
                        a_elements = datepicker_group.find_elements(By.XPATH,'.//td[@class=" undefined"]//a')
                        if len(a_elements):
                            appointment_days += month_span.text +  " : " + ' '.join([a_element.get_attribute("innerHTML") for a_element in a_elements]) + "\n"
                        
                        if month_span.text == search_month:
                            # Check if there is a td with class "undefined" that contains an 'a' with innerText '15'
                            td_element = datepicker_group.find_element(By.XPATH, './/td[@class=" undefined"]//a[text()="' + search_day + '"]')
                            if td_element:
                                # Found the conditions, trigger the alert and break the loop
                                alert(appointment_days)
                                alert("RDV " + search_day + " " + search_month + "OK")
                                break
                except Exception:
                    alert(appointment_days)
                    print('Day Not found')
                    pass
                pass
            else:
                # Select is disabled, no appointments
                print('No RDV found')

            driver.close()
            time.sleep(30)  # pause for x seconds
        except DialogBoxException as e:
            print(f"{e}")
            driver.close()
            time.sleep(30)
        except Exception as e:
            # Print the exception
            print(f"An error occurred: {e}")

            # Wait for a certain amount of time before retrying
            print("Restarting in 5 seconds...")
            driver.close()
            time.sleep(5)


def create_folder_if_not_exists(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        # If it doesn't exist, create it
        os.makedirs(folder_path)
        print(f"Creating folder '{folder_path}'.")


def alert(message):
    requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=" + message)


class DialogBoxException(Exception):
    "Raised when a dialog box is detected"
    pass


if __name__ == "__main__":
    main()
