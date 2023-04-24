import requests
import pandas as pd


class DataExtractor:

    def __init__(self):
        self.api_key = None
        self.api_url = "https://api.pandascore.co"
        self.header = None

    def set_api_key(self, new_api_key):
        self.api_key = new_api_key
        self.header = {"accept": "application/json", "authorization": f"Bearer {new_api_key}"}

    def fetch_raw_videogame(self, videogame):
        url = f"{self.api_url}/videogames/{videogame}"

        game_info = requests.get(url, headers=self.header).json()

        first_dataframe = pd.json_normalize(game_info)

        return first_dataframe

    def fetch_raw_league_from_videogames_id_list(self, videogames_id_list):
        leagues_df = pd.DataFrame()

        for videogame_id in videogames_id_list:
            for page_index in range(1, 5):
                url = f"{self.api_url}/videogames/{videogame_id}/leagues?sort=&page=number={page_index}&size=100&per_page=100"

                response = requests.get(url, headers=self.header)
                data = response.json()

                temp_dataframe = pd.json_normalize(data)

                temp_dataframe["videogame_id"] = videogame_id

                leagues_df = pd.concat([leagues_df, temp_dataframe])

        return leagues_df

    def fetch_raw_series_from_leagues_id_list(self, leagues_id_list):
        series_raw_infos = []

        for league_id in leagues_id_list:
            for page_index in range(1, 4):
                url = f"{self.api_url}/leagues/{league_id}/series?sort=&page={page_index}&per_page=100"

                response = requests.get(url, headers=self.header)
                data = response.json()

                series_raw_infos.extend(data)

        series_raw_df = pd.json_normalize(series_raw_infos)

        return series_raw_df

    def fetch_raw_tournaments_from_series_id_list(self, series_id_list):
        tournaments_raw_infos = []

        for serie_id in series_id_list:
            url = f"https://api.pandascore.co/series/{serie_id}/tournaments?sort=&page=1&per_page=50"

            response = requests.get(url, headers=self.header).json()
            tournaments_raw_infos.extend(response)

        tournaments_raw_df = pd.json_normalize(tournaments_raw_infos)

        return tournaments_raw_df

    def fetch_raw_matches_from_tournaments_id_list(self, tournaments_id_list):
        matches_raw_infos = []

        for tournament_id in tournaments_id_list:
            url = f"{self.api_url}/tournaments/{tournament_id}/matches"

            match_info = requests.get(url, headers=self.header).json()
            matches_raw_infos.extend(match_info)

        matches_raw_df = pd.json_normalize(matches_raw_infos)

        return matches_raw_df

    def fetch_raw_games_from_matches_id_list(self, matches_id_list):
        games_raw_infos = []

        for match_id in matches_id_list:
            url = f"{self.api_url}/matches/{match_id}"

            games_info = requests.get(url, headers=self.header).json()["games"]

            games_raw_infos.extend(games_info)

        games_raw_df = pd.json_normalize(games_raw_infos)

        return games_raw_df

    def fetch_raw_teams_from_tournaments_id_list(self, tournaments_id_list):
        teams_raw_infos = []

        for tournament_id in tournaments_id_list:
            url = f"{self.api_url}/tournaments/{tournament_id}/teams?sort=&page=1&per_page=50"

            raw_teams = requests.get(url, headers=self.header).json()

            teams_raw_infos.extend(raw_teams)

        teams_raw_df = pd.json_normalize(teams_raw_infos)

        return teams_raw_df

    def fetch_raw_players_from_teams_id_list(self, teams_id_list):
        players_raw_df = pd.DataFrame()

        for team_id in teams_id_list:
            url = f"{self.api_url}/players?filter[team_id]={team_id}&sort=&page=1&per_page=50"

            response = requests.get(url, headers=self.header).json()

            temp_players_df = pd.json_normalize(response)
            temp_players_df["team_id"] = team_id

            players_raw_df = pd.concat([players_raw_df, temp_players_df])

        return players_raw_df

    def fetch_raw_stream_from_matches_id_list(self, matches_id_list):
        streams_raw_df = pd.DataFrame()

        for match_id in matches_id_list:
            url = f"{self.api_url}/matches/{match_id}"

            raw_stream = requests.get(url, headers=self.header).json()

            temp_streams_raw_df = pd.json_normalize(raw_stream["streams_list"])
            temp_streams_raw_df["match_id"] = raw_stream["id"]

            pd.concat([streams_raw_df, temp_streams_raw_df])

        return streams_raw_df