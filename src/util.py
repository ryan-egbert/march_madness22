import requests
from bs4 import BeautifulSoup
import json

def get_soup(link):
    resp = requests.get(link)
    text = resp.text
    soup = BeautifulSoup(text, 'html.parser')
    return soup


def write_json(filepath, json_obj):
    with open(filepath, 'w') as f:
        json.dump(json_obj, f)

def load_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    return data

def parse_int(int_str):
    try:
        res = int(int_str)
        return res
    except ValueError as e:
        print(f"Invalid param passed {int_str}")
        return None