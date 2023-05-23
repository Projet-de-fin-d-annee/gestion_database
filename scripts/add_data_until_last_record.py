import asyncio
import datetime
import time
import os
import sys

from pipeline.extract.asynchronus_extraction_with_date_range import AsynchronousDateRangeDataExtractor
from pipeline.load.mysql_data_manager import MySQLDataManager
from pipeline.transform.clean_and_transform_dataframe import *

#print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['..\\..\\Data'])

date_range_data_extractor = AsynchronousDateRangeDataExtractor()

database_host = os.environ.get('DATABASE_HOST')
database_name = os.environ.get('DATABASE_NAME')
database_user = os.environ.get('DATABASE_USER')
database_password = os.environ.get('DATABASE_PASSWORD')

videogames_id_list = [26, 1]

mysql_data_manager = MySQLDataManager("lgm.cihggjssark1.eu-west-3.rds.amazonaws.com", "admin", "azertyuiop", "main")


async def main():
    await mysql_data_manager.connect_to_database()

    last_record_datetime = pd.to_datetime("2023-05-21 00:00:00")
    current_datetime = pd.to_datetime(datetime.datetime.now())
    
    start_time = time.time()

    leagues_df = await date_range_data_extractor.fetch_leagues_with_date_range(last_record_datetime, current_datetime, videogames_id_list)

    #print(leagues_df)

    leagues_id_list = list(set(leagues_df.id.to_list() + await mysql_data_manager.get_table_id_list("league")))

    series_df = await date_range_data_extractor.fetch_series_with_date_range(leagues_id_list, last_record_datetime, current_datetime)

    #print(series_df)

    series_id_list = list(set(series_df.id.to_list() + await mysql_data_manager.get_table_id_list("serie")))

    tournaments_df = await date_range_data_extractor.fetch_tournaments_with_date_range(series_id_list, last_record_datetime, current_datetime)

    #print(tournaments_df)

    tournaments_id_list = tournaments_df.id.to_list() + await mysql_data_manager.get_table_id_list("tournament")

    matches_raw_df, matches_streams_raw_df, matches_games_raw_df, matches_opponents_raw_df = await date_range_data_extractor.fetch_raw_all_matches_infos_with_date_range(tournaments_id_list, last_record_datetime)

    #print(matches_raw_df)
    #print(matches_games_raw_df)
    #print(matches_streams_raw_df)
    #print(matches_opponents_raw_df)

    teams_raw_df, players_raw_df = await date_range_data_extractor.fetch_raw_teams_and_players_from_tournaments_id_list(tournaments_id_list)

    #print(teams_raw_df)
    #print(players_raw_df)

    end_time = time.time()

    print(end_time - start_time)
    

    # pd.to_pickle(clean_leagues_dataframe(leagues_df), "../tests/league")
    # pd.to_pickle(clean_series_dataframe(series_df), "../tests/serie")
    # pd.to_pickle(clean_tournaments_dataframe(tournaments_df), "../tests/tournament")
    # pd.to_pickle(clean_matches_dataframe(matches_raw_df), "../tests/matchs")
    # pd.to_pickle(clean_games_dataframe(matches_games_raw_df), "../tests/match_game")
    # pd.to_pickle(clean_streams_dataframe(matches_streams_raw_df), "../tests/match_stream")
    # pd.to_pickle(clean_opponents_dataframe(matches_opponents_raw_df), "../tests/match_opponent")
    # pd.to_pickle(clean_teams_dataframe(teams_raw_df), "../tests/team")
    # pd.to_pickle(clean_players_dataframe(players_raw_df), "../tests/player")

    start_time = time.time()

    dataframes = {'league': clean_leagues_dataframe(leagues_df), 'serie': clean_series_dataframe(series_df), 'tournament': clean_tournaments_dataframe(tournaments_df), 'matchs': clean_matches_dataframe(matches_raw_df),
                  'match_game': clean_games_dataframe(matches_games_raw_df), 'match_opponent': clean_opponents_dataframe(matches_opponents_raw_df), 'match_stream': clean_streams_dataframe(matches_streams_raw_df),
                  'team': clean_teams_dataframe(teams_raw_df), 'player': clean_players_dataframe(players_raw_df)}

    end_time = time.time()

    print(end_time - start_time)
    
    start_time = time.time()

    tasks = []
    for name, dataframe in dataframes.items():
        task = asyncio.create_task(mysql_data_manager.insert_or_update_data_async(dataframe, name))
        tasks.append(task)

    await asyncio.gather(*tasks)

    end_time = time.time()

    print(end_time - start_time)

    await mysql_data_manager.close_connection()

asyncio.run(main())
