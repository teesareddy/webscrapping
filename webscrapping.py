import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import webbrowser
from urllib.parse import urljoin

url = "https://cosmetics.specialchem.com/channel/sun-care"

try:
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for non-2xx status codes

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Prompt the user for input
    print("Enter the keywords to search for in the link text (separated by commas):")
    link_text_keywords = [keyword.strip().lower() for keyword in input().split(",")]

    # Find all the hyperlinks
    links = soup.find_all("a")

    # Extract the text, link, and latest updated date for each hyperlink that matches the user's requirements
    link_text = []
    link_urls = []
    updated_dates = []
    for link in links:
        if link.get("href"):
            link_content = link.text.strip().lower()
            if all(keyword in link_content for keyword in link_text_keywords):
                link_text.append(link.text.strip())
                link_url = link.get("href")
                full_link_url = urljoin(url, link_url)
                link_urls.append(full_link_url)
                
                # Find the latest updated date for the link
                updated_date_element = link.find_previous("span", {"class": "updated-date"})
                if updated_date_element:
                    updated_date = updated_date_element.text.strip()
                else:
                    updated_date = "N/A"
                updated_dates.append(updated_date)

    # Create a pandas DataFrame to store the link text, URLs, and updated dates
    df = pd.DataFrame({"Link Text": link_text, "Link URL": link_urls, "Updated Date": updated_dates})

    # Write the DataFrame to an Excel sheet
    df.to_excel("filtered_links_and_text.xlsx", index=False)
    print("Data saved to 'filtered_links_and_text.xlsx'")

    # Open the Excel sheet
    webbrowser.open("filtered_links_and_text.xlsx")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Add a delay to avoid overwhelming the website
    time.sleep(2)