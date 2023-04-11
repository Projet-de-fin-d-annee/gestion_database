import requests
from config import API_URL, HEADER


def fetch_raw_series(videogame):
    url = f"{API_URL}/videogames/{videogame}/series?sort=&page=1&per_page=50"

    series = requests.get(url, headers=HEADER).json()

    return series


def fetch_raw_matches(tournament):
    url = f"{API_URL}/tournaments/{tournament}"

    matches = requests.get(url, headers=HEADER).json()["matches"]

    return matches


def fetch_raw_tournament_participants(tournament):
    url = f"{API_URL}/tournaments/{tournament}"

    rosters = requests.get(url, headers=HEADER).json()

    return rosters


def fetch_raw_players(team):
    url = f"{API_URL}/teams/{team}"

    players = requests.get(url, headers=HEADER).json()["players"]

    return players


def fetch_raw_team(team):
    url = f"{API_URL}/teams/{team}"

    raw_team = requests.get(url, headers=HEADER).json()


    return raw_team