import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
products = []

def scrape_amazon(search_query, pages=3):
    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")
        url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}&page={page}"
        driver.get(url)
        time.sleep(5) # Give it extra time to be safe
        
        # Scroll to load everything
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)
        
        # Find all product containers
        items = driver.find_elements(By.XPATH, '//div[@data-component-type="s-search-result"] | //div[contains(@class, "s-result-item")]')
        print(f"Found {len(items)} containers. Extracting details...")
        
        for item in items:
            name, link, price, rating = "N/A", "N/A", "N/A", "N/A"
            try:
                # --- FLEXIBLE NAME FINDER ---
                name_selectors = ['.//h2//span', './/h3//span', './/span[contains(@class, "a-text-normal")]']
                for selector in name_selectors:
                    try:
                        name = item.find_element(By.XPATH, selector).text
                        if name: break
                    except: continue

                # --- FLEXIBLE LINK FINDER ---
                link_selectors = ['.//h2/a', './/h3/a', './/a[contains(@class, "a-link-normal")]']
                for selector in link_selectors:
                    try:
                        link = item.find_element(By.XPATH, selector).get_attribute('href')
                        if link: break
                    except: continue

                # --- FLEXIBLE PRICE FINDER ---
                price_selectors = ['.//span[@class="a-price-whole"]', './/span[@class="a-offscreen"]']
                for selector in price_selectors:
                    try:
                        price = item.find_element(By.XPATH, selector).text
                        if price: break
                    except: continue

                # Only add if we at least found a name
                if name != "N/A":
                    products.append({
                        "Product Name": name,
                        "Price (INR)": price,
                        "Product Link": link,
                        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

            except Exception as e:
                continue
            
scrape_amazon("laptops", pages=3) # Switched to 'laptops' for a high-result test

if len(products) > 0:
    df = pd.DataFrame(products).drop_duplicates(subset=['Product Name'])
    df.to_excel("Amazon_Price_Intelligence_Full.xlsx", index=False)
    print(f"--- SUCCESS ---")
    print(f"Extracted {len(df)} unique products.")
else:
    print("--- CRITICAL ERROR ---")
    print("Still 0. Amazon is likely showing a CAPTCHA. Look at the Chrome window while it runs!")

driver.quit()