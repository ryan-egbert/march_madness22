from mongo_client import get_collection
from espn import (
    _get_bpi,
    _get_games,
    _get_season_records,
    _get_season_stats,
    _get_teams,
    _get_resume,
    GENDER
)
import re
from util import parse_int

TEAM_STATS = get_collection("team_stats") if GENDER == "mens" else get_collection("womens_team_stats")
GAMES = get_collection("games") if GENDER == "mens" else get_collection("womens_games")

GET_GAME_ID = r"/gameId/(\d+)"

def get_team_id_from_link(link):
    teams = _get_teams()
    for team_id, team_info in teams.items():
        if isinstance(team_info, list):
            continue
        if team_info["link"] == link:
            return team_id
    print(f"No team found with link: {link}")
    return -1

def get_game_id_from_link(link):
    m = re.search(GET_GAME_ID, link)
    if m:
        id_ = m.group(1)
    else:
        print(f"No id found in link: {link}")
        id_ = -1
    return id_

def insert_games(team_id, year, games):
    for game in games:
        if not game.get("RESULT", {}).get("link"):
            print("Game not found. Skipping...")
            continue
        result = game.get("RESULT", {})
        game_link = result.get("link", "")
        game_id = get_game_id_from_link(game_link)
        if list(GAMES.find({"game_id": game_id})):
            print(f"game_id: {game_id} already exists in Mongo. Skipping...")
            continue
        opponent_link = game.get("OPPONENT", {}).get("link", "")
        if opponent_link:
            opponent_id = get_team_id_from_link(opponent_link)
        else:
            opponent_id = game.get("OPPONENT", {}).get("info", "")
        is_win = result.get("info", "").startswith('W')
        winner = "team_1" if is_win else "team_2"
        scores = result.get("info", "").replace("W", "").replace("L", "").split("-")
        if len(scores) <= 1:
            print(f"Invalid score {scores}.")
            continue
        if is_win:
            score = scores[0]
            opponent_score = scores[1].split(" ")[0]
        else:
            score = scores[1].split(" ")[0]
            opponent_score = scores[0]
        date = game.get("DATE", {}).get("info", "")

        doc = {
            "game_id": game_id,
            "date": date,
            "year": year, 
            "link": game_link,
            "team_1": {
                "id": team_id,
                "score": score
            },
            "team_2": {
                "id": opponent_id,
                "score": opponent_score
            },
            "winner": winner
        }

        GAMES.insert_one(doc)

def insert_stats(team_id, year, season_stats, team_info):
    abbreviation_map = {
        "Points Per Game": "PPG",
        "Rebounds Per Game": "RPG",
        "Assists Per Game": "APG",
        "Steals Per Game": "SPG",
        "Blocks Per Game": "BPG",
        "Turnovers Per Game": "TOPG",
        "Field Goal Percentage": "FG%",
        "Free Throw Percentage": "FT%",
        "3-Point Field Goal Percentage": "3P%",
    }
    games_played = parse_int(season_stats.get("Games Played", [-1])[0])
    if not games_played:
        print("Won't insert stats, error occurred")
        return
    
    stat_dict = {}
    for full_name, abbreviation in abbreviation_map.items():
        stat_dict[abbreviation] = season_stats.get(full_name, [""])[0]
    
    fga = parse_int(season_stats.get("Field Goals Attempted", [-1])[0])
    fta = parse_int(season_stats.get("Free Throws Attempted", [-1])[0])
    _3pa = parse_int(season_stats.get("3-Point Field Goals Attempted", [-1])[0])
    orb = parse_int(season_stats.get("Offensive Rebounds", [-1])[0])
    drb = parse_int(season_stats.get("Defensive Rebounds", [-1])[0])

    if fga:
        stat_dict["FGAPG"] = fga / games_played
    if fta:
        stat_dict["FTAPG"] = fta / games_played
    if _3pa:
        stat_dict["3PAPG"] = _3pa / games_played
    if orb:
        stat_dict["ORBPG"] = orb / games_played
    if drb:
        stat_dict["DRBPG"] = drb / games_played

    if list(TEAM_STATS.find({"team_id": team_id, "year": year})):
        print(f"Document already exists for {team_id} - {year}. Skipping...")
        return

    TEAM_STATS.insert_one({
        "team_id": team_id,
        "year": year,
        "stats": stat_dict,
        "info": team_info
    })
    



def add_teams():
    GAMES.delete_many({})
    TEAM_STATS.delete_many({})
    first_year = 2008
    final_year = 2022

    teams = _get_teams()

    for year in range(first_year, final_year+1):
        season_records = _get_season_records(year)
        # bpi = _get_bpi(year)
        for team_id, team_info in teams.items():
            if not isinstance(team_info, dict):
                print(f"{team_id} not a valid team")
                continue
            print(f"Processing {team_info.get('name')} for {year}")
            for record in season_records:
                if record.get("ID") == team_id:
                    team_info.update(record.get("TEAM_INFO", {}))
            games = _get_games(team_id, year)
            insert_games(team_id, year, games)
            season_stats = _get_season_stats(team_id, year)
            insert_stats(team_id, year, season_stats, team_info)

def add_bpi():
    first_year = 2008
    final_year = 2022

    for year in range(first_year, final_year+1):
        print(f"Processing year {year}...")
        bpi_ranks = _get_bpi(year)
        count = 0
        for bpi_info in bpi_ranks:
            count += 1
            if count % 100 == 0:
                print(f"Team {count} of {len(bpi_ranks)} processed")
            team_id = bpi_info.get("id")
            conf = bpi_info.get("conference")
            bpi_info = bpi_info.get("bpi_info")

            TEAM_STATS.find_one_and_update({"team_id": team_id, "year": year}, {
                "$set": {"bpi_info": bpi_info, "info.CONFERENCE": conf}
            })
            
def add_resume():
    first_year = 2008
    final_year = 2022

    for year in range(first_year, final_year+1):
        print(f"Processing year {year}...")
        resume_ranks = _get_resume(year)
        count = 0
        for resume in resume_ranks:
            count += 1
            if count % 100 == 0:
                print(f"Team {count} of {len(resume_ranks)} processed")
            team_id = resume.get("id")
            # print(team_id, year)
            # conf = resume.get("conference")
            resume_info = resume.get("resume")

            TEAM_STATS.find_one_and_update({"team_id": team_id, "year": year}, {
                "$set": {"resume_info": resume_info}
            })
        #     break
        # break



add_teams()
add_bpi()
add_resume()