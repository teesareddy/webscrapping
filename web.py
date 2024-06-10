import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def extract_data(url:str, week_date:str, xls=False):
    '''
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
    parent_url = 'https://cosmetics.specialchem.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the total number of pages
    pagination = soup.find('div', class_='products-pagination')
    total_pages = 1

    if pagination:
        pages = pagination.find_all('a')
        if pages:
            total_pages = int(pages[-2].text)

    data = []

    for page_num in range(1, total_pages + 1):
        page_url = f'{url}?indexpage={page_num}'
        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.content, 'html.parser')

        headlines = page_soup.find_all(class_='titre float')
        dates = page_soup.find_all(class_='date float dotted_line c5')

        headlines_text = [headline.get_text(strip=True) for headline in headlines]
        dates_text = [date.get_text(strip=True) for date in dates]
        urls = [parent_url + headline['href'] for headline in headlines]

        data += list(zip(headlines_text, urls, dates_text))

    df = pd.DataFrame(data, columns=['Headline', 'URL', 'Date'])
    df['Date'] = df['Date'].str.extract(r'([A-Za-z]{3} \d{1,2}, \d{4})')
    df.dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format=r'%b %d, %Y')
    week_updates = []

    weekly_data = df.groupby(pd.Grouper(key='Date', freq='W')).apply(lambda x: list(zip(x['Headline'], x['URL'], x['Date']))).to_dict()
    date = pd.to_datetime(week_date)

    for week_start, headlines_urls in weekly_data.items():
        week_end = week_start + pd.DateOffset(days=6)
        if date >= week_start and date <= week_end:
            week_updates = headlines_urls

    if len(week_updates):
        if xls:
            path = url.split('/')[-1] + " all updates " + datetime.now().strftime(r'%d-%a-%Y') + '.xlsx'
            df['Date'] = df['Date'].dt.strftime(r'%b %d, %Y')
            df.to_excel(path, index=False)
        week_df = pd.DataFrame(week_updates, columns=['Headline', 'URL', 'Date'])
        week_df['Date'] = week_df['Date'].dt.strftime(r'%b %d, %Y')
        week_df.to_excel(f'{url.split("/")[-1]} week_{week_date}.xlsx', index=False)
        return (df, week_updates)
    return ([], 'No updates this week')

def weekly_data(df, week_date, xls=False):
    '''
    parameters:
        df: dataframe of the imported excel sheet
        week_date: date of the week in the format %Y-%m-%d (2024-01-31)
        xls: True if need to extract data into excel sheet else False
    returns:
        week updates urls
    '''
    df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')
    weekly_data = df.groupby(pd.Grouper(key='Date', freq='W')).apply(lambda x: list(zip(x['Headline'], x['URL'], x['Date']))).to_dict()
    date = pd.to_datetime(week_date)

    week_updates = []
    for week_start, headlines in weekly_data.items():
        week_end = week_start + pd.DateOffset(days=6)
        if date >= week_start and date <= week_end:
            week_updates = headlines

    if len(week_updates):
        if xls:
            week_df = pd.DataFrame(week_updates, columns=['Headline', 'URL', 'Date'])
            week_df['Date'] = week_df['Date'].dt.strftime(r'%b %d, %Y')
            week_df.to_excel(f'week_{week_date}.xlsx', index=False)
        return week_updates
    return 'No updates this week'

# Main code
data, week_data = extract_data('https://cosmetics.specialchem.com/channel/sun-care', '2024-04-05', xls=True)
print(week_data)
print(data['URL'].head())

weekly_data(data, '2024-05-05')