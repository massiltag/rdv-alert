"""
Requirements to install with pip3 :
    - selenium
    - chromedriver (Chrome) OR geckodriver (Firefox)
    - requests
"""

import time
import requests
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://rdv-etrangers-94.interieur.gouv.fr/eAppointmentpref94/element/jsp/specific/pref94.jsp"

# Arguments
headless = 0
search_month = "Décembre"
search_day = "15"

options = webdriver.ChromeOptions()

if (headless):
    options.add_argument('--headless')  # Run Chrome in headless mode

while True:
    # 1. open url
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # 2. enter "94800" in a text box whose id is #CPId
    cpid_input = driver.find_element(By.ID, "CPId") #find_element_by_id("CPId")
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
    driver.save_screenshot("screens/rdv-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + '.png')
    wait = WebDriverWait(driver, 5)  # waits for 5 seconds
    try:
        dialog = wait.until(EC.alert_is_present())
    except Exception: # TimeoutError
        # Dialog was not present, there are appointments
        requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=RDV23-OK")

        # 8. Check for specific conditions in the datepicker groups
        wait = WebDriverWait(driver, 2)  # waits for 2 seconds
        try:
            # Wait for at least one div with class "ui-datepicker-group" to be present on the page
            datepicker_groups = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ui-datepicker-group")))
        
            # Check conditions in each datepicker group
            for datepicker_group in datepicker_groups:
                # Check if there is a span with class "ui-datepicker-month" and inner text search_month
                month_span = datepicker_group.find_element(By.CLASS_NAME, "ui-datepicker-month")
                if month_span.text == search_month:
                    # Check if there is a td with class "undefined" that contains an 'a' with innerText '15'
                    td_element = datepicker_group.find_element(By.XPATH, './/td[@class=" undefined"]//a[text()="' + 15 + '"]')
                    if td_element:
                        # Found the conditions, trigger the alert and break the loop
                        requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=RDV-15-DEC-OK")
                        break
        except Exception as e:
            print('15 Not found')
            pass
        pass
    else:
        # Dialog was present, switch to it and accept it
        print('No RDV found')
        driver.switch_to.alert.accept()

    driver.close()
    time.sleep(30)  # pause for x seconds

