import logging

from bs4 import BeautifulSoup

from celery import shared_task
from celery.schedules import crontab

from celery_app.models import Author, Quote

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


@shared_task
def scrape_quotes_and_authors():
    base_url = 'https://quotes.toscrape.com/'
    page_number = 1
    quote_count = 0

    while True:
        page_url = f'{base_url}page/{page_number}/'
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            quotes = soup.select('.quote')

            if not quotes:
                logger.info('No quotes found to scrape.')
                break

            for quote in quotes:
                if quote_count >= 5:

                    break

                author_name = quote.select_one('.author').get_text(strip=True)

                about_url = quote.find('a')['href']
                author_response = requests.get('https://quotes.toscrape.com' + about_url)
                if author_response.status_code == 200:
                    author_soup = BeautifulSoup(author_response.content, 'html.parser')
                    born_text = author_soup.select_one('.author-born-date').get_text(strip=True)
                    description_text = author_soup.select_one('.author-description').get_text(strip=True)

                    author, _ = Author.objects.get_or_create(name=author_name)
                    author.born = born_text
                    author.description = description_text
                    author.save()
                    quote_content = quote.select_one('.text').get_text(strip=True)

                    if not Quote.objects.filter(author=author, content=quote_content).exists():
                        Quote.objects.create(author=author, content=quote_content)
                        quote_count += 1
                    else:
                        quote_count == quote_count

            if quote_count >= 5:

                break

            page_number += 1
        else:
            logger.error(f'Error accessing page: {page_url}')
            break


settings.CELERY_BEAT_SCHEDULE = {
    'scrape-quotes': {
        'task': 'celery_app.tasks.scrape_quotes_and_authors',
        'schedule': crontab(hour='1-23/2', minute='0'),
    },
}
