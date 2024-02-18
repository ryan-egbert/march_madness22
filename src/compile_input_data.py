from mongo_client import get_collection
import re
from util import parse_int, parse_float
from pprint import pprint
import pandas as pd

TEAM_STATS = get_collection("team_stats")
GAMES = get_collection("games")
INPUT_FN = "./input/input.csv"

def get_all_games():
    print("Getting all game info")
    return list(GAMES.find({"year": {"$gte": 2008}}))

def get_all_teams():
    print("Getting all team info")
    team_info = {}
    for team in TEAM_STATS.find({"year": {"$gte": 2008}}):
        team_info[team.get("team_id")+ "-" + str(team.get("year"))] = team

    return team_info

def construct_team_row(info, stats, bpi, resume):
    ovr_record = info.get("OVR_RECORD").split("-")
    conf_record = info.get("CONF_RECORD").split("-")
    home_record = info.get("HOME_RECORD").split("-")
    away_record = info.get("AWAY_RECORD").split("-")
    vs_ap_record = info.get("VS_AP").split("-")
    vs_ap_wins = parse_int(vs_ap_record[0])
    vs_ap_losses = parse_int(vs_ap_record[1])
    if vs_ap_losses is not None and vs_ap_wins is not None:
        vs_ap_percent = vs_ap_wins / (vs_ap_wins + vs_ap_losses) if (vs_ap_wins + vs_ap_losses) > 0 else 0
    else:
        vs_ap_percent = 0
    quality = resume.get("qual_wins").split("-")
    quality_wins, quality_losses = parse_int(quality[0]), parse_int(quality[1])
    team = {
        "TEAM": info.get("name"),
        # INFO
        "OVR_PERCENT": info.get("OVR_PERCENT"),
        "WINS": ovr_record[0],
        "LOSSES": ovr_record[1],
        "CONF_PERCENT": info.get("OVR_PERCENT"),
        "CONF_WINS": conf_record[0],
        "CONF_LOSSES": conf_record[1],
        "HOME_PERCENT": info.get("OVR_PERCENT"),
        "HOME_WINS": home_record[0],
        "HOME_LOSSES": home_record[1],
        "AWAY_PERCENT": info.get("OVR_PERCENT"),
        "AWAY_WINS": away_record[0],
        "AWAY_LOSSES": away_record[1],
        "VS_AP_PERCENT": str(vs_ap_percent),
        "VS_AP_WINS": vs_ap_record[0],
        "VS_AP_LOSSES": vs_ap_record[1],
        "CONF": info.get("CONFERENCE"),
        # STATS
        "PPG": stats.get("PPG"),
        "ORBPG": str(stats.get("ORBPG")),
        "DRBPG": str(stats.get("DRBPG")),
        "RBPG": stats.get("RPG"),
        "APG": stats.get("APG"),
        "SPG": stats.get("SPG"),
        "BPG": stats.get("BPG"),
        "TOPG": stats.get("TOPG"),
        "FG%": stats.get("FG%"),
        "FT%": stats.get("FT%"),
        "3P%": stats.get("3P%"),
        "FGAPG": str(stats.get("FGAPG")),
        "FTAPG": str(stats.get("FTAPG")),
        "3PAPG": str(stats.get("3PAPG")),
        # BPI
        "OBPI": bpi.get("off"),
        "DBPI": bpi.get("def"),
        "BPIRK": bpi.get("rank"),
        # RESUME
        "SOR": resume.get("sor"),
        "SOR_SCURVE": resume.get("sor_scurve"),
        "SOS": resume.get("sos"),
        "NC_SOS": resume.get("nc_sos"),
        "QUAL_WINS": str(quality_wins),
        "QUAL_LOSSES": str(quality_losses),
        "QUALITY_INDICATOR": str((quality_wins ** 2) / (quality_wins + quality_losses)) if (quality_wins + quality_losses) > 0 else "0",
        "FINAL_STREAK": info.get("STREAK","0").replace("L", "-").replace("W", "")
    }

    return team

def compile_data():
    input_file = open(INPUT_FN, 'w')
    input_file.write( # TEAM METRICS
                    "TEAM,RECORD_PCT,"\
                    "PPG,FG%,"\
                    "FGAPG,OBPI,DBPI,SOR,"\
                    "SCORE,"\
                    # OPPONENT METRICS
                    "OPP_TEAM,OPP_RECORD_PCT,"\
                    "OPP_PPG,OPP_FG%,"\
                    "OPP_FGAPG,OPP_OBPI,OPP_DBPI,OPP_SOR,"\
                    "OPP_SCORE,"\
                    "WINNER\n")

    games = get_all_games()
    teams = get_all_teams()

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
        
        if not all([info1, info2, stats1, stats2, bpi1, bpi2, resume1, resume2]):
            print(f"Cannot find either {team1} or {team2}. Year: {year}")
            continue

        team1_data = construct_team_row(info1, stats1, bpi1, resume1)
        team2_data = construct_team_row(info2, stats2, bpi2, resume2)

        input_file.write(f"{','.join(team1_data.values())},{team1_score},{','.join(team2_data.values())},{team2_score},{'0' if game.get('winner') == 'team_1' else '1'}\n")
        input_file.write(f"{','.join(team2_data.values())},{team2_score},{','.join(team1_data.values())},{team1_score},{'0' if game.get('winner') == 'team_2' else '1'}\n")
        # break

    input_file.close()

def load_input_file(fn=INPUT_FN):
    df = pd.read_csv(fn)
    print(df.head())
        

compile_data()