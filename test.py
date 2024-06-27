from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# Configure options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)


def check_page_status(url):
    driver.get(url)
    try:
        # Example check: Look for specific text in the body that indicates a 404 page
        body_text = driver.find_element(by=By.TAG_NAME, value="body").text
        print(body_text)
        if "404" in body_text or "Page Not Found" in body_text:
            return "Page Not Found"
        else:
            return "Page Found"
    except NoSuchElementException:
        return "Page Found"


# Test URLs
urls = [
    "https://www.3m.com/3M/en_US/p/d/b40067282/",
    "http://example.com/non-existent-page"
]

for url in urls:
    status = check_page_status(url)
    print(f"URL: {url} - Status: {status}")

# Close the WebDriver
driver.quit()
