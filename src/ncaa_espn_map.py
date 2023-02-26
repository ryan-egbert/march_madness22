import json
from util import write_json, load_json

def get_possible_map():
    net_schools = load_json('output/net.json')
    espn_teams = load_json('output/espn_teams.json')

    school_map = {
        "no_espn_match": [],
        "no_net_match": []
    }

    for net_name, net_team_info in net_schools.items():
        found_match = False
        for espn_id, espn_team_info in espn_teams.items():
            if espn_id == "-1":
                continue
            espn_name = espn_team_info.get("name")
            if net_name.replace('.', '') in espn_name:
                found_match = True
                print(f"Found possible map: {net_name} ==> {espn_name}")
                if espn_id not in school_map:
                    school_map[espn_id] = [net_name]
                else:
                    school_map[espn_id].append(net_name)

        if not found_match:
            print(f"No match found for {net_name}")
            school_map["no_espn_match"].append(net_name)
    
    for espn_id, espn_team_info in espn_teams.items():
        if espn_id == "-1":
            continue
        if espn_id not in school_map:
            school_map["no_net_match"].append(f"{espn_id} --> {espn_team_info['name']}")


    return school_map


def validate_map():
    net_schools = load_json('output/net.json')
    espn_teams = load_json('output/espn_teams.json')
    possible_map = load_json('output/possible_map.json')
    
    correct_map = {}
    for espn_id, net_list in possible_map.items():
        if espn_id in espn_teams:
            espn_name = espn_teams[espn_id]["name"]
            if len(net_list) > 1:
                print(f"ESPN NAME: {espn_name}")
                correct = int(input(f"in {net_list}:\n").strip())
            else:
                correct = 0
            correct_map[espn_id] = net_list[correct]
        else:
            print(f"{espn_id} not found in espn_names")

    write_json('output/correct_map.json', correct_map)

def check_all_exist():
    net_schools = load_json('output/net.json')
    espn_teams = load_json('output/espn_teams.json')
    correct_map = load_json('output/correct_map.json')

    for espn_id, espn_team_info in espn_teams.items():
        if espn_id not in correct_map.keys():
            print(f"{espn_id} not in correct_map.json")
    
    for net_name, net_team_info in net_schools.items():
        if net_name not in correct_map.values():
            print(f"{net_name} not in correct_map.json")


if __name__ == "__main__":
    # school_map = get_possible_map()
    # write_json("output/possible_map.json", school_map)
    check_all_exist()