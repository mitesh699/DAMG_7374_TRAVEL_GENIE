import os
import csv
import re
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time
import random


# Function to extract city name from the webpage
def extract_city_name(sb):
    try:
        # Find the city name from the page's header element
        # div_element = sb.find_element(By.CLASS_NAME, "f k O Cj Pf PN Ps PA")
        # child_element = div_element.find_element(By.XPATH, "./*")
        # Find the parent div element that contains the breadcrumbs
        # div_element = sb.find_element(By.CLASS_NAME, "f k O Cj Pf PN Ps PA")

        # Locate the third div for Boston city using XPath
        child_element = sb.find_element(By.XPATH, '//*[@id="lithium-root"]/main/div[1]/div[1]/div/div/div[3]/a')

        # Extract the text for the Boston city link
        # city_name = child_element.find_element(By.XPATH, ".//a/span/span").text
        city_name = child_element.text.strip()
        print(city_name)
        return city_name

    except NoSuchElementException:
        return "N/A"


# Function to extract city ID from the URL
def extract_city_id(url):
    match = re.search(r'-g(\d+)-', url)
    if match:
        city_id = match.group(1)
        return city_id
    return 'N/A'


def extract_location_name(url):
    # Extract location name from the URL (between the last two dashes)
    match = re.search(r'-Reviews-(.*?)-', url)
    if match:
        location_name = match.group(1).replace('_', ' ').strip()
        print(location_name)
        return location_name
    return 'N/A'


def extract_location_id(url):
    # Extract location ID from the URL
    match = re.search(r'-d(\d+)-', url)
    if match:
        location_id = match.group(1)
        return location_id
    return 'N/A'


# Function to save reviews to CSV file
def save_reviews_to_csv(reviews, location_id=None, location_name=None, city_name=None, city_id=None, file_mode='a'):
    # Create 'reviews' folder if it doesn't exist
    if not os.path.exists('dmg7374/reviews'):
        os.makedirs('dmg7374/reviews')

    # Define the path to save the CSV file (with the city name)
    file_path = os.path.join('dmg7374/reviews', 'attractions_reviews.csv')

    # Define the CSV headers
    headers = ['City ID', 'City Name', 'Attraction ID', 'Attraction Name', 'Review ID', 'Review Link', 'Review Title',
               'Ratings Score',
               'Review Date', 'Review Body', 'Username', 'Username Link']

    # Append reviews to CSV after each page
    with open(file_path, file_mode, newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        # Write header only once
        if file_mode == 'w':
            writer.writeheader()

        for review in reviews:
            writer.writerow({
                'City ID': city_id,
                'City Name': city_name,
                'Attraction ID': location_id,
                'Attraction Name': location_name,
                'Review ID': review.get('review_id'),
                'Review Link': review['review_link_href'],
                'Review Title': review['review_title'],
                'Ratings Score': review['rating_score'],
                'Review Date': review['review_date'],
                'Review Body': review['review_body'],
                'Username': review['username'],
                'Username Link': review['username_link'],
            })
    print(f"Reviews saved to {file_path} (mode: {file_mode})")


# Function to extract reviews for a given URL
def extract_reviews(url, rating=1, limit=100):
    reviews_data = []
    count = 0

    filter_button = 'span:contains("Filters")'
    rating_button = f".qgcDG > div:nth-child(2) > div > button:nth-of-type({rating})"
    apply_button = 'span:contains("Apply")'

    with SB(uc=True, demo=True, incognito=True, locale_code="en") as sb:
        sb.uc_open_with_reconnect(url, 4)

        # Extract city name and city id
        city_name = extract_city_name(sb)
        city_id = extract_city_id(url)

        location_name = extract_location_name(url)  # Extract location name from URL
        location_id = extract_location_id(url)

        # Filtering by rating
        sb.uc_click(filter_button, reconnect_time=2)
        sb.uc_click(rating_button, reconnect_time=2)
        sb.uc_click(apply_button, reconnect_time=2)
        time.sleep(random.uniform(3, 6))

        while count < limit:
            get_reviews = sb.find_element(By.CLASS_NAME, "LbPSX")
            get_each_review_child = get_reviews.find_elements(By.CLASS_NAME, "_c")
            page_reviews = []

            for element in get_each_review_child:
                review_data = {}

                try:
                    review_data['rating_score'] = rating
                    review_link = element.find_element(By.CSS_SELECTOR, ".biGQs._P.fiohW.qWPrE.ncFvv.fOtGX")
                    review_data['review_link_href'] = review_link.find_element(By.XPATH, "./*").get_attribute("href")
                    review_data['review_title'] = review_link.find_element(By.XPATH, "./*").text
                except NoSuchElementException:
                    review_data['review_link_href'] = "N/A"
                    review_data['review_title'] = "N/A"

                # Extract review_id from the review URL
                try:
                    review_id_match = re.search(r"-r(\d+)-", review_data.get('review_link_href', ''))
                    review_data['review_id'] = review_id_match.group(1) if review_id_match else "N/A"
                except Exception:
                    review_data['review_id'] = "N/A"

                try:
                    review_data['review_date'] = element.find_element(By.CLASS_NAME, "RpeCd").text.strip().split('•')[
                        0].strip()
                except NoSuchElementException:
                    review_data['review_date'] = "N/A"

                try:
                    username_entities = element.find_element(By.CSS_SELECTOR, ".biGQs._P.fiohW.fOtGX")
                    review_data['username'] = username_entities.text
                    review_data['username_link'] = username_entities.find_element(By.CSS_SELECTOR,
                                                                                  ".BMQDV._F.Gv.wSSLS.SwZTJ.FGwzt.ukgoS").get_attribute(
                        "href")
                except NoSuchElementException:
                    review_data['username'] = "N/A"
                    review_data['username_link'] = "N/A"

                try:
                    review_data['review_body'] = element.find_element(By.CLASS_NAME, "JguWG").text.strip()
                except NoSuchElementException:
                    review_data['review_body'] = "N/A"

                page_reviews.append(review_data)
                count += 1

                if count >= limit:
                    break

            # Save the reviews for the current page before moving to the next one
            if page_reviews:
                save_reviews_to_csv(page_reviews, location_id, location_name, city_id, city_name, file_mode='a')

            if count >= limit:
                break

            try:
                # Pagination Logic
                next_button_divs = sb.find_elements(By.CLASS_NAME, "xkSty")
                next_button = next_button_divs[0].find_element(By.XPATH, ".//a[@aria-label='Next page']")

                # Check if the button is enabled before clicking
                if next_button.is_enabled():
                    next_button.click()  # Click the next button
                    time.sleep(random.uniform(3, 6))  # Add a delay to prevent detection
                else:
                    print("Next button is disabled or not clickable.")
                    break

            except NoSuchElementException:
                print("Next button not found.")
                break

    return reviews_data


# Function to run the scraper for multiple URLs
def run_scraper_for_urls(urls, ratings_to_extract=[1, 2, 3, 4, 5], limit=40):
    for url in urls:
        print(f"Scraping reviews for: {url}")

        for rating in ratings_to_extract:
            try:
                reviews = extract_reviews(url, rating,
                                          limit=limit)  # Extract reviews with a specified limit for each rating
            except Exception as e:
                print(f"Error extracting reviews for rating {rating}: {e}")


# Initialize CSV with headers
save_reviews_to_csv([], file_mode='w')  # 'w' mode to write headers
# Usage
urls = [
    "https://www.tripadvisor.com/Attraction_Review-g60745-d105250-Reviews-Fenway_Park-Boston_Massachusetts.html",
    "https://www.tripadvisor.com/Attraction_Review-g60745-d104604-Reviews-Freedom_Trail-Boston_Massachusetts.html"
]

# Run the scraper for multiple URLs
run_scraper_for_urls(urls)
