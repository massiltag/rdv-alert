"""
Requirements to install with pip3 :
    - selenium
    - chromedriver (Chrome) OR geckodriver (Firefox)
    - requests
"""

import time
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
url = "https://rdv-etrangers-94.interieur.gouv.fr/eAppointmentpref94/element/jsp/specific/pref94.jsp"

while True:
    # 1. open url
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
    wait = WebDriverWait(driver, 4)  # waits for 4 seconds
    try:
        dialog = wait.until(EC.alert_is_present())
    except Exception: # TimeoutError
        # Dialog was not present, there are appointments
        requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=RDV23-OK")
        pass
    else:
        # Dialog was present, switch to it and accept it
        driver.switch_to.alert.accept()

    driver.close()
    time.sleep(30)  # pause for x seconds