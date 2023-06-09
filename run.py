import asyncio
import logging
import time
from datetime import datetime
from website_data import website_data
from playwright.async_api import async_playwright
from util import insert_articles
from util import insert_logs

# Asynchronous function to crawl articles from a given URL
async def crawl_articles(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Set the viewport size to ensure consistent page rendering
            await page.set_viewport_size(viewport_size={'width': 1280, 'height': 800})

            # Emulate the 'en-US' and 'en' languages for consistent content rendering
            await page.evaluate('() => { Object.defineProperty(navigator, "languages", { get: () => ["en-US", "en"] }); }')

            # Visit the specified URL
            await page.goto(url)

            articles = []
            unique_hrefs = set()
            links = await page.query_selector_all(website_data[url]['article_links'])

            # Extract unique article links from the page
            for link in links:
                try:
                    href = await link.get_attribute('href')

                    if href not in unique_hrefs:
                        articles.append(href)
                        unique_hrefs.add(href)

                except Exception as e:
                    logging.error(f"Error occurred while processing a link: {e}")

            await browser.close()

            return articles

    except Exception as e:
        logging.error(f"Error occurred while crawling: {e}")
        raise

# Asynchronous function to extract data from an article given its URL and selectors
async def extract_article_data(url, selectors):
    result = {}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        # Visit the specified article URL
        await page.goto(url)

        # Extract data using the provided selectors
        for key, selector in selectors.items():
            if key == 'p_texts':
                elements = await page.query_selector_all(selector)
                result[key] = [await element.inner_text() for element in elements]
            elif key == 'img_url':
                element = await page.query_selector(selector)
                result[key] = await element.get_attribute('src') if element else ''
            else:
                element = await page.query_selector(selector)
                result[key] = await element.inner_text() if element else ''

        await browser.close()

    return result

# Asynchronous function to process articles from a given URL using their selectors
async def process_articles(url, selectors):
    articles = await crawl_articles(url)
    counter = 0
    total_articles = len(articles)

    # Iterate over the articles and extract data for each one
    for article_url in articles:
        counter += 1
        start_time = time.time()

        result = await extract_article_data(article_url, selectors)

        # Extract relevant data from the result dictionary
        title = result['header_text']
        opening = result['extracted_text']
        img_url = result['img_url']
        published = result['date']
        author = result['author']
        main_section = result['p_texts']
        created_on = datetime.now()
        modified_on = datetime.now()

        # Insert the extracted data into the articles table
        insert_articles(title, opening, img_url, published, author, main_section, created_on, modified_on)

        elapsed_time = time.time() - start_time

        # Log the progress and elapsed time to the database
        log_message = f"Processed article {counter}/{total_articles}. Time elapsed: {elapsed_time} seconds."
        await insert_logs(log_message, datetime.now())

        print(log_message)

# Main function to run the article processing asynchronously
async def main():
    logging.basicConfig(level=logging.ERROR)

    tasks = []
    for url, selectors in website_data.items():
        task = asyncio.create_task(process_articles(url, selectors))
        tasks.append(task)

    await asyncio.gather(*tasks)

# Entry point of the script
if __name__ == '__main__':
    asyncio.run(main())


