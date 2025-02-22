from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time


# Function to initialize the WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return None

    return driver


# Function to scrape the disease list from NHS Inform A-to-Z page
def get_disease_list(driver, url):
    driver.get(url)
    time.sleep(5)  # Allow page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all disease links within <ul class="nhsuk-list nhsuk-list--border">
    disease_elements = soup.select('ul.nhsuk-list.nhsuk-list--border li a')
    diseases = [element.get_text(strip=True) for element in disease_elements]
    return diseases


# Function to scrape symptoms from the Mayo Clinic website for a given disease
def scrape_symptoms_mayo(driver, disease_name):
    search_url = f"https://www.mayoclinic.org/search/search-results?q={disease_name}"
    driver.get(search_url)
    time.sleep(5)  # Allow the page to load

    try:
        # Locate the first relevant link and navigate to it
        links = driver.find_elements(By.CSS_SELECTOR, 'a.azsearchlink')  # Updated to use By.CSS_SELECTOR
        for link in links:
            if "symptoms" in link.text.lower():
                link.click()
                time.sleep(5)
                break
        else:
            print(f"No relevant symptoms link found for {disease_name}")
            return []

        # Parse the symptoms page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        symptoms_section = soup.find('h2', string='Symptoms')
        if symptoms_section:
            symptoms_list = symptoms_section.find_next_sibling('ul')
            if symptoms_list:
                symptoms = [li.get_text(strip=True) for li in symptoms_list.find_all('li')]
                return symptoms
    except Exception as e:
        print(f"Error scraping symptoms for {disease_name}: {e}")
    
    return []


# Main script
driver = init_driver()

if driver:
    # Initialize a list to store the data
    data = []

    # Step 1: Define the base URL of the NHS A-Z conditions page
    nhs_url = "https://www.nhs.uk/conditions/"
    
    # Step 2: Get the list of diseases
    print("Scraping disease names from NHS...")
    disease_list = get_disease_list(driver, nhs_url)
    
    print(f"Found {len(disease_list)} diseases.")
    
    # Step 3: Loop through each disease and scrape symptoms from Mayo Clinic
    for disease_name in disease_list:
        print(f"Processing disease: {disease_name}")
        
        symptoms = scrape_symptoms_mayo(driver, disease_name)
        if symptoms:
            print(f"Symptoms for {disease_name}:")
            for symptom in symptoms:
                print(f" - {symptom}")
                data.append({'disease': disease_name, 'type': 'symptom', 'content': symptom})
        else:
            print(f"No symptoms found for {disease_name}.")
        time.sleep(1)  # Add delay to avoid overwhelming the server

    # Close the WebDriver
    driver.quit()

    # Step 4: Save disease names and symptoms to a CSV
    df = pd.DataFrame(data)
    df.to_csv('nhs_diseases_and_symptoms.csv', index=False, encoding='utf-8')

    print("Scraping completed and data saved to nhs_diseases_and_symptoms.csv")
else:
    print("Failed to initialize the WebDriver. Exiting the script.")
