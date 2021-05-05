import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from cigar import Cigar
from functions import len_to_decimal, convert_currency, curr_to_string

logger = logging.getLogger(__name__)


# Get cigar attributes from an specific url
def get_cigar(url: str) -> Cigar:
    cigar = Cigar()

    content = requests.get(url).text

    soup = BeautifulSoup(content, 'lxml')

    cigar_details = soup.find('div', class_='row cigar-detail')

    # Tasting Notes
    tasting_note = cigar_details.find(
        'div',
        class_='col-md-10 ml-auto order-3 order-md-2 cigar-detail_tastingnote')
    tasting_note = tasting_note.contents[3].text

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
    price = details[1].contents[5].text
    price = price.partition("Price:")[2].strip()
    price = price.split()[0]
    currency = curr_to_string(price[0])
    cigar.price = convert_currency(price[1:], currency, 'USD')

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

    return cigar


# def get_all_cigars(url: str) -> list[Cigar]:
#     content = requests.get(url).text

#     soup = BeautifulSoup(content, 'lxml')


if __name__ == '__main__':
    # url = 'https://www.cigaraficionado.com/ratings/22233'
    # url = 'https://www.cigaraficionado.com/ratings/22439'
    # cigar = get_cigar(url)

    # get_all_cigars()

    logger.info('All cigars were extracted')
