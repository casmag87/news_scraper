import asyncio
import logging
from playwright.async_api import async_playwright
from util import insert_articles
from util import insert_logs
from datetime import datetime, date
import time
async def url_articles(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)

            articles = {}
            unique_hrefs = set()
            links = await page.query_selector_all('div.zox-art-title a')

            for link in links:
                try:
                    href = await link.get_attribute('href')

                    if href not in unique_hrefs:
                        articles[href] = href
                        unique_hrefs.add(href)

                except Exception as e:
                    logging.error(f"Error occurred while processing a link: {e}")

            await browser.close()

            return articles

    except Exception as e:
        logging.error(f"Error occurred while crawling: {e}")
        raise

async def get_single_article(url):
    result = {}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        header_element = await page.query_selector('h1')
        if header_element:
            result['header_text'] = await header_element.inner_text()
        else: 
            result['header_text'] = []

        span_text = await page.query_selector('span.zox-post-excerpt')
        if span_text:
            result['extracted_text'] = await span_text.inner_text()
        else: 
            result['extracted_text'] = []
        
        image_element = await page.query_selector('.zox-post-img img')
        if image_element:
            result['img_url'] = await image_element.get_attribute('src')
        else: 
            result['img_url'] = []


        date_element = await page.query_selector('.zox-post-date-wrap time')
        if date_element:
            result['date'] = await date_element.inner_text()
        else: 
            result['date'] = []

        author_element = await page.query_selector('.zox-author-name-wrap .zox-author-name a')
        if author_element:
            result['author'] = await author_element.inner_text()
        else: 
            result['author'] = []

        p_tags = await page.query_selector_all('.theiaPostSlider_preloadedSlide p')
        if p_tags:
            result['p_texts'] = [await p_tag.inner_text() for p_tag in p_tags]
        else:
            result['p_texts'] = []

        await browser.close()

    return result






if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    url = 'https://www.securityweek.com/'
    articles = asyncio.run(url_articles(url))
    counter = 0
    total_articles = len(articles)
    
    for article in articles:
        counter += 1
        start_time = time.time()

        result = asyncio.run(get_single_article(article))

        title = result['header_text']
        opening = result['extracted_text']
        img_url = result['img_url']
        published = result['date']
        author = result['author']
        main_section = result['p_texts']
        created_on = datetime.now()
        modified_on = datetime.now()

        insert_articles(title, opening, img_url, published, author, main_section, created_on, modified_on)

        elapsed_time = time.time() - start_time

        # Log the progress and elapsed time to the database
        log_message = f"Processed article {counter}/{total_articles}. Time elapsed: {elapsed_time} seconds."
        print(log_message)
        insert_logs(log_message, datetime.now())