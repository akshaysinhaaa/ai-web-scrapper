import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service

def scrape_website (website):
    print(f"Launching Chrome browser...")

    chrome_driver_path = ""
    options = webdriver.ChromeOptions() 
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        driver.get(website)
        print("Page Loaded...")
        html = driver.page_source

        return html
    finally:
        driver.quit()