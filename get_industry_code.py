import json
import time
from requests import get
from bs4 import BeautifulSoup

CRAWL_DELAY = 10
# file dir: data/
# file name: data_CITY.json where CITY \in FILES
FILES = ['als', 'arden', 'ejstrupholm', 'loegstoer', 'naesbjerg', 'oester-hurup', 'ranum']

base_url = 'https://datacvr.virk.dk/data/'
crawl_url = f'{base_url}visenhed'

for file in FILES:
    path = f'data/data_{file}.json'
    print('#' * 40)
    print(f'FILE: {path}')
    with open(path, 'r') as f:
        d = json.loads(f.read())

    d = {k: v for k, v in d.items() if d['pnr']}

    row_index = 0
    for ent_id, data in d.items():
        print('-' * 40)
        print(f'{data["navn1"]} | {data["pnr"]}')
        params = {
            'enhedstype': 'produktionsenhed',
            'id': data['pnr'],
            'language': 'da',
            'soeg': data['pnr'],
        }

        print(f'{crawl_url} | {params}')
        res = get(crawl_url, params=params)

        soup = BeautifulSoup(res.content.decode('utf-8'), 'html.parser')

        industry_elem = soup.find('div', attrs={'class': 'Help-stamdata-data-branchekode'})

        industry_elem = industry_elem.parent.parent.parent
        industry = list(industry_elem.children)[3].text.strip()
        data['industry_code'] = industry.split()[0]
        data['industry_text'] = industry.replace(data['industry_code'], '').strip()
        print(f'code: {data["industry_code"]}: {data["industry_text"]}')

        start_date_elem = soup.find('div', attrs={'class': 'Help-stamdata-data-startdato'})

        start_date_elem = start_date_elem.parent.parent.parent
        data['start_date'] = list(start_date_elem.children)[3].text.strip()
        print(f'date: {data["start_date"]}')

        row_index += 1
        row_rem = len(d.keys()) - row_index
        print(f'{row_rem} rows to go')

        time.sleep(CRAWL_DELAY)

    with open(path, 'w') as f:
        f.write(json.dumps(d, indent=4))

    print('#' * 40)
    file_index = FILES.index(file)
    file_rem = len(FILES[file_index + 1:])
    print(f'{file_rem} files to go')