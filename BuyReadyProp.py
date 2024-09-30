import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initialize_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.bayut.com/")
    return driver


def extract_property_data(driver):
    data = {}
    try:
        read_more_button = driver.find_elements(By.CSS_SELECTOR, "div._2b5fcdea[aria-label='View More']")
        if read_more_button:
            read_more_button[0].click()
            time.sleep(1)  # Attendez que les informations supplémentaires soient chargées

        contact_details_buttons = driver.find_elements(By.CSS_SELECTOR, "button.a7f929d9.phoneCTA")
        if contact_details_buttons:
            contact_details_buttons[0].click()
            time.sleep(1)
            try:
                phone_number_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='tel:'] > span[dir='ltr']")
                if phone_number_elements:
                    data['Phone'] = phone_number_elements[0].text.strip()  # Utiliser .strip() pour nettoyer les espaces
                else:
                    data['Phone'] = "N/A"
            except Exception as e:
                print(f"Error retrieving phone number: {e}")
                data['Phone'] = "N/A"
        else:
            data['Phone'] = "N/A"

        data['Price'] = driver.find_element(By.CSS_SELECTOR, "span._2d107f6e").text
        data['Address'] = driver.find_element(By.CSS_SELECTOR, "div.e4fd45f0").text
        data['Beds'] = driver.find_element(By.CSS_SELECTOR, "span._783ab618[aria-label='Beds'] > span").text
        data['Baths'] = driver.find_element(By.CSS_SELECTOR, "span._783ab618[aria-label='Baths'] > span").text
        data['Area'] = driver.find_element(By.CSS_SELECTOR, "span._783ab618[aria-label='Area'] > span").text
        data['URL'] = driver.current_url
        data['Agent Name'] = driver.find_element(By.CSS_SELECTOR, "span._4c376836.undefined").text
    except Exception as e:
        print("Error extracting property data:", e)
    return data


def write_to_csv(data, filename='ayouub.csv'):
    fieldnames = ['Price', 'Address', 'Beds', 'Baths', 'Area', 'Phone', 'Agent Name', 'URL']
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(data)
    except Exception as e:
        print("Error writing to CSV:", e)


def apply_filters(driver):
    wait = WebDriverWait(driver, 30)
    time.sleep(1)
    location_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text'][placeholder='Enter location']")))
    location_input.send_keys("Jumeirah Lake Towers")
    time.sleep(1)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li.bce7b87f[data-selected='true'] button"))).click()

    ready_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button._01214aea:nth-child(2)")))
    ready_button.click()

    category_button = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div[aria-label='Category filter']")))
    category_button.click()

    apartment_option = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li._90e5f992")))
    apartment_option.click()

    search_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a._6219ce30.aaf1e20a")))
    search_button.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[aria-label='TruCheck listings first']"))).click()


def navigate_listings(driver):
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.e20beb46")))  # Wait for the list to be visible

    listings = driver.find_elements(By.CSS_SELECTOR, "ul.e20beb46 > li[role='article']")
    total_listings = len(listings)
    print(f"Found {total_listings} listings.")

    for i in range(total_listings):
        listings = driver.find_elements(By.CSS_SELECTOR, "ul.e20beb46 > li[role='article']")
        if i >= len(listings):
            print("The number of listings has changed, stopping the loop.")
            break

        try:
            listings[i].click()
            time.sleep(1)
            property_data = extract_property_data(driver)
            write_to_csv(property_data)
        except Exception as e:
            print(f"Error clicking on element {i}: {e}")
            continue

        driver.back()
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.e20beb46")))  # Ensure the list is visible again

        if i == total_listings - 1:
            print("Processed all listings.")
            break


def handle_pagination(driver):
    wait = WebDriverWait(driver, 30)

    while True:
        navigate_listings(driver)
        try:
            next_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[title='Next'] > div._948d9e0a.e1afd4c7.b2e0090c._371e9918")))
            next_button.click()
            print("Navigated to the next page.")
            time.sleep(2)
        except Exception as e:
            print("No more pages or next button not found. Error: ", str(e))
            break


driver = initialize_browser()
apply_filters(driver)
handle_pagination(driver)
time.sleep(2)
