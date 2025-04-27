import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import datetime
import re

def setup_driver():
    """Set up and return a Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode, comment this out for debugging
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_website(url):
    """Scrape a single webpage and return its HTML content."""
    driver = setup_driver()
    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for page to load properly
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Page loaded successfully")
        html = driver.page_source
        return html
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
    finally:
        driver.quit()

def scrape_all_job_pages(base_url):
    """Scrape all pages of job listings."""
    driver = setup_driver()
    all_html_content = []
    page_num = 1
    
    try:
        while True:
            # For the first page, use the base_url, for subsequent pages add page parameter
            url = base_url if page_num == 1 else f"{base_url}&page={page_num}"
            print(f"Scraping page {page_num}: {url}")
            driver.get(url)
            
            # Wait for job listings to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card"))
                )
            except TimeoutException:
                print(f"No job listings found on page {page_num}, possibly the last page")
                break
                
            html_content = driver.page_source
            all_html_content.append(html_content)
            
            # Check if there's a next page
            try:
                # Look for pagination next button
                next_buttons = driver.find_elements(By.CSS_SELECTOR, ".pagination li a")
                has_next = False
                
                for btn in next_buttons:
                    if btn.text.strip() == "»" or "Next" in btn.text:
                        has_next = True
                        page_num += 1
                        break
                
                if not has_next:
                    print("No next page button found, reached last page")
                    break
                    
                # Add a small delay to be respectful to the server
                time.sleep(2)
            except NoSuchElementException:
                print("No pagination found, single page only")
                break
        
        return "\n".join(all_html_content)
        
    except Exception as e:
        print(f"Error during pagination: {e}")
        return "\n".join(all_html_content) if all_html_content else ""
    finally:
        driver.quit()

def extract_job_data_from_html(html_content):
    """Extract job data from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []
    
    # Find all job cards
    job_cards = soup.select(".job-card, div[role='listitem']")
    
    for card in job_cards:
        try:
            # Extract job title
            title_element = card.select_one("h3, .job-title, a > strong")
            title = title_element.text.strip() if title_element else "N/A"
            
            # Extract company and location
            location_elements = card.select(".location, span:contains('Gurgaon'), span:contains('Bangalore')")
            locations = [loc.text.strip() for loc in location_elements if loc]
            location = ", ".join(locations) if locations else "N/A"
            
            # Extract years of experience
            years_element = card.select_one("span:contains('Years')")
            years = years_element.text.strip() if years_element else "N/A"
            
            # Extract posted date
            posted_date_element = card.select_one("span:contains('Posted'), span:contains('day ago'), span:contains('today')")
            posted_date = posted_date_element.text.strip() if posted_date_element else "N/A"
            if "Posted" in posted_date:
                posted_date = posted_date.replace("Posted", "").strip()
            
            # Extract link
            link_element = card.select_one("a[href]")
            link = link_element['href'] if link_element else "N/A"
            if link.startswith('/'):
                link = f"https://www.hirist.tech{link}"
            
            # Extract skills/tags
            skills_elements = card.select(".skill, span.tag, .tech-tag")
            skills = [skill.text.strip() for skill in skills_elements if skill]
            
            # Extract company name
            company_element = card.select_one(".company-name, span.company")
            company = company_element.text.strip() if company_element else "N/A"
            
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "experience": years,
                "skills": ", ".join(skills),
                "posted_date": posted_date,
                "link": link,
                "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            jobs.append(job_data)
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            continue
    
    print(f"Extracted {len(jobs)} jobs")
    return jobs

def filter_jobs_by_keywords(jobs, keywords):
    """Filter jobs by specified keywords in title or description."""
    if not keywords:
        return jobs
        
    filtered_jobs = []
    for job in jobs:
        job_text = f"{job['title']} {job.get('skills', '')}".lower()
        if any(keyword.lower() in job_text for keyword in keywords):
            filtered_jobs.append(job)
    
    return filtered_jobs

def filter_jobs_by_date(jobs, hours=24):
    """Filter jobs posted within the specified number of hours."""
    filtered_jobs = []
    
    for job in jobs:
        posted_date = job["posted_date"].lower()
        
        if hours <= 24:
            # Last 24 hours
            if "hour" in posted_date or "today" in posted_date:
                filtered_jobs.append(job)
        elif hours <= 72:
            # Last 3 days
            if "hour" in posted_date or "today" in posted_date or "1 day" in posted_date or "2 day" in posted_date:
                filtered_jobs.append(job)
        else:
            # All jobs
            filtered_jobs.append(job)
    
    return filtered_jobs