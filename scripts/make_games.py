import re
import json
from bs4 import BeautifulSoup
import urllib
from Game import Game
from pprint import pprint
import requests
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.ncaa
TEAMS = db.teams2
GAMES = db.games

with open('id_name_3.csv','r') as f:
    firstLine = True
    for line in f:
        if firstLine:
            firstLine = False
            continue
        else:
            line = line.replace('\n','')
            info = line.split(',')
            year = info[0]
            round_ = info[1]
            region = info[2]
            team1seed = info[4]
            team1score = info[5]
            team1name = info[6]
            team1id = info[10]
            team2seed = info[9]
            team2score = info[8]
            team2name = info[7]
            team2id = info[11]

            team1 = TEAMS.find_one({'ID': team1id + year})
            team2 = TEAMS.find_one({'ID': team2id + year})

            if team1 != None and team2 != None:
                score = {
                    'team1': team1score,
                    'team2': team2score
                }
                meta = {
                    'year': year,
                    'round': round_,
                    'region': region
                }
                team1['seed'] = team1seed
                team2['seed'] = team2seed
                game = Game(team1, team2, score, meta)

                GAMES.insert_one(game.to_dict())
            else:
                print('could not find {}-{} or {}-{}'.format(team1name, year, team2name, year))
