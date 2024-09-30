import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import re


def initialize_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Edge(options=chrome_options)
    driver.get(
        "https://dubai.dubizzle.com/en/property-for-sale/residential/apartment/?completion_status=completed&sorting=verified_listing_desc&neighborhood=57505")
    return driver


def apply_filters(driver):
    wait = WebDriverWait(driver, 30)

    ready_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='completion-status-button-completed']")))
    ready_button.click()
    time.sleep(1)
    sort_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='sort-button']")))
    sort_button.click()
    time.sleep(1)

    verified_option = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "li[data-testid='sort-option-1']")))
    verified_option.click()
    time.sleep(1)


def navigate_listings(driver):
    url = driver.current_url
    wait = WebDriverWait(driver, 60)
    current_index = 0
    total_listings = 0

    while True:
        driver.get(url)
        wait.until(EC.visibility_of_element_located(
            (By.ID, "listing-card-wrapper")))
        try:
            links = driver.find_elements(By.CSS_SELECTOR, "a[data-testid^='listing-'][href*='/property-for-sale/']")
            if not links or current_index >= len(links):
                print(f"All listings processed. Total: {total_listings}")
                break
            if current_index == 0:
                print(f"Found {len(links)} listings.")

            driver.execute_script("arguments[0].scrollIntoView();", links[current_index])
            links[current_index].click()
            time.sleep(2)
            extract_property_data(driver)

            current_index += 1
            total_listings += 1
            print(f"Processed listing {current_index}/{len(links)}")
        except Exception as e:
            print(f"Error processing listing {current_index + 1}: {str(e)}")
            break


def safe_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def navigate_to_page(driver, start_page):
    current_page = start_page
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[data-testid='page-{current_page}']"))).click()
            print(f"Navigated to page {current_page}.")
            break
        except TimeoutException:
            print(f"Failed to navigate to page {current_page}, trying next page...")
            current_page += 1
            if current_page > 50:  # Assume there are no more than 50 pages
                print("Assuming page does not exist.")
                break

def handle_pagination(driver, start_page):
    navigate_to_page(driver, start_page)
    while True:
        navigate_listings(driver)
        try:
            next_page_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='page-next']:not([disabled])"))
            )
            if next_page_button.get_attribute('aria-disabled') == 'true':
                print("Reached the last page.")
                break
            else:
                print("Next page button is visible and active. Attempting to click...")
                next_page_button.click()
                time.sleep(2)
                print("Navigated to next page.")
        except TimeoutException:
            print("Timed out waiting for the next page button to become available. Assuming end of pages.")
            break
        except NoSuchElementException:
            print("No next page button found. Assuming end of pages.")
            break
        except Exception as e:
            print(f"An error occurred while trying to navigate to the next page: {str(e)}")
            break


def setup_csv():
    with open('continue3.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Price', 'Address', 'Beds', 'Baths', 'Area', 'URL', 'Phone'])


def extract_property_data(driver):
    wait = WebDriverWait(driver, 30)
    data = {}
    try:
        data['Price'] = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.mui-style-1qcnehy"))).text
        data['Address'] = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.mui-style-uq2ei[data-testid='location-information']"))).text
        data['Beds'] = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.mui-style-vhs5k[data-testid='bed_space']"))).text
        data['Baths'] = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.mui-style-vhs5k[data-testid='bath']"))).text
        data['Area'] = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.mui-style-vhs5k[data-testid='sqft']"))).text
        data['URL'] = driver.current_url

        try:
            read_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='read-more']")))
            read_more_button.click()
        except TimeoutException:
            print("No 'Read More' button found.")

        try:
            show_number_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                        "button.MuiButtonBase-root.MuiButton-root.MuiButton-text.MuiButton-textPrimary.MuiButton-sizeMedium.MuiButton-textSizeMedium.mui-style-11g0oxc")))
            show_number_button.click()

            description_text = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.mui-style-1ddiinb"))).text

            phone_match = re.search(r"\+971\s*\d{1,3}\s*\d{1,3}\s*\d{1,3}", description_text)
            if phone_match:
                data['Phone'] = phone_match.group().replace(" ", "")  # Formate le numéro sans espaces
            else:
                data['Phone'] = "N/A"

        except TimeoutException:
            # Gestion du cas où le bouton "Show Number" n'existe pas
            print("No 'Show Number' button available.")
            data['Phone'] = "N/A"

        with open('continue3.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([data['Price'], data['Address'], data['Beds'], data['Baths'], data['Area'], data['URL'], data['Phone'] ])
    except Exception as e:
        print(f"Failed to extract or write data: {str(e)}")
    return data


driver = initialize_browser()
apply_filters(driver)
handle_pagination(driver, start_page=15)
time.sleep(2)
driver.quit()
