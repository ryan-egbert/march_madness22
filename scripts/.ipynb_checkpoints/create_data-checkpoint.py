from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.ncaa
GAMES = db.games

import pandas as pd
import numpy as np

mm_games = list(GAMES.find())

with open('MARCH_MADNESS_DATA.csv', 'w') as f:
    f.write('YEAR,ROUND,REGION,')
    f.write('T1ID,T1SEED,T1SCORE,T1NAME,T1PTS,T1REB,T1AST,T1STL,T1BLK,T1TO,T1FG%,T1FT%,T13P%,T1W,T1L,T1HW,T1HL,T1AW,T1AL,T1BPI,T1SOS,T1SOR,T1REC,T1HREC,T1AREC,')
    f.write('T2ID,T2SEED,T2SCORE,T2NAME,T2PTS,T2REB,T2AST,T2STL,T2BLK,T2TO,T2FG%,T2FT%,T23P%,T2W,T2L,T2HW,T2HL,T2AW,T2AL,T2BPI,T2SOS,T2SOR,T2REC,T2HREC,T2AREC,')
    f.write('SEEDDIFF,BPIDIFF,SOSDIFF,SORDIFF,WINNER\n')

    for game in mm_games:
        year = game['year']
        round_ = game['round']
        region = game['region']
        f.write(f'{year},{round_},{region},')
        
        ### TEAM 1 INFO ###
        t1id = game['team1']['id_num']
        t1seed = game['team1']['seed']
        t1score = game['team1score']
        t1name = game['team1']['name']
        t1PTS = game['team1']['stats']['PTS']
        t1REB = game['team1']['stats']['REB']
        t1AST = game['team1']['stats']['AST']
        t1STL = game['team1']['stats']['STL']
        t1BLK = game['team1']['stats']['BLK']
        t1TOV = game['team1']['stats']['TO']
        t1FG = game['team1']['stats']['FG%']
        t1FT = game['team1']['stats']['FT%']
        t13P = game['team1']['stats']['3P%']
        t1w = game['team1']['record']['record'].split('-')[0]
        t1l = game['team1']['record']['record'].split('-')[1]
        t1rec = round(int(t1w) / (int(t1w) + int(t1l)),3)
        t1hw = game['team1']['record']['home'].split('-')[0]
        t1hl = game['team1']['record']['home'].split('-')[1]
        if t1hw != '' and t1hl != '':
            t1hrec = round(int(t1hw) / (int(t1hw) + int(t1hl)),3)
        else:
            t1hrec = '--'
        t1aw = game['team1']['record']['away'].split('-')[0]
        t1al = game['team1']['record']['away'].split('-')[1]
        if t1aw != '' and t1al != '':
            t1arec = round(int(t1aw) / (int(t1aw) + int(t1al)),3)
        else:
            t1arec = '--'
        t1bpi = game['team1']['ranking']['bpi']
        t1sos = game['team1']['ranking']['sos']
        t1sor = game['team1']['ranking']['sor']
        f.write(f'{t1id},{t1seed},{t1score},{t1name},{t1PTS},{t1REB},{t1AST},{t1STL},{t1BLK},{t1TOV},{t1FG},{t1FT},{t13P},{t1w},{t1l},{t1hw},{t1hl},{t1aw},{t1al},{t1bpi},{t1sos},{t1sor},{t1rec},{t1hrec},{t1arec},')

        ### TEAM 2 INFO ###
        t2id = game['team2']['id_num']
        t2seed = game['team2']['seed']
        t2score = game['team2score']
        t2name = game['team2']['name']
        t2PTS = game['team2']['stats']['PTS']
        t2REB = game['team2']['stats']['REB']
        t2AST = game['team2']['stats']['AST']
        t2STL = game['team2']['stats']['STL']
        t2BLK = game['team2']['stats']['BLK']
        t2TOV = game['team2']['stats']['TO']
        t2FG = game['team2']['stats']['FG%']
        t2FT = game['team2']['stats']['FT%']
        t23P = game['team2']['stats']['3P%']
        t2w = game['team2']['record']['record'].split('-')[0]
        t2l = game['team2']['record']['record'].split('-')[1]
        t2rec = round(int(t2w) / (int(t2w) + int(t2l)),3)
        t2hw = game['team2']['record']['home'].split('-')[0]
        t2hl = game['team2']['record']['home'].split('-')[1]
        if t2hw == '' or t2hl == '':
            t2hrec = '--'
        else:
            t2hrec = round(int(t2hw) / (int(t2hw) + int(t2hl)),3)
        # t2hrec = round(int(t2hw) / (int(t2hw) + int(t2hl)),3)
        t2aw = game['team2']['record']['away'].split('-')[0]
        t2al = game['team2']['record']['away'].split('-')[1]
        if t2aw == '' or t2al == '':
            t2arec = '--'
        else:
            t2arec = round(int(t2aw) / (int(t2aw) + int(t2al)),3)
        # t2arec = round(int(t2aw) / (int(t2aw) + int(t2al)),3)
        t2bpi = game['team2']['ranking']['bpi']
        t2sos = game['team2']['ranking']['sos']
        t2sor = game['team2']['ranking']['sor']
        f.write(f'{t2id},{t2seed},{t2score},{t2name},{t2PTS},{t2REB},{t2AST},{t2STL},{t2BLK},{t2TOV},{t2FG},{t2FT},{t23P},{t2w},{t2l},{t2hw},{t2hl},{t2aw},{t2al},{t2bpi},{t2sos},{t2sor},{t2rec},{t2hrec},{t2arec},')

        winner = 0 if int(t1score) > int(t2score) else 1
        seed_diff = int(t1seed) - int(t2seed)
        bpi_diff = int(t1bpi) - int(t2bpi)
        sos_diff = int(t1sos) - int(t2sos)
        sor_diff = int(t1sor) - int(t2sor)
        f.write(f'{seed_diff},{bpi_diff},{sos_diff},{sor_diff},{winner}\n')


