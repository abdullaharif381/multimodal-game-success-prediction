from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Define the path to your ChromeDriver
chrome_driver_path = (
    r"C:\Users\Dell\Desktop\Selinium\chromedriver-win64\chromedriver.exe"
)

# Set up Chrome options (if needed)
options = Options()
options.add_argument("--start-maximized")  # Start browser maximized

# Set up the ChromeDriver service
service = Service(chrome_driver_path)

# Initialize the WebDriver with the service and options
driver = webdriver.Chrome(service=service, options=options)

# Open the specific game's URL (Street Fighter 6)
driver.get("https://store.steampowered.com/app/1364780/Street_Fighter_6/")

# Give some time for the page to load
time.sleep(5)

# Extract the "Recent Reviews" and "All Reviews" sections using appropriate locators
recent_reviews = driver.find_element(
    By.CSS_SELECTOR, ".game_review_summary[data-tooltip-text*='Recent Reviews']"
).text
overall_reviews = driver.find_element(
    By.CSS_SELECTOR, ".game_review_summary[data-tooltip-text*='All Reviews']"
).text

# Close the WebDriver
driver.quit()

# Create a pandas DataFrame to save the scraped data
data = {"Recent Reviews": [recent_reviews], "Overall Reviews": [overall_reviews]}

df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
csv_file_path = "steam_reviews.csv"
df.to_csv(csv_file_path, index=False)

print(f"Data saved to {csv_file_path}")
