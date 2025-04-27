import streamlit as st
import pandas as pd
import datetime
import os
from scrape import (
    scrape_website,
    scrape_all_job_pages,
    extract_job_data_from_html
)
from parse import parse_with_ollama

st.title('Hirist.tech Job Scraper')

# Default URL for hirist.tech job search with keywords
st.subheader("Job Search Configuration")

# Keywords input for search
search_keyword = st.text_input('Enter search keyword (e.g., django, python)', value='django')

# Keywords to filter by
st.subheader("Additional Keyword Filters")
filter_keywords = st.multiselect(
    'Select additional keywords to filter jobs',
    ['backend', 'django', 'fullstack', 'python', 'node', 'php'],
    default=['python', 'django']
)

# Time filter
st.subheader("Time Filter")
time_filter = st.radio(
    "Filter jobs by time posted",
    ("Last 24 hours", "Last 3 days", "All jobs"),
    index=0
)

if st.button("Scrape Jobs"):
    search_url = f"https://www.hirist.tech/search/{search_keyword}.html?locIds=0&exp=0&range=1"
    st.write(f"Scraping {search_url} for jobs matching: {', '.join(filter_keywords)}...")
    
    with st.spinner("Scraping job listings... this may take a few minutes"):
        # Scrape all pages of job listings
        html_content = scrape_website(search_url)
        
        if html_content:
            # Extract jobs from the HTML
            all_jobs = extract_job_data_from_html(html_content)
            
            # Filter by time (days)
            filtered_jobs = []
            for job in all_jobs:
                posted_time = job["posted_date"].lower()
                
                if time_filter == "Last 24 hours":
                    if "today" in posted_time or "hour" in posted_time:
                        filtered_jobs.append(job)
                elif time_filter == "Last 3 days":
                    if "today" in posted_time or "hour" in posted_time or "1 day" in posted_time or "2 day" in posted_time:
                        filtered_jobs.append(job)
                else:
                    filtered_jobs.append(job)
            
            # Filter by keywords
            if filter_keywords:
                keyword_filtered_jobs = []
                for job in filtered_jobs:
                    job_text = f"{job['title']} {job.get('description', '')}".lower()
                    if any(keyword.lower() in job_text for keyword in filter_keywords):
                        keyword_filtered_jobs.append(job)
                filtered_jobs = keyword_filtered_jobs
            
            # Display results in Streamlit
            st.subheader(f"Found {len(filtered_jobs)} matching jobs")
            
            # Create a DataFrame
            if filtered_jobs:
                df = pd.DataFrame(filtered_jobs)
                st.dataframe(df)
                
                # Export to CSV
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"hirist_jobs_{search_keyword}_{timestamp}.csv"
                df.to_csv(filename, index=False)
                
                # Provide download link
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name=filename,
                        mime="text/csv"
                    )
            else:
                st.write("No jobs matching your criteria were found.")
        else:
            st.error("Failed to scrape the website. Please check your internet connection or try again later.")
