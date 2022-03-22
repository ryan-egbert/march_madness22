import re
import json
from bs4 import BeautifulSoup
import urllib
# from Team import Team, TeamGroup
from pprint import pprint
import requests
from pymongo import MongoClient

dates = [
    '20210318',
    '20210319',
    '20210320',
    '20210321',
    '20210322',
    '20210323',
    '20210324',
    '20210325',
    '20210326',
    '20210327',
    '20210328',
    '20210329',
    '20210330',
    '20210331',
    '20210401',
    '20210402',
    '20210403',
    '20210404',
    '20210405',
]

with open('2021_games.csv', 'w') as f:
    for date in dates:
        print('http://cdn.espn.com/mens-college-basketball/scoreboard/_/date/{}'.format(date))
        url = requests.get('http://cdn.espn.com/mens-college-basketball/scoreboard/_/date/{}'.format(date))
        html = url.text
        soup = BeautifulSoup(html, 'html.parser')
        games = soup.find_all('div', {'class':'ScoreboardScoreCell'})
        for game in games:
            teams = game.find_all('li')
            team1name = teams[0].find('div', {'class': 'ScoreCell__TeamName'}).text
            team1seed = teams[0].find('div', {'class': 'ScoreCell__Rank'}).text
            team1score = teams[0].find('div', {'class': 'ScoreCell__Score'})
            if team1score != None:
                team1score = team1score.text
            else:
                team1score = 0
            team2name = teams[1].find('div', {'class': 'ScoreCell__TeamName'}).text
            team2seed = teams[1].find('div', {'class': 'ScoreCell__Rank'}).text
            team2score = teams[1].find('div', {'class': 'ScoreCell__Score'})
            if team2score != None:
                team2score = team2score.text
            else:
                team2score = 0

            f.write(',,,,{},{},{},{},{},{}\n'.format(team1seed, team1score, team1name, team2name, team2score, team2seed))


