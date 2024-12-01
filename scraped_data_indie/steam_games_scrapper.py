import requests
from bs4 import BeautifulSoup
import re
import time


def get_AppData(url):
    """ Fetch HTML content from a given URL.
    
    Parameters:
        url (str): The URL of the webpage to fetch.

    Returns:
        BeautifulSoup object if successful, None otherwise.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError if status is 4xx or 5xx
        return BeautifulSoup(response.text, 'lxml')
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for URL {url}: {e}")
        return None


def find_general_details(soup):
    """Extract general details such as title, description, genre, and tags.

    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.

    Returns:
        tuple: title, description, content, genre, player type, tags list, and release date.
    """
    title = description = content = genre = player = tags_list = release_date = None

    try:
        title = soup.find('div', class_='apphub_AppName').get_text(strip=True)
        description = soup.find('div', class_='game_description_snippet').get_text(strip=True)
        content_div = soup.find('div', class_='shared_game_rating')
        content = content_div.find('p').get_text(strip=True) if content_div else None
        genre = [g.get_text(strip=True) for g in soup.select('div.details_block a')]
        tags_list = [tag.get_text(strip=True) for tag in soup.select('div.glance_tags a')]
        release_date = soup.find('div', class_='date').get_text(strip=True).replace(',', '')
        player = soup.find('a', class_='game_area_details_specs_ctn').find('div', class_='label').get_text(strip=True)
    except AttributeError:
        pass

    return title, description, content, genre, player, tags_list, release_date


def extract_details(div, index):
    """Extract developer or publisher details.
    
    Parameters:
        div (list): List of div elements containing developer/publisher info.
        index (int): Index of the div to extract details from.
    
    Returns:
        tuple: (link, name) if found, else (None, None).
    """
    try:
        detail_div = div[index].find('div', class_='summary column')
        link = detail_div.find('a').get('href')
        name = detail_div.get_text(strip=True)
        return link, name
    except (AttributeError, IndexError):
        return None, None


def fetch_followers(link):
    """Fetch number of followers from a given developer/publisher link.
    
    Parameters:
        link (str): URL of the developer/publisher page.
    
    Returns:
        str: Number of followers or None if not found.
    """
    soup = None
    if not link:
        return None
    try:
        soup = get_AppData(link)
        res = soup.find('div', class_="num_followers").get_text(strip=True).replace(',', '') if soup else None
        return res
    except:
        return None


def find_developer_publisher_details(soup):
    """Extract developer and publisher details, along with follower counts.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.
    
    Returns:
        tuple: Developer and publisher names, and their follower counts.
    """
    developer = publisher = dev_followers = pub_followers = None
    try:
        divs = soup.find_all('div', class_='dev_row')
        dev_link, developer = extract_details(divs, 0)
        pub_link, publisher = extract_details(divs, 1)
        dev_followers = fetch_followers(dev_link)
        pub_followers = fetch_followers(pub_link)
    except Exception as e:
        pass
    return developer, publisher, dev_followers, pub_followers


def find_price(soup):
    """Extract price and discount prices from the game page.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.
    
    Returns:
        tuple: Regular price and list of discount prices.
    """
    price = discount_prices = None
    try:
        price = soup.find('div', class_='game_purchase_price').get_text(strip=True).replace('$', '')
        discount_divs = soup.find_all('div', class_='discount_final_price')
        discount_prices = [dp.get_text(strip=True).replace('$', '') for dp in discount_divs] or None
    except AttributeError:
        pass
    return price, discount_prices


def find_review_count(soup):
    """Extract monthly and all-time review counts and ratings.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.
    
    Returns:
        tuple: Monthly review count, positive review ratio for the month, total review count, positive review ratio for all time.
    """
    month_reviews = positive_review_ratio_month = total_reviews = positive_review_ratio_all_time = None

    review_divs = soup.find_all('span', class_="nonresponsive_hidden responsive_reviewdesc")
        
    try:
        monthly_numbers = re.findall(r'\d{1,3}(?:,\d{3})*', review_divs[0].get_text())
        positive_review_ratio_month = int(monthly_numbers[0].replace(',', ''))
        month_reviews = int(monthly_numbers[1].replace(',', ''))
    except (AttributeError, IndexError, ValueError):
        month_reviews = positive_review_ratio_month = None
        
    try:
        all_time_numbers = re.findall(r'\d{1,3}(?:,\d{3})*', review_divs[1].get_text())
        positive_review_ratio_all_time = int(all_time_numbers[0].replace(',', ''))
        total_reviews = int(all_time_numbers[1].replace(',', ''))
    except (AttributeError, IndexError, ValueError):
        total_reviews = positive_review_ratio_all_time = None

    return month_reviews, positive_review_ratio_month, total_reviews, positive_review_ratio_all_time


def find_media_links(soup):
    """Extract media links, including header image, screenshots, and videos.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.
    
    Returns:
        tuple: Header URL, image URLs, thumbnail URLs, HD video URLs, and 480p video URLs.
    """
    header_url = image_url_list = image_small_url_list = video_urls_hd_list = video_urls_480p_list = None
    try:
        header_url = soup.find('img', class_='game_header_image_full')['src']
        image_url_list = [img['href'] for img in soup.find_all('a', class_='highlight_screenshot_link')]
        image_small_url_list = [img.find('img')['src'] for img in soup.find_all('div', class_='highlight_strip_item highlight_strip_screenshot')]
        video_links = soup.find_all('div', class_='highlight_player_item highlight_movie')
        video_urls_hd_list = [v_link['data-mp4-hd-source'] for v_link in video_links if 'data-mp4-hd-source' in v_link.attrs]
        video_urls_480p_list = [v_link['data-mp4-source'] for v_link in video_links if 'data-mp4-source' in v_link.attrs]
    except (AttributeError, TypeError):
        pass
    return header_url, image_url_list, image_small_url_list, video_urls_hd_list, video_urls_480p_list


def find_requirements(soup):
    """Extract system requirements.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.
    
    Returns:
        list: List of system requirements or None if not found.
    """
    try:
        lines = soup.find('div', class_='sysreq_tabs').get_text(strip=True).split('\n')
        return [item.strip() for item in lines]
    except AttributeError:
        return None


def find_languages(soup):
    """Extract list of supported languages.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML content of the game page.
    
    Returns:
        list: List of supported languages.
    """
    return [td.get_text(strip=True) for td in soup.select("td.ellipsis")]


def extract_data(appid) -> dict:
    """Main function to extract game details based on the appid from Steam."""
    
    time.sleep(1) 
    url = f"https://store.steampowered.com/app/{appid}/"
    soup = get_AppData(url) 
    
    app_id = appid
    title, description, content, genre, player, tags_list, release_date = find_general_details(soup)
    developer, publisher, dev_followers, pub_followers = find_developer_publisher_details(soup) 
    price, discount_prices = find_price(soup)
    month_reviews, pos_ratio_month, total_reviews, pos_ratio_all = find_review_count(soup)
    header_url,image_url_list,image_small_url_list, video_urls_hd_list, video_urls_480p_list = find_media_links(soup)
    sys_reqs = find_requirements(soup)
    languages_list = find_languages(soup)
    
    # Combine all extracted details into a dictionary
    game_data = {
        'App ID': app_id,
        'Title': title,
        'Description': description,
        'Content': content,
        'Genre': genre,
        'Player Type': player,
        'Tags': tags_list,
        'Release Date': release_date,
        'Developer': developer,
        'Publisher': publisher,
        'Dev Followers': dev_followers,
        'Pub Followers': pub_followers,
        'Price': price,
        'Discount Prices': discount_prices,
        'Monthly Reviews': month_reviews,
        'Positive Review Ratio (Monthly)': pos_ratio_month,
        'Total Reviews': total_reviews,
        'Positive Review Ratio (All Time)': pos_ratio_all,
        'Header Image URL': header_url,
        'Image URLs': image_url_list,
        'Image Small URLs': image_small_url_list,
        'HD Video URLs': video_urls_hd_list,
        '480p Video URLs': video_urls_480p_list,
        'System Requirements': sys_reqs,
        'Languages': languages_list
    }

    return game_data
