from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict
from bs4 import BeautifulSoup
from typing import Dict

class WebScraper:
    def __init__(self):
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the driver
        self.service = Service(ChromeDriverManager().install())
        
    def scrape_website(self, url: str) -> Dict[str, str]:  
        try:
            # Create a new driver instance
            driver = webdriver.Chrome(
                service=self.service,
                options=self.chrome_options
            )
            
            # Set page load timeout
            driver.set_page_load_timeout(30)
            
            try:
                # Get the page
                driver.get(url)
                
                # Wait for body to be present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Extract content
                content = {
                    'title': self._get_title(driver),
                    'main_content': self._get_main_content(driver),
                    'headings': self._get_headings(driver),
                    'meta_description': self._get_meta_description(driver)
                }

                print("Scraped content: \n", content, "\n")
                
                return content
                
            finally:
                driver.quit()
                
        except Exception as e:
            raise Exception(f"Failed to scrape website: {str(e)}")
    def _get_title(self, driver) -> str:
        try:
            return driver.title
            
        except:
            return ""
    
    def _get_meta_description(self, driver) -> str:
        try:
            meta = driver.find_element(
                By.CSS_SELECTOR, 
                'meta[name="description"]'
            )
            return meta.get_attribute('content')
        except:
            return ""

    def _get_main_content(self, driver) -> str:
        content_elements = []
        
        # Try to find main content containers
        selectors = [
            'main',
            'article',
            '#content',
            '#main',
            '.main-content',
            'div[role="main"]'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(
                    By.CSS_SELECTOR, 
                    selector
                )
                if elements:
                    content_elements.extend(elements)
            except:
                continue
        
        # If no main content containers found, get body
        if not content_elements:
            try:
                content_elements = [driver.find_element(By.TAG_NAME, 'body')]
            except:
                return ""
        
        # Extract text content
        text_content = []
        for element in content_elements:
            try:
                text = element.text
                if text:
                    text_content.append(text)
            except:
                continue
        
        return "\n".join(text_content)

    def _get_headings(self, driver) -> list:
        headings = []
        try:
            # Get all heading elements
            for tag in ['h1', 'h2', 'h3']:
                elements = driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text:
                            headings.append({
                                'level': tag,
                                'text': text
                            })
                    except:
                        continue
        except:
            pass
        
        return headings