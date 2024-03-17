from mongo_client import get_collection
import re
from espn import GENDER
from util import parse_int, parse_float
from pprint import pprint
import pandas as pd

TEAM_STATS = get_collection("team_stats")
GAMES = get_collection("games")
INPUT_FN = f"./input/{GENDER}_input.csv"

def get_all_games():
    print("Getting all game info")
    return list(GAMES.find({"year": {"$gte": 2008}}))

def get_all_teams():
    print("Getting all team info")
    team_info = {}
    for team in TEAM_STATS.find({"year": {"$gte": 2008}}):
        team_info[team.get("team_id")+ "-" + str(team.get("year"))] = team

    return team_info

def construct_team_row(info, stats, bpi={}, resume={}, opp=""):
    ovr_record = info.get("OVR_RECORD")
    if ovr_record:
        ovr_record = ovr_record.split("-")
    else:
        print(f"No OVR_RECORD for {info.get('name')}. Skipping game...")
        return None
    
    conf_record = info.get("CONF_RECORD")
    if conf_record:
        conf_record = conf_record.split("-")
    else:
        print(f"No CONF_RECORD for {info.get('name')}. Skipping game...")
        return None
    
    home_record = info.get("HOME_RECORD")
    if home_record:
        home_record = home_record.split("-")
    else:
        print(f"No HOME_RECORD for {info.get('name')}. Skipping game...")
        return None
    
    away_record = info.get("AWAY_RECORD")
    if away_record:
        away_record = away_record.split("-")
    else:
        print(f"No AWAY_RECORD for {info.get('name')}. Skipping game...")
        return None
    
    vs_ap_record = info.get("VS_AP")
    if vs_ap_record:
        vs_ap_record = vs_ap_record.split("-")
    else:
        print(f"No VS_AP for {info.get('name')}. Skipping game...")
        return None
    
    vs_ap_wins = parse_int(vs_ap_record[0])
    vs_ap_losses = parse_int(vs_ap_record[1])
    if vs_ap_losses is not None and vs_ap_wins is not None:
        vs_ap_percent = vs_ap_wins / (vs_ap_wins + vs_ap_losses) if (vs_ap_wins + vs_ap_losses) > 0 else 0
    else:
        vs_ap_percent = 0
    team = {
        f"{opp}TEAM": info.get("name"),
        # INFO
        f"{opp}OVR_PERCENT": info.get("OVR_PERCENT"),
        f"{opp}WINS": ovr_record[0],
        f"{opp}LOSSES": ovr_record[1],
        f"{opp}CONF_PERCENT": info.get("OVR_PERCENT"),
        # f"{opp}CONF_WINS": conf_record[0],
        # f"{opp}CONF_LOSSES": conf_record[1],
        f"{opp}HOME_PERCENT": info.get("OVR_PERCENT"),
        # f"{opp}HOME_WINS": home_record[0],
        # f"{opp}HOME_LOSSES": home_record[1],
        f"{opp}AWAY_PERCENT": info.get("OVR_PERCENT"),
        # f"{opp}AWAY_WINS": away_record[0],
        # f"{opp}AWAY_LOSSES": away_record[1],
        # f"{opp}VS_AP_PERCENT": str(vs_ap_percent),
        f"{opp}VS_AP_WINS": vs_ap_record[0],
        # f"{opp}VS_AP_LOSSES": vs_ap_record[1],
        f"{opp}CONF": info.get("CONFERENCE"),
        # STATS
        f"{opp}PPG": stats.get("PPG"),
        f"{opp}ORBPG": str(stats.get("ORBPG")),
        f"{opp}DRBPG": str(stats.get("DRBPG")),
        f"{opp}RBPG": stats.get("RPG"),
        f"{opp}APG": stats.get("APG"),
        f"{opp}SPG": stats.get("SPG"),
        f"{opp}BPG": stats.get("BPG"),
        f"{opp}TOPG": stats.get("TOPG"),
        f"{opp}FG%": stats.get("FG%"),
        f"{opp}FT%": stats.get("FT%"),
        f"{opp}3P%": stats.get("3P%"),
        f"{opp}FGAPG": str(stats.get("FGAPG")),
        f"{opp}FTAPG": str(stats.get("FTAPG")),
        f"{opp}3PAPG": str(stats.get("3PAPG")),
        # f"{opp}FINAL_STREAK": info.get("STREAK","0").replace("L", "-").replace("W", "")
    }
    
    if bpi:
        bpi_dict = {
            # BPI
            f"{opp}OBPI": bpi.get("off"),
            f"{opp}DBPI": bpi.get("def"),
            f"{opp}BPIRK": bpi.get("rank")
        }
        team.update(bpi_dict)
        
    if resume:
        quality = resume.get("qual_wins", "0-0").split("-")
        quality_wins, quality_losses = parse_int(quality[0]), parse_int(quality[1])
        resume_dict = {
            # RESUME
            f"{opp}SOR": resume.get("sor"),
            # f"{opp}SOR_SCURVE": resume.get("sor_scurve"),
            f"{opp}SOS": resume.get("sos"),
            f"{opp}NC_SOS": resume.get("nc_sos"),
            f"{opp}QUAL_WINS": str(quality_wins),
            # f"{opp}QUAL_LOSSES": str(quality_losses),
            f"{opp}QUALITY_INDICATOR": str((quality_wins ** 2) / (quality_wins + quality_losses)) if (quality_wins + quality_losses) > 0 else "0"
        }
        team.update(resume_dict)

    return team

def compile_data():
    # input_file = open(INPUT_FN, 'w')
    # input_file.write( # TEAM METRICS
    #                 "TEAM,RECORD_PCT,"\
    #                 "PPG,FG%,"\
    #                 "FGAPG,OBPI,DBPI,SOR,"\
    #                 "SCORE,"\
    #                 # OPPONENT METRICS
    #                 "OPP_TEAM,OPP_RECORD_PCT,"\
    #                 "OPP_PPG,OPP_FG%,"\
    #                 "OPP_FGAPG,OPP_OBPI,OPP_DBPI,OPP_SOR,"\
    #                 "OPP_SCORE,"\
    #                 "WINNER\n")

    games = get_all_games()
    teams = get_all_teams()
    
    rows = []

    count = 0
    for game in games:
        count += 1
        # if "Mar" not in game.get("date", ""):
        #     continue
        team1 = str(game.get("team_1").get("id"))
        team2 = str(game.get("team_2").get("id"))
        team1_score = game.get("team_1").get("score")
        team2_score = game.get("team_2").get("score")

        year = str(game.get('year'))

        team1_info = teams.get(team1 + "-" + year)
        team2_info = teams.get(team2 + "-" + year)
        # print(team1_info)
        # print(team2_info)
        
        if team1_info is None or team2_info is None:
            print(f"Cannot find either {team1} or {team2}. Year: {year}")
            continue

        print(f"{round(count/len(games) * 100, 2)}% -- Processing {year} {team1_info.get('info').get('name')}-{team1} vs. {team2_info.get('info').get('name')}-{team2}. Result: {team1_score}-{team2_score}")
            #   flush=False, 
            #   end='\r')

        info1 = team1_info.get("info")
        stats1 = team1_info.get("stats")
        bpi1 = team1_info.get("bpi_info")
        resume1 = team1_info.get("resume_info")
        info2 = team2_info.get("info")
        stats2 = team2_info.get("stats")
        bpi2 = team2_info.get("bpi_info")
        resume2 = team2_info.get("resume_info")
        
        # if not all([info1, info2, stats1, stats2, bpi1, bpi2, resume1, resume2]):
        if not all([info1, info2, stats1, stats2]):
            print(f"Cannot find either {team1} or {team2}. Year: {year}")
            continue

        team1_data = construct_team_row(info1, stats1, bpi1, resume1)
        team2_data = construct_team_row(info2, stats2, bpi2, resume2, opp="OPP_")
        
        if team1_data is None or team2_data is None:
            print(f"Error processing {team1} or {team2}")
            continue
            
        team1_data.update({
            'SCORE': team1_score,
            'WINNER': '0' if game.get('winner') == 'team_1' else '1'
        })
        team2_data.update({
            'OPP_SCORE': team2_score
        })
        
        if team1_data and team2_data:
            total_data = {**team1_data, **team2_data}
            
            rows.append(total_data)

        # input_file.write(f"{','.join(team1_data.values())},{team1_score},{','.join(team2_data.values())},{team2_score},{'0' if game.get('winner') == 'team_1' else '1'}\n")
        # input_file.write(f"{','.join(team2_data.values())},{team2_score},{','.join(team1_data.values())},{team1_score},{'0' if game.get('winner') == 'team_2' else '1'}\n")
        # break


    df = pd.DataFrame(rows)
    df.to_csv(INPUT_FN)

def load_input_file(fn=INPUT_FN):
    df = pd.read_csv(fn)
    print(df.head())
        

compile_data()