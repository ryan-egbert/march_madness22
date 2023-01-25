import time
from pprint import pprint

from util import *

NET_URL = "https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"

def _get_net():
    soup = get_soup(NET_URL)
    table = soup.find_all("table")
    header_index = {}
    all_schools = {}
    for t in table:
        trs = t.find_all('tr')
        count_trs = 0
        for tr in trs:
            count_trs += 1
            if count_trs == 1:
                headers = tr.text.split('\n')
                for i in range(len(headers)):
                    header_index[i] = headers[i]
            else:
                row = tr.text.split('\n')
                school = row[3]
                data = {}
                for i in range(len(row)):
                    data[header_index[i].lower()] = row[i]
                all_schools[school] = data
    
    return all_schools
    

if __name__ == "__main__":
    schools = _get_net()
    now = int(time.time())
    write_json(f'./output/net_ranks_{now}.json', schools)
