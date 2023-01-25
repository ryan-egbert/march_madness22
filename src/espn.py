import re
import json
from bs4 import BeautifulSoup
import urllib
from pprint import pprint
import time
import requests
from util import *

ESPN_LINK = "https://www.espn.com"
ESPN_TEAMS_LINK = "https://www.espn.com/mens-college-basketball/teams"
ESPN_TEAMS_FP = "./output/espn_teams.json"
BPI_TEAMS_FP = "./output/bpi_teams.json"
ESPN_SCHEDULE_LINK = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/{}/season/{}"
ESPN_STATS_LINK = "https://www.espn.com/mens-college-basketball/team/stats/_/id/{}/season/{}"
ESPN_BPI_LINK = "https://www.espn.com/mens-college-basketball/bpi/_/view/overview/season/{}/page/{}"

YEAR = 2022

def _get_teams():
    """
    Gets a list of teams from ESPN with their name and corresponding EspnId
    """
    soup = get_soup(ESPN_TEAMS_LINK)
    teams = soup.find_all("div", {"class": "ContentList__Item"})
    team_link_map = {}
    for team in teams:
        name = team.find("h2").text
        link = team.find("a")['href']
        data = {
            "name": name,
            "link": link
        }
        m = re.search('\/id\/(\d+)\/', link)
        if m:
            id_ = m.group(1)
        else:
            id_ = -1
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
    link = ESPN_SCHEDULE_LINK.format(team_id, year)
    soup = get_soup(link)

    games = soup.find_all("tr", {"class": "Table__TR"})
    all_games = []
    header = True
    header_data = {}
    for game in games:
        game_info = game.find_all("td")
        data = {}
        if len(game_info) > 1:
            if header:
                header = False
                for i in range(len(game_info)):
                    td = game_info[i]
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

def _get_season_stats(team_id, year):
    """
    Gets data on season long stats for a given team/year
    """
    link = ESPN_STATS_LINK.format(team_id, year)
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

def _get_bpi(year):
    page = 1
    pull_data = True
    bpi_ranks = {}
    while pull_data:
        link = ESPN_BPI_LINK.format(year, page)
        soup = get_soup(link)
        no_data = soup.find("div", {"class": "no-data-available"})
        if no_data:
            pull_data = False
        else:
            table = soup.find("table", {"class": "bpi__table"})
            thead = table.find_all("th")
            tbody = table.find("tbody").find_all("tr")

            for tr in tbody:
                all_td = tr.find_all("td")
                team_name = all_td[1].find("span", {"class": "team-names"}).text
                if len(all_td) == len(thead):
                    team_info = {}
                    for i in range(len(all_td)):
                        td = all_td[i]
                        team_link = td.find("a")
                        if team_link:
                            td_info = {
                                "link": team_link["href"],
                                "name": td.text
                            }
                        else:
                            td_info = td.text
                        th = thead[i].text
                        team_info[th] = td_info

                    bpi_ranks[team_name] = team_info
                else:
                    print(f"Lengths don't match for BPI ranks: {team_name}")
        page += 1

    return bpi_ranks

if __name__ == "__main__":
    # _get_season_stats("2", 2022)
    # teams = _get_teams()
    # now = int(time.time())
    # write_json(ESPN_TEAMS_FP, teams)
    bpi_ranks = _get_bpi(2022)
    write_json(BPI_TEAMS_FP, bpi_ranks)