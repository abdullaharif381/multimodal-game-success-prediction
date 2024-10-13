import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


# Function to get HTML of a Steam page
def get_steam_page(game_id):
    url = f"https://store.steampowered.com/app/{game_id}"
    try:
        response = requests.get(url, timeout=10)  # Timeout after 10 seconds
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.RequestException:
        return None


# Function to parse Steam metadata
def parse_metadata(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract game title (handle None)
    title_element = soup.find("div", class_="apphub_AppName")
    title = title_element.text.strip() if title_element else None

    # Extract developer (handle None)
    developer_element = soup.find("div", class_="dev_row")
    developer = (
        developer_element.find_all("a")[0].text.strip() if developer_element else None
    )

    # Extract genre (handle None and index errors)
    genre_element = soup.find("div", class_="details_block")
    genre_links = genre_element.find_all("a") if genre_element else []
    genre = genre_links[1].text.strip() if len(genre_links) > 1 else None

    # Extract price (handle None and free games)
    try:
        price_element = soup.find("div", class_="game_purchase_price")
        price = price_element.text.strip() if price_element else "Free"
    except:
        price = "Free"

    # Extract release date (handle None)
    release_date_element = soup.find("div", class_="date")
    release_date = release_date_element.text.strip() if release_date_element else None

    return {
        "Title": title,
        "Developer": developer,
        "Genre": genre,
        "Price": price,
        "Release Date": release_date,
    }


# Function to store the data in a DataFrame
def store_data(game_data_list):
    df = pd.DataFrame(game_data_list)
    df.to_csv("steam_games_data.csv", index=False)


# Read game IDs from CSV file where the second column has the game name
def read_game_ids_from_csv(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Filter the rows where the second column (game name) is not empty
    df = df[df.iloc[:, 1].notna()]

    # Get the game IDs from the 15,000th row to the 20,000th row (first column)
    game_ids = df.iloc[15000:20000, 0].astype(str).tolist()
    return game_ids


# Function to scrape metadata for a game ID
def scrape_game_data(game_id):
    html_content = get_steam_page(game_id)
    if html_content:
        game_data = parse_metadata(html_content)
        # Only add game data if none of the important fields are None
        if all([game_data["Title"], game_data["Developer"], game_data["Genre"]]):
            return game_data
    return None


# File path for the CSV containing game IDs and names
csv_file_path = "all_steam_games.csv"

# Read the game IDs from CSV file (15k to 20k rows)
game_ids = read_game_ids_from_csv(csv_file_path)

# List to hold all game metadata
game_data_list = []

# Use ThreadPoolExecutor for concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
    future_to_game = {
        executor.submit(scrape_game_data, game_id): game_id for game_id in game_ids
    }

    for future in as_completed(future_to_game):
        game_data = future.result()
        if game_data:
            game_data_list.append(game_data)

# Store the scraped data in a CSV file
store_data(game_data_list)

print("Scraping completed! Check steam_games_data.csv for results.")
