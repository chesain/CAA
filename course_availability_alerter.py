import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)


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
        driver.switch_to.frame("TargetContent")

        time.sleep(5)

        # Select the term from the dropdown
        term_dropdown = Select(driver.find_element(By.ID, "CLASS_SRCH_WRK2_STRM$35$"))
        term_dropdown.select_by_value(term_code)
        print("Term selected")

        time.sleep(5)


        # Select the subject from the dropdown
        subject_dropdown = Select(driver.find_element(By.ID, 'SSR_CLSRCH_WRK_SUBJECT_SRCH$0'))
        subject_dropdown.select_by_value(subject_code)
        print("Subject selected")

        time.sleep(5)


        # Select the match dropdown
        match_dropdown = Select(driver.find_element(By.ID, 'SSR_CLSRCH_WRK_SSR_EXACT_MATCH1$1'))
        match_dropdown.select_by_value('E')
        print("Match selected")

        time.sleep(5)
        

        # Enter the class number
        class_number_input = driver.find_element(By.ID, 'SSR_CLSRCH_WRK_CATALOG_NBR$1')
        class_number_input.send_keys(class_number)
        print("Class number entered")
        
        #time.sleep(5)
        
        
        # Submit the search form
        search_button = driver.find_element(By.ID, 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH')  # Replace with the actual ID of the search button
        ActionChains(driver).move_to_element(search_button).click().perform()
        print("Search button clicked")

        time.sleep(5)

        # Wait for the results page to load and display the results
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print("Results loaded")
        
       
        driver.switch_to.default_content()
        
        # Check if the class is available
        table_index = 0
        while True:
            driver.switch_to.frame("TargetContent")
            try:
                print(f"Checking table {table_index}")
                print(f'SSR_CLSRCH_MTG1$scroll${table_index}') 
                results_table = driver.find_element(By.ID, f'SSR_CLSRCH_MTG1$scroll${table_index}')
                rows = results_table.find_elements(By.TAG_NAME, "tr")
                print(results_table.text)
                for row in rows:
                    try:
                        status_image = row.find_element(By.XPATH, ".//img[contains(@src, 'PS_CS_STATUS')]")
                        status_src = status_image.get_attribute("src")
                        status_alt = status_image.get_attribute("alt")
                        
                        print(f"Status image src: {status_src}")
                        print(f"Status image alt: {status_alt}")
                        
                        if "open" in status_src.lower() or "open" in status_alt.lower():
                            print("Class is available")
                            return True
                    except:
                        continue
                
                table_index += 1
            except:
                print("No more tables found")
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

def send_email(receiver_email):
    sender = os.getenv("SENDER_EMAIL")
    receiver = receiver_email
    password = os.getenv("SENDER_PASSWORD")
    subject = "Class Availability Alert"
    body = "The class you were waiting for is now available!"

    print(f"Sender: {sender}")
    print(f"Seder password: {password}")
    # Check if environment variables are set
    if not sender or not receiver or not password:
        print("Error: One or more environment variables are not set.")
        print(f"SENDER_EMAIL: {sender}")
        print(f"RECEIVER_EMAIL: {receiver}")
        print(f"SENDER_PASSWORD: {password}")
        return

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    config = load_config()
    class_number = config["class_number"]
    subject_code = config["subject_code"]
    term_code = config["term_code"]


    load_dotenv()

    if check_class_availability(class_number, subject_code, term_code):
        send_email(config["receiver"])
        print("Email sent")
