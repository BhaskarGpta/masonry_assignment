import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from utils.file import FileHandler
import os

class WebScraper:
    def __init__(self, sites_file: str, output_dir: str = "data/scraped_data"):
        self.sites = FileHandler.load_json(sites_file)
        self.output_dir = output_dir
        self.file_handler = FileHandler()
        os.makedirs(self.output_dir, exist_ok=True)

    def create_driver(self):
        service = Service(executable_path='/home/bhaskar/mansory/masonry/chromedriver')
        options = Options()
        options.add_argument('--headless') #headless for less gpu-usage
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(180)  # increased time since was observing frequent timeouts
        return driver

    def scrape_site(self, url: str, title: str):
        retries = 3  # Number of retries before giving up
        for attempt in range(retries):
            try:
                driver = self.create_driver()
                print(f"\n🔗 Scraping: {url}")
                driver.get(url)
                time.sleep(3)

                data = {
                    "url": url,
                    "headings": [],
                    "paragraphs": [],
                    "lists": [],
                    "tables": []
                }

                # Scroll to bottom to load all content
                old_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if old_height == new_height:
                        break
                    old_height = new_height

                # Try to click "Read more" buttons
                try:
                    read_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Read more') or contains(text(),'More')]")
                    for button in read_more_buttons:
                        button.click()
                        time.sleep(3)
                except Exception as e:
                    print(f"❌ Error finding Read More buttons: {e}")

                driver.execute_script("window.scrollTo(0, 0);") #SCrll above once since read more can be anywhere on the page, scrolling above and then down once more will make sure entire cntent is loaded
                old_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) #wait for loading
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if old_height == new_height:
                        break
                    old_height = new_height

                # Extract headings
                for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    elements = driver.find_elements(By.TAG_NAME, tag)
                    data["headings"].extend([el.text for el in elements if el.text.strip()])

                # Extract paragraphs
                paragraphs = driver.find_elements(By.TAG_NAME, "p")
                data["paragraphs"] = [p.text for p in paragraphs if p.text.strip()]

                # Extract lists
                lists = driver.find_elements(By.TAG_NAME, "ul") + driver.find_elements(By.TAG_NAME, "ol")
                for l in lists:
                    items = l.find_elements(By.TAG_NAME, "li")
                    list_text = [item.text for item in items if item.text.strip()]
                    if list_text:
                        data["lists"].append(list_text)

                # Extract tables
                tables = driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    table_data = []
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td") + row.find_elements(By.TAG_NAME, "th")
                        row_data = [cell.text.strip() for cell in cells if cell.text.strip()]
                        if row_data:
                            table_data.append(row_data)
                    if table_data:
                        data["tables"].append(table_data)

                filename = self.sanitize_filename(title) + ".json"
                path = os.path.join(self.output_dir, filename)
                self.file_handler.save_json(data, path)

                print(f"✅ Successfully scraped {url}")
                break  # Exit the loop if scraping is successful

            except TimeoutException as e:
                print(f"❌ Timeout error occurred while scraping {url}. Retrying... ({attempt + 1}/{retries})")
                time.sleep(5)  # Wait for 5 seconds before retrying

            except WebDriverException as e:
                print(f"❌ WebDriver error occurred while scraping {url}: {e}")
                break  # Exit the loop if the error is not recoverable

            except Exception as e:
                print(f"❌ General error occurred while scraping {url}: {e}")
                break  # Exit the loop after other types of errors

            finally:
                driver.quit()

    def sanitize_filename(self, name: str):
        return name.replace(".", "_").replace("/", "_").strip("_")

    def start_scraping(self):
        for site in self.sites:
            link = site["url"]
            title = site["title"]
            self.scrape_site(link, title)
