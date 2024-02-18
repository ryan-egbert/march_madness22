import re
import json
from bs4 import BeautifulSoup
import urllib
from pprint import pprint
import time
import requests
from util import *

ESPN_LINK = "https://www.espn.com"
ESPN_TEAMS_LINK = "https://www.espn.com/{}-college-basketball/teams"
ESPN_TEAMS_FP = "./output/espn_teams.json"
BPI_TEAMS_FP = "./output/bpi_teams.json"
ESPN_SCHEDULE_LINK = "https://www.espn.com/{}-college-basketball/team/schedule/_/id/{}/season/{}"
ESPN_STATS_LINK = "https://www.espn.com/{}-college-basketball/team/stats/_/id/{}/season/{}"
ESPN_BPI_LINK = "https://www.espn.com/{}-college-basketball/bpi/_/season/{}/page/{}"
ESPN_RESUME_LINK = "https://www.espn.com/{}-college-basketball/bpi/_/view/resume/season/{}/page/{}"
ESPN_STANDINGS_LINK = "https://www.espn.com/{}-college-basketball/standings/_/season/{}"

GENDER = "womens"

TEAM_ID_FROM_LINK = '\/id\/(\d+)\/'

YEAR = 2022

def get_team_id_from_url(url):
    m = re.search(TEAM_ID_FROM_LINK, url)
    if m:
        id_ = m.group(1)
    else:
        id_ = -1
    
    return id_

def _get_teams():
    """
    Gets a list of teams from ESPN with their name and corresponding EspnId
    """
    soup = get_soup(ESPN_TEAMS_LINK.format(GENDER))
    teams = soup.find_all("div", {"class": "ContentList__Item"})
    team_link_map = {}
    for team in teams:
        name = team.find("h2").text
        link = team.find("a")['href']
        data = {
            "name": name,
            "link": link
        }
        id_ = get_team_id_from_url(link)
        if id_ in team_link_map:
            if isinstance(team_link_map[id_], list):
                team_link_map[id_].append(data)
            else:
                team_link_map[id_] = [data, team_link_map[id_]]
        else:        
            team_link_map[id_] = data
    
    return team_link_map

def _get_games(team_id, year):
    """
    Gets data on games for a given team/year
    """
    link = ESPN_SCHEDULE_LINK.format(GENDER, team_id, year)
    soup = get_soup(link)

    games = soup.find_all("tr", {"class": "Table__TR"})
    all_games = []
    header = True
    header_data = {}
    for game in games:
        game_info = game.find_all("td")
        data = {}
        if len(game_info) == 7:
            if header:
                header = False
                for i in range(len(game_info)):
                    td = game_info[i]
                    # print(td)
                    header_data[i] = td.text
            else:
                for i in range(len(game_info)):
                    td = game_info[i]
                    td_link = td.find("a")
                    td_data = {}
                    if td_link:
                        td_data["link"] = td_link["href"]
                    td_data["info"] = td.text
                    data[header_data[i]] = td_data
                    
                all_games.append(data)

    return all_games

def _get_top_player_stats(team_id, year):
    link = ESPN_STATS_LINK.format(GENDER, team_id, year)
    soup = get_soup(link)
    table = soup.find("div", {"class", "Table__ScrollerWrapper"})
    if not table:
        return {}
    labels = table.find_all("th")
    rows = table.find_all("tr", {"class", "Table__TR--sm"})
    
    top_player_stats = {}
    rows_to_skip = []
    for i in range(len(labels)):
        label = labels[i].find("span")
        if label:
            label_text = label.text
            for j in range(len(rows) - 1):
                if j in rows_to_skip:
                    continue
                row = rows[j]
                stats = row.find_all("td")
                stat = float(stats[i].text)
                if label_text == "GP" and stat < 10 or \
                    label_text == "MIN" and stat < 5:
                        rows_to_skip.append(j)
                        print("Skipping player, GP or MIN were too low...")
                else:
                    if label_text in top_player_stats:
                        top_player_stats[label_text].append(stat)
                    else:
                        top_player_stats[label_text] = [stat]
        
    max_stats = {}            
    for label, stats in top_player_stats.items():
        max_stat = max(stats)
        max_stats[label] = max_stat
    
    return max_stats
    

def _get_season_stats(team_id, year):
    """
    Gets data on season long stats for a given team/year
    """
    link = ESPN_STATS_LINK.format(GENDER, team_id, year)
    soup = get_soup(link)
    labels = soup.find_all("th")
    values = soup.find_all("td", {"class": "Stats__TotalRow"})
    stats = {}
    if len(labels) == len(values):
        for i in range(len(labels)):
            label = labels[i].find("span")
            if not label:
                label = {}
            value = values[i]
            key = label.get("title", "No Label")
            if key in stats:
                stats[key].append(value.text)
            else:
                stats[key] = [value.text]
    else:
        print("Labels and Values are of different lengths.")
    
    return stats

def _get_season_records(year):
    """
    Gets a team's record for a given year
    """
    columns = [
        "CONF_RECORD",
        "GB",
        "CONF_PERCENT",
        "OVR_RECORD",
        "OVR_PERCENT",
        "HOME_RECORD",
        "AWAY_RECORD",
        "STREAK",
        "VS_AP",
        "VS_USA"
    ]
    link = ESPN_STANDINGS_LINK.format(GENDER, year)
    soup = get_soup(link)
    tables = soup.find_all("tbody", {"class": "Table__TBODY"})
    all_teams = []
    team_list = []
    is_team_name = True
    for table in tables:
        trs = table.find_all("tr", class_= lambda x: "subgroup-headers" not in x)
        if is_team_name:
            for tr in trs:
                if "subgroup-headers" in tr.get("class"):
                    team_list.append({})
                    continue
                team =  tr.find("span", {"class": "hide-mobile"}).find("a")
                if team:
                    team_url = team.get("href")
                    team_name = team.text
                    team_id = get_team_id_from_url(team_url)
                    team_list.append({
                        "NAME": team_name,
                        "LINK": team_url,
                        "ID": team_id
                    })
                else:
                    team_list.append({})
        else:
            for i in range(len(trs)):
                team_info = {}
                tr = trs[i]
                if "subgroup-headers" in tr.get("class"):
                    continue
                tds = tr.find_all("td")
                for j in range(len(tds)):
                    td = tds[j]
                    td_text = td.text
                    team_info[columns[j]] = td_text
                team_list[i]["TEAM_INFO"] = team_info
        
            all_teams += team_list
            team_list = []
        is_team_name = not is_team_name

    return all_teams

def _get_resume(year):
    page = 1
    pull_data = True
    resume_ranks = []
    while pull_data:
        link = ESPN_RESUME_LINK.format(GENDER, year, page)
        soup = get_soup(link)
        no_data = soup.find("div", {"class": "NoDataAvailable__Msg"})
        if no_data:
            pull_data = False
        else:
            tables = soup.find_all("table", {"class": "Table"})
            if len(tables) <= 1:
                print(f"Page {page} has invalid data: {link}. Breaking...")
                break
            team_table = True
            all_rows = []
            for table in tables:
                tbody = table.find("tbody")
                trs = tbody.find_all("tr")
                for i in range(len(trs)):
                    tr = trs[i]
                    tds = tr.find_all("td")
                    if team_table:
                        if len(tds) != 2:
                            print("Invalid number of columns")
                            break
                        team = tds[0].find("span", {"class": "TeamLink__Name"})
                        team_conf = tds[1].text
                        team_id = get_team_id_from_url(team.find("a").get("href"))
                        team_name = team.text

                        all_rows.append({
                            "id": team_id,
                            "conference": team_conf,
                            "name": team_name
                        })
                    else:
                        if len(tds) != 7:
                            print("Invalid number of columns")
                            break
                        sor_rank = tds[1].text
                        sor_seek = tds[2].text
                        sor_scurve = tds[3].text
                        qual_wins = tds[4].text
                        sos_rank = tds[5].text
                        nc_sos_rank = tds[6].text

                        all_rows[i]["resume"] = {
                            "sor": sor_rank,
                            "sor_scurve": sor_scurve,
                            "qual_wins": qual_wins,
                            "sos": sos_rank,
                            "nc_sos": nc_sos_rank
                        }
                team_table = not team_table
            resume_ranks += all_rows
        page += 1

    return resume_ranks

def _get_bpi(year):
    page = 1
    pull_data = True
    bpi_ranks = []
    while pull_data:
        link = ESPN_BPI_LINK.format(GENDER, year, page)
        soup = get_soup(link)
        no_data = soup.find("div", {"class": "NoDataAvailable__Msg"})
        if no_data:
            pull_data = False
        else:
            tables = soup.find_all("table", {"class": "Table"})
            if len(tables) <= 1:
                print(f"Page {page} has invalid data: {link}. Breaking...")
                break
            team_table = True
            all_rows = []
            for table in tables:
                tbody = table.find("tbody")
                trs = tbody.find_all("tr")
                for i in range(len(trs)):
                    tr = trs[i]
                    tds = tr.find_all("td")
                    if team_table:
                        if len(tds) != 2:
                            print("Invalid number of columns")
                            break
                        team = tds[0].find("span", {"class": "TeamLink__Name"})
                        team_conf = tds[1].text
                        team_id = get_team_id_from_url(team.find("a").get("href"))
                        team_name = team.text

                        all_rows.append({
                            "id": team_id,
                            "conference": team_conf,
                            "name": team_name
                        })
                    else:
                        if len(tds) != 10:
                            print("Invalid number of columns")
                            break
                        bpi = tds[1].text
                        bpi_rank = tds[2].text
                        bpi_off = tds[4].text
                        bpi_def = tds[5].text

                        all_rows[i]["bpi_info"] = {
                            "bpi": bpi,
                            "rank": bpi_rank,
                            "off": bpi_off,
                            "def": bpi_def
                        }
                team_table = not team_table
            bpi_ranks += all_rows
        page += 1

    return bpi_ranks

if __name__ == "__main__":
    stats = _get_top_player_stats("2", 2022)
    # teams = _get_teams()
    # pprint(teams)
    # now = int(time.time())
    # write_json(ESPN_TEAMS_FP, teams)
    # bpi_ranks = _get_bpi(2022)
    # resume = _get_resume(2022)
    # games = _get_games("2", 2022)
    # write_json("./output/bpi_ranks_2022.json", bpi_ranks)
    # records = _get_season_records(2021)
    pprint(stats)
    # write_json("./output/2021_records.json", records)