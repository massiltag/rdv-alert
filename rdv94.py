"""
Requirements to install with pip3 :
    - selenium
    - chromedriver (Chrome) OR geckodriver (Firefoxs)
    - requests
"""

import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# 1. open url
url = "https://rdv-etrangers-94.interieur.gouv.fr/eAppointmentpref94/element/jsp/specific/pref94.jsp"
driver.get(url)

# 2. enter "94800" in a text box whose id is #CPId
cpid_input = driver.find_element(By.ID, "CPId") #find_element_by_id("CPId")
cpid_input.send_keys("94800")

# 3. click on an input which has type "button" and value "Continuer"
button = driver.find_element(By.CSS_SELECTOR, 'input[type="button"][value="Continuer"]')
button.click()

# 4. wait for next page to load
# You can use WebDriverWait to wait for a specific element to be present on the page
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
except TimeoutError:
    # Dialog was not present, there are appointments
    requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=RDV23-OK")
    pass
else:
    # Dialog was present, switch to it and accept it
    driver.switch_to.alert.accept()



# 8. check if RDVs available
# Check if an element with the name "dayValueId" is present on the webpage
# and is not disabled
'''
elements = driver.find_elements(By.ID, "dayValueId")
if elements and not elements[0].get_attribute("disabled"):
    # Element is present and not disabled, make an HTTP GET call
    print(elements[0])
    requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=RDV23-OK")
else: 
    requests.get("https://smsapi.free-mobile.fr/sendmsg?user=45489845&pass=sFrBFAqzkuZTp0&msg=RDV23-KO")
'''