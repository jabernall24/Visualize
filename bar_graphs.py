import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLog
import datetime
from constants import MONTHS, TO_MONTH, TEAM_COLORS
import os
import mpld3
import json
from pprint import pprint

class BarGraph(object):

    def __init__(self, player_name):
        """
        :param player_name: Name of player you want to plot a graph for
        :param season: Season you would like to plot (2018-19)
        :param season_type: Pre Season, Regular Season, Playoffs
        """
        possible_players = players.find_players_by_full_name(player_name)
        if len(possible_players) > 1:
            for i, player in enumerate(possible_players):
                print(f"For '{player['full_name']}' with id {player['id']} enter {i}")

            index = int(input("Select the player you want: "))
            self.player = possible_players[index]
        elif len(possible_players) == 1:
            self.player = possible_players[0]
        else:
            print("Unknown player")
        # self.season = season
        # self.season_type = season_type
        self.df_game_logs = None

    def games_with_x_amount_of_points(self, season, season_type):
        """
        :return: Shows a graph of the player's season with the amount of times a player scored between x amount of
                 points
        """
        # abs_path = os.path.abspath(os.path.dirname(__file__))
        # path = f"files/{self.player['full_name']}/games_with_x_amount_of_points/{self.player['first_name']}.png"
        # if os.path.exists(f"{abs_path}/static/{path}"):
        #     return path
        #
        # os.makedirs(f"{abs_path}/static/files/{self.player['full_name']}/games_with_x_amount_of_points/")

        if self.df_game_logs is None:
            self.df_game_logs = self.get_game_logs(season=season, season_type=season_type)

        point_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        """ Checks the amount of times each bin appears """
        data = [len(self.df_game_logs[self.df_game_logs['PTS_Binned'] == '0-9']),
                len(self.df_game_logs[self.df_game_logs['PTS_Binned'] == '10-19']),
                len(self.df_game_logs[self.df_game_logs['PTS_Binned'] == '20-29']),
                len(self.df_game_logs[self.df_game_logs['PTS_Binned'] == '30-39']),
                len(self.df_game_logs[self.df_game_logs['PTS_Binned'] == '40-49']),
                len(self.df_game_logs[self.df_game_logs['PTS_Binned'] == '50+'])]

        fig = plt.figure()
        plt.bar(point_labels, data)

        plt.xticks(np.arange(6), point_labels, rotation=50, fontsize=10)
        plt.xlabel('Points', fontsize=18)

        plt.yticks(np.arange(0, max(data) + 10, 5), fontsize=10)
        plt.ylabel('Games', fontsize=18)

        plt.title(f"Points binned scored for the\n{season} {season_type}\nby {self.player['full_name']}")

        myfig = mpld3.fig_to_dict(fig)

        for i, a in enumerate(myfig['axes'][0]['axes'][0]['tickvalues']):
            myfig['axes'][0]['axes'][0]['tickvalues'][i] = int(myfig['axes'][0]['axes'][0]['tickvalues'][i])

        for i, a in enumerate(myfig['axes'][0]['axes'][1]['tickvalues']):
            myfig['axes'][0]['axes'][1]['tickvalues'][i] = int(myfig['axes'][0]['axes'][1]['tickvalues'][i])

        plt.close('all')
        return json.dumps(myfig)

    def points_per_month(self):
        """
        :return: Shows a graph with the total points the player scored each month of the season
        """
        if self.df_game_logs is None:
            self.df_game_logs = self.get_game_logs()

        plt.figure(figsize=(15, 6.75))

        months = np.array(self.df_game_logs['GAME_MONTH'].unique())
        months = [TO_MONTH[val] for val in months]
        points_grouped = np.array(self.df_game_logs.groupby('GAME_MONTH', sort=False)['PTS'].sum())

        plt.bar(months, points_grouped)

        plt.xticks(rotation=50)
        plt.xlabel('Month')

        plt.ylabel('Points')

        plt.title(f"{self.player['full_name']}\n{self.season}\nTotal points per month")
        plt.show()

    def point_avg_vs_every_team(self):
        """
        :return: Shows a graph with the average points the player scored against every team
        """
        if self.df_game_logs is None:
            self.df_game_logs = self.get_game_logs()

        plt.figure(figsize=(15, 6.75))

        teams = np.array(self.df_game_logs['OPP'].unique())
        pts_on_teams = np.array(self.df_game_logs.groupby('OPP', sort=False)['PTS'].mean())
        colors = [TEAM_COLORS[team] for team in teams]

        plt.bar(teams, pts_on_teams, color=colors)

        plt.xticks(rotation=50)
        plt.xlabel('Team')

        plt.ylabel('Total Points')

        plt.title(f"{self.player['full_name']}\n{self.season}\nAverage points vs every team")
        plt.show()

    def points_vs_every_team(self):
        """
        :return: Shows a graph with the total points the player scored vs every team
        """
        if self.df_game_logs is None:
            self.df_game_logs = self.get_game_logs()

        plt.figure(figsize=(15, 6.75))

        teams = np.array(self.df_game_logs['OPP'].unique())
        pts_on_teams = np.array(self.df_game_logs.groupby('OPP', sort=False)['PTS'].sum())
        colors = [TEAM_COLORS[team] for team in teams]

        plt.bar(teams, pts_on_teams, color=colors)

        plt.xticks(rotation=50)
        plt.xlabel('Team')

        plt.ylabel('Total Points')

        plt.title(f"{self.player['full_name']}\n{self.season}\nTotal points vs every team")
        plt.show()

    def get_game_logs(self, season, season_type):
        """
        Cleans up the data and adds new columns to the df that nba_api creates

        :return: Makes a DataFrame
        """
        player_game_logs = PlayerGameLog(player_id=self.player['id'], season=season,
                                         season_type_all_star=season_type)
        df = player_game_logs.player_game_log.get_data_frame()

        """ Put points into bins """
        points = [0, 10, 20, 30, 40, 50, 200]
        point_labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50+']

        df['PTS_Binned'] = pd.cut(df['PTS'], points, labels=point_labels, include_lowest=True, right=False)

        month = np.zeros(len(df), int)
        day = np.zeros(len(df), int)
        year = np.zeros(len(df), int)

        for i, date in enumerate(df['GAME_DATE']):
            temp = date.split(' ')
            month[i] = MONTHS[temp[0]]
            day[i] = temp[1][:-1]
            year[i] = temp[2]

        df["GAME_MONTH"] = month
        df["GAME_DAY"] = day
        df["GAME_YEAR"] = year

        team = list()
        opp = list()
        home_away = list()
        for matchup in df['MATCHUP']:
            temp = matchup.split(' ')
            team.append(temp[0])
            opp.append(temp[2])
            if temp[1] == '@':
                home_away.append(temp[1])
            else:
                home_away.append(temp[1][:-1])

        df['TEAM'] = team
        df['OPP'] = opp
        df['H/A'] = home_away

        del df['VIDEO_AVAILABLE']
        del df['GAME_DATE']
        del df['Game_ID']
        del df['SEASON_ID']
        del df['MATCHUP']
        del df['Player_ID']

        cols = ['GAME_MONTH', 'GAME_DAY', 'GAME_YEAR', 'TEAM',
                'OPP', 'H/A', 'WL',
                'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M',
                'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF',
                'PTS',
                'PTS_Binned',
                'PLUS_MINUS']

        df = df[cols]
        df = df.iloc[::-1]
        df.index = np.arange(1, len(df) + 1)

        pts = [1 if pts > 9 else 0 for pts in df['PTS']]
        reb = [1 if pts > 9 else 0 for pts in df['REB']]
        ast = [1 if pts > 9 else 0 for pts in df['AST']]
        stl = [1 if pts > 9 else 0 for pts in df['STL']]
        blk = [1 if pts > 9 else 0 for pts in df['BLK']]

        double_doubles = np.arange(len(df))
        triple_doubles = np.arange(len(df))

        for i in range(len(df)):
            count = 0
            if pts[i] == 1:
                count += 1
            if reb[i] == 1:
                count += 1
            if ast[i] == 1:
                count += 1
            if stl[i] == 1:
                count += 1
            if blk[i] == 1:
                count += 1

            double_doubles = 1 if count >= 2 else 0
            triple_doubles[i] = 1 if count >= 3 else 0

        df['DOUBLE_DOUBLE'] = double_doubles
        df['TRIPLE_DOUBLE'] = triple_doubles

        return df
