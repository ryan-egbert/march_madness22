import re
import json
from bs4 import BeautifulSoup
import urllib
from Team import Team, TeamGroup
from pprint import pprint
from constants import TEAM_IDS as ids
from constants import ( START_YEAR, END_YEAR )
import requests
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.ncaa
TEAMS = db.teams2

url_re = r'(\d+)'
stats_url = 'https://www.espn.com/mens-college-basketball/team/stats/_/id/{}/season/{}'
record_url = 'https://www.espn.com/mens-college-basketball/standings/_/season/{}'
STATS_CAT = ['NAME','GP','MIN','PTS','REB','AST','STL','BLK','TO','FG%','FT%','3P%',
             'total_NAME','total_MIN','total_FGM','total_FGA','total_FTM','total_FTA',
             'total_3PM','total_3PA','total_PTS','total_OR','total_DR','total_REB',
             'total_AST','total_TO','total_STL','total_BLK']


for year in range(START_YEAR,END_YEAR):
    for id_name in ids:
        print("Stats ==> " + stats_url.format(id_name['id'], str(year)))
        if TEAMS.find_one({'ID': id_name['id'] + str(year)}) == None:
            url_stat = requests.get(stats_url.format(id_name['id'], str(year)))
            stat = url_stat.text
            soup_stat = BeautifulSoup(stat, 'html.parser')
            total_stat = soup_stat.find_all('td',{'class':'Stats__TotalRow'})
            if len(total_stat) == 0:
                continue
            cats = []
            for t in total_stat:
                cats.append(t.find('span').text)

            meta = {
                'name': id_name['name'],
                'year': str(year),
                'stats': cats
            }
            team = Team(id_name['id'], meta)
            TEAMS.insert_one(team.to_dict())

for year in range(START_YEAR,END_YEAR):
    print("Record ==> " + record_url.format(str(year)))
    url_record = requests.get(record_url.format(str(year)))
    record = url_record.text
    soup_record = BeautifulSoup(record, 'html.parser')
    conferences = soup_record.find_all('div', {'class':'standings__table'})
    for conf in conferences:
        tables = conf.find_all('table')
        names_tab = tables[0]
        records_tab = tables[1]
        names = names_tab.find('tbody', {'class': 'Table__TBODY'}).find_all('tr')
        records = records_tab.find('tbody', {'class': 'Table__TBODY'}).find_all('tr')
        assert len(names) == len(records)
        for i in range(len(names)):
            name = names[i].find('span', {'class': 'hide-mobile'})
            if name != None:
                name = name.text
                # print(name)
                cats = records[i].find_all('td')
                overall = cats[3].text
                home = cats[5].text
                away = cats[6].text
                meta = {
                    'record': overall,
                    'home': home,
                    'away': away
                }
                # print(meta)
                TEAMS.update_one({'name': name, 'year': str(year)}, { '$set': { 'record': meta }})

bpi_url = 'https://www.espn.com/mens-college-basketball/bpi/_/view/overview/season/{}/page/{}'
for year in range(START_YEAR, END_YEAR):
    for page in range(1,9):
        print("BPI ==> " + bpi_url.format(str(year), str(page)))
        bpi_req = requests.get(bpi_url.format(str(year), str(page))).text
        soup = BeautifulSoup(bpi_req, 'html.parser')
        bpi_table = soup.find('table', {'class': 'bpi__table'})
        if bpi_table != None:
            bpi_tbody = bpi_table.find('tbody')
            bpi_tr = bpi_table.find_all('tr')
            for rec in bpi_tr:
                bpi_td = rec.find_all('td')
                if len(bpi_td) > 0:
                    id_full = bpi_td[1].find('a', href=True)['href']
                    m = re.search(url_re, id_full)
                    if m:
                        id = m.group(1)
                        record = bpi_td[3].text
                        bpi = bpi_td[4].text
                        sos = bpi_td[5].text
                        sor = bpi_td[6].text
                        meta = {
                            'record': record,
                            'bpi': bpi,
                            'sos': sos,
                            'sor': sor
                        }

                        TEAMS.update_one({'id_num': id, 'year': str(year)}, {'$set': {'ranking': meta}})
            

