import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to get HTML of a Steam page
def get_steam_page(game_id):
    url = f"https://store.steampowered.com/app/{game_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Function to parse Steam metadata
def parse_metadata(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract game title
    title = soup.find('div', class_='apphub_AppName').text.strip()
    
    # Extract developer
    developer = soup.find('div', class_='dev_row').find_all('a')[0].text.strip()
    
    # Extract genre
    genre = soup.find('div', class_='details_block').find_all('a')[1].text.strip()
    
    # Extract price
    try:
        price = soup.find('div', class_='game_purchase_price').text.strip()
    except:
        price = "Free"  # Some games are free
    
    # Extract release date
    release_date = soup.find('div', class_='date').text.strip()
    
    return {
        "Title": title,
        "Developer": developer,
        "Genre": genre,
        "Price": price,
        "Release Date": release_date
    }

# Function to store the data in a DataFrame
def store_data(game_data_list):
    df = pd.DataFrame(game_data_list)
    df.to_csv('steam_games_data.csv', index=False)

# Example game IDs to scrape (you can add more)
game_ids = ['730', '578080', '252490']  # CS:GO, PUBG, Rust (as examples)

# List to hold all game metadata
game_data_list = []

# Loop through game IDs and scrape data
for game_id in game_ids:
    html_content = get_steam_page(game_id)
    if html_content:
        game_data = parse_metadata(html_content)
        game_data_list.append(game_data)

# Store the scraped data in a CSV file
store_data(game_data_list)

print("Scraping completed! Check steam_games_data.csv for results.")
