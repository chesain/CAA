import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import yagmail

def check_class_availability(class_number, subject_code, term_code):
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)

    try:
        # Go to the class search page
        driver.get("https://access.myzou.missouri.edu/psp/prdpa/EMPLOYEE/SA/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?&AITS_HDR_CODE=2")
        print(driver.title)
        
        # Wait for the select dropdown to be present
        # WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'SSR_CLSRCH_WRK_SUBJECT_SRCH$0')))
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print("Page loaded")

        # Select the term from the dropdown
        term_dropdown = Select(driver.find_element(By.ID, 'CLASS_SRCH_WRK2_STRM$35$'))
        term_dropdown.select_by_value(term_code)
        print("Term selected")

        # Select the subject from the dropdown
        subject_dropdown = Select(driver.find_element(By.ID, 'SSR_CLSRCH_WRK_SUBJECT_SRCH$0'))
        subject_dropdown.select_by_value(subject_code)
        print("Subject selected")

        # Select the match dropdown
        match_dropdown = Select(driver.find_element(By.ID, 'SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1'))
        match_dropdown.select_by_value('E')
        print("Match selected")

        # Enter the class number
        class_number_input = driver.find_element(By.ID, 'SSR_CLSRCH_WRK_CATALOG_NBR$1')
        class_number_input.send_keys(class_number)
        print("Class number entered")

        # Submit the search form
        search_button = driver.find_element(By.ID, 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH')
        search_button.click()
        print("Search button clicked")

        # Wait for the results page to load and display the results
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'SSR_CLSRCH_MTG1$scroll$0')))
        print("Results loaded")

        # Check if the class is available
        table_index = 0
        while True:
            try:
                results_table = driver.find_element(By.ID, f'SSR_CLSRCH_MTG1$scroll${table_index}')
                if "Open" in results_table.text:
                    return True
                table_index += 1
            except:
                # Break the loop if no more tables are found
                break

        return False

    except Exception as e:
        print(f"Error checking class availability: {e}")
        # Print page source for debugging
        
        # Take a screenshot for visual debugging
        driver.save_screenshot('debug_screenshot.png')
        return False
    finally:
        driver.quit()

def send_email():
    receiver = os.getenv("cvcrx@umsystem.edu")
    body = "The class you were waiting for is now available!"
    
    yag = yagmail.SMTP(os.getenv("*********"), os.getenv("*********"))
    yag.send(
        to=receiver,
        subject="Class Availability Alert",
        contents=body,
    )

if __name__ == "__main__":
    # Replace with the specific class number and subject code you want to check
    class_number = "4850"
    subject_code = "CMP_SC"  # This should be the value attribute of the <option> tag

    if check_class_availability(class_number, subject_code, "5243"):
        send_email()
