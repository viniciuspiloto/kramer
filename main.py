import logging
from datetime import datetime

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

from kramer.cigar import Cigar
from utils.functions import len_to_decimal, convert_currency, curr_to_string, cigars_to_csv

logging.basicConfig(filename='./output/failure/failures.log',
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger(__name__)

URL = 'https://www.cigaraficionado.com'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
    '(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


# Get cigar attributes from an specific url
def get_cigar(url: str, headers: dict) -> Cigar:
    cigar = Cigar()

    try:
        http_request = requests.get(url, headers=headers)
        content = http_request.text
        logger.info(f'HTTP {http_request.status_code}')
    except Exception as e:
        logger.warning(f'HTTP {http_request.status_code} Could not get cigar. {e}')

    soup = BeautifulSoup(content, 'lxml')

    try:
        cigar_details = soup.find('div', class_='row cigar-detail')

        # Tasting Notes
        tasting_note = cigar_details.find(
            'div',
            class_='col-md-10 ml-auto order-3 order-md-2 cigar-detail_tastingnote')
        cigar.tasting_note = tasting_note.contents[3].text

        # Get graphic row details
        cigar.title = cigar_details.find('h1').contents[0]
        score = cigar_details.find('div', class_='attributes-item_score')
        cigar.score = int(score.text)
        attributes = cigar_details.find_all('div', class_='attributes-item_label')
        cigar.length = len_to_decimal(attributes[1].text)
        cigar.strength = attributes[2].text
        attribute_gauge = cigar_details.find('div', class_='ring-gauge')
        cigar.gauge = attribute_gauge.contents[3].text

        # Details
        details = cigar_details.find_all('div', class_='col-12 col-md-6 col-lg-12')

        # First Half
        # Size
        size = details[0].contents[1].text
        cigar.size = size.partition("Size:")[2].strip()

        # Filler
        filler = details[0].contents[5].text
        cigar.filler = filler.partition("Filler:")[2].strip()

        # Binder
        binder = details[0].contents[9].text
        cigar.binder = binder.partition("Binder:")[2].strip()

        # Wrapper
        wrapper = details[0].contents[13].text
        cigar.wrapper = wrapper.partition("Wrapper:")[2].strip()

        # Second Half
        # Country
        country = details[1].contents[1].text
        cigar.country = country.partition("Country:")[2].strip()

        # Price
        try:
            price = details[1].contents[5].text
            price = price.partition("Price:")[2].strip()
            price = price.split()[0]
            currency = curr_to_string(price[0])
            cigar.price = convert_currency(price[1:], currency, 'USD')
        except Exception as e:
            logger.warning(f'Cigar with no price at {url}. {e}')

        # Box Date
        try:
            box_date = details[1].contents[9].text
            box_date = box_date.partition("Box Date:")[2].strip()
            cigar.box_date = datetime.strptime(box_date, '%B %Y')
        except Exception as e:
            cigar.box_date = None
            logging.info(str(e))

        # Issue
        if box_date:
            issue = details[1].contents[13].text
        else:
            issue = details[1].contents[9].text
        issue = issue.partition("Issue:")[2].strip()
        cigar.issue = " ".join(issue.split())

    except Exception as e:
        logger.error(f'Error while trying to get cigar at {url}. {e}')

    return cigar


# Get all cigars from all pages in URL
def get_all_cigars(url: str, headers: dict) -> list:
    cigars = list()

    content_search = requests.get(url, headers=headers).text
    soup_search = BeautifulSoup(content_search, 'lxml')

    max_page = int(soup_search.find('ul', class_='pagination').contents[-2].text)

    for page in tqdm(range(1, max_page + 1)):
        try:
            url_page = f'{url}&page={page}'

            content = requests.get(url_page, headers=headers).text
            soup = BeautifulSoup(content, 'lxml')

            rows = soup.find('div', class_='content-cigarcard')
            view_tasting_note = rows.findChildren('p', class_='d-none d-lg-block')
            for cigar in view_tasting_note:
                cigar_url = URL + cigar.a.get('href')
                cigar = get_cigar(cigar_url, headers)
                cigars.append(cigar)
        except Exception as e:
            logger.error(f'Error. {e}')

    return cigars


if __name__ == '__main__':

    url = 'https://www.cigaraficionado.com/ratings/search?q=&brand='
    cigars = get_all_cigars(url, HEADERS)

    cigars_to_csv(cigars)

    logger.info('All cigars were extracted')
