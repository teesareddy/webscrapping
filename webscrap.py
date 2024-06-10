import requests  
# Import the requests library for making HTTP requests
from bs4 import BeautifulSoup  
# Import BeautifulSoup for parsing HTML
import pandas as pd  
# Import pandas for data manipulation and analysis
from datetime import datetime  
# Import datetime for working with dates

def extract_data(url:str, week_date:str, xls=False):
    '''
    This function extracts data from a website based on the provided URL and week date.
    
    parameters:
        url: url of the website
        week_date: date of the week to retrieve the results
        xls: True if want to save the results in excel sheet
    returns:
        dataframe of the entire results
        excel sheet of week updates
        week updates urls
    '''
    url = url  
    # Assign the input URL to a variable
    parent_url = 'https://cosmetics.specialchem.com'  
    # Define the parent URL for constructing full URLs
    response = requests.get(url)  
    # Send a GET request to the URL and store the response
    soup = BeautifulSoup(response.content, 'html.parser')  
    # Parse the HTML content using BeautifulSoup

    # Find the total number of pages
    pagination = soup.find('div', class_='products-pagination')  
    # Find the pagination element
    total_pages = 1  
    # Initialize total_pages to 1 as a default

    if pagination:  
        # If pagination element exists
        pages = pagination.find_all('a')  
        # Find all the page links
        if pages:  
            # If there are page links
            total_pages = int(pages[-2].text)  
            # Get the text of the second-to-last page link and convert it to an integer

    data = []  # Initialize an empty list to store the extracted data

    for page_num in range(1, total_pages + 1):  # Iterate over the pages
        page_url = f'{url}?indexpage={page_num}'  # Construct the URL for the current page
        page_response = requests.get(page_url)  # Send a GET request to the current page URL
        page_soup = BeautifulSoup(page_response.content, 'html.parser')  
        # Parse the HTML content of the current page

        headlines = page_soup.find_all(class_='titre float')  
        # Find all the headlines on the current page
        dates = page_soup.find_all(class_='date float dotted_line c5')  
        # Find all the dates on the current page

        headlines_text = [headline.get_text(strip=True) for headline in headlines]  
        # Extract the text from the headlines
        dates_text = [date.get_text(strip=True) for date in dates]  
        # Extract the text from the dates
        urls = [parent_url + headline['href'] for headline in headlines]  
        # Construct the full URLs for the headlines

        data += list(zip(headlines_text, urls, dates_text))  
        # Zip the headlines, URLs, and dates and append to the data list

    df = pd.DataFrame(data, columns=['Headline', 'URL', 'Date'])  
    # Create a pandas DataFrame from the extracted data
    df['Date'] = df['Date'].str.extract(r'([A-Za-z]{3} \d{1,2}, \d{4})')  
    # Extract the date in the format 'MMM DD, YYYY'
    df.dropna(inplace=True)  # Drop any rows with missing values
    df['Date'] = pd.to_datetime(df['Date'], format=r'%b %d, %Y')  
    # Convert the date strings to datetime objects
    week_updates = []  # Initialize an empty list to store the week updates

    weekly_data = df.groupby(pd.Grouper(key='Date', freq='W')).apply(lambda x: list(zip(x['Headline'], x['URL'], x['Date']))).to_dict()  # Group the data by week and convert to a dictionary
    date = pd.to_datetime(week_date)  # Convert the input week date to a datetime object

    for week_start, headlines_urls in weekly_data.items():  
        # Iterate over the weekly data
        week_end = week_start + pd.DateOffset(days=6)  
        # Calculate the end date of the week
        if date >= week_start and date <= week_end: 
             # Check if the input date falls within the current week
            week_updates = headlines_urls 
             # Assign the headlines, URLs, and dates for the current week to week_updates

    if len(week_updates):  # If there are week updates
        if xls:  # If the xls parameter is True
            path = url.split('/')[-1] + " all updates " + datetime.now().strftime(r'%d-%a-%Y') + '.xlsx'  
            # Construct the file path for the Excel sheet
            df['Date'] = df['Date'].dt.strftime(r'%b %d, %Y')  
            # Convert the date column to a string format
            df.to_excel(path, index=False)  
            # Save the entire DataFrame to an Excel sheet
        week_df = pd.DataFrame(week_updates, columns=['Headline', 'URL', 'Date']) 
         # Create a DataFrame for the week updates
        week_df['Date'] = week_df['Date'].dt.strftime(r'%b %d, %Y')  
        # Convert the date column to a string format
        week_df.to_excel(f'{url.split("/")[-1]} week_{week_date}.xlsx', index=False)  
        # Save the week updates to an Excel sheet
        return (df, week_updates) 
     # Return the entire DataFrame and the week updates
    return ([], 'No updates this week')  
# If there are no updates, return an empty list and a message

def weekly_data(df, week_date, xls=False):
    '''
    This function extracts the weekly data from a DataFrame based on the provided week date.
    
    parameters:
        df: dataframe of the imported excel sheet
        week_date: date of the week in the format %Y-%m-%d (2024-01-31)
        xls: True if need to extract data into excel sheet else False
    returns:
        week updates urls
    '''
    df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')  # Convert the date column to datetime objects
    weekly_data = df.groupby(pd.Grouper(key='Date', freq='W')).apply(lambda x: list(zip(x['Headline'], x['URL'], x['Date']))).to_dict()  # Group the data by week and convert to a dictionary
    date = pd.to_datetime(week_date)  # Convert the input week date to a datetime object

    week_updates = []  
    # Initialize an empty list to store the week updates
    for week_start, headlines in weekly_data.items():  
        # Iterate over the weekly data
        week_end = week_start + pd.DateOffset(days=6)  
        # Calculate the end date of the week
        if date >= week_start and date <= week_end: 
             # Check if the input date falls within the current week
            week_updates = headlines 
             # Assign the headlines, URLs, and dates for the current week to week_updates

    if len(week_updates):  # If there are week updates
        if xls:  # If the xls parameter is True
            week_df = pd.DataFrame(week_updates, columns=['Headline', 'URL', 'Date']) 
             # Create a DataFrame for the week updates
            week_df['Date'] = week_df['Date'].dt.strftime(r'%b %d, %Y') 
             # Convert the date column to a string format
            week_df.to_excel(f'week_{week_date}.xlsx', index=False) 
             # Save the week updates to an Excel sheet
        return week_updates  # Return the week updates
    return 'No updates this week'  # If there are no updates, return a message

# Main code
url = 'https://cosmetics.specialchem.com/channel/skin-care'  
# Define the URL for the main code
week_date = input("Enter the week date in the format YYYY-MM-DD: ") 
 # Prompt the user to enter the week date
data, week_data = extract_data(url, week_date, xls=True)  
# Call the extract_data function with the URL, week date, and xls=True
print(week_data)  # Print the week updates
print(data['URL'].head()) 
 # Print the first few URLs from the entire DataFrame

weekly_data(data, week_date) 
 # Call the weekly_data function with the DataFrame and week date