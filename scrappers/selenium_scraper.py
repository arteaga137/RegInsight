from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Set up Selenium with Chrome in headless mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
webdriver_service = Service(executable_path='/usr/local/bin/chromedriver')

def extract_articles_with_selenium(urls, depth=1, delay=0):
    visited = set()
    all_articles = []
    start_time = time.time()
    num_links_visited = 0
    num_articles_scraped = 0

    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    def extract_article(url, depth):
        nonlocal num_links_visited, num_articles_scraped

        if url in visited or depth <= 0:
            return None

        visited.add(url)
        num_links_visited += 1
        print(f"Scraping {url} with depth {depth}")

        if delay > 0:
            time.sleep(delay)

        try:
            driver.get(url)
            time.sleep(3)

            try:
                accept_cookies_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class*="cookie"]'))
                )
                accept_cookies_button.click()
                time.sleep(2)
            except Exception as e:
                print(f"No cookie banner found or issue clicking it: {e}")

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            content = ""
            content_divs = soup.find_all(['article', 'section']) or \
                           soup.find_all('div', class_=['content', 'article-body', 'main-content'])
            if content_divs:
                content = "\n".join([div.get_text(separator=" ", strip=True) for div in content_divs])

            if not content:
                paragraphs = soup.find_all('p')
                content = "\n".join([p.get_text() for p in paragraphs])

            content = content.replace('\n', ' ').strip()
            content = ' '.join(content.split())

            title = soup.title.string if soup.title else ''
            author = soup.find('meta', {'name': 'author'})
            publication_date = soup.find('meta', {'property': 'article:published_time'}) or \
                               soup.find('time')
            main_image = soup.find('meta', {'property': 'og:image'})

            article_data = {
                'url': url,
                'title': title.strip() if title else 'No title found',
                'author': author['content'] if author else 'No author found',
                'published': publication_date['datetime'] if publication_date and 'datetime' in publication_date.attrs else 'No publication date found',
                'image': main_image['content'] if main_image else 'No image found',
                'content': content
            }
            all_articles.append(article_data)
            num_articles_scraped += 1

            links = soup.find_all('a', href=True)
            for link in links:
                full_url = urljoin(url, link['href'])
                if full_url.startswith('http') and full_url not in visited:
                    extract_article(full_url, depth - 1)

            return article_data

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    for url in urls:
        extract_article(url, depth)

    driver.quit()

    end_time = time.time()
    total_time = end_time - start_time

    print(f"Total time taken: {total_time:.2f} seconds")
    print(f"Total links visited: {num_links_visited}")
    print(f"Total articles scraped: {num_articles_scraped}")
    print(f"Total length of scraped content: {sum(len(article['content']) for article in all_articles)} characters")
    
    return all_articles if all_articles else []