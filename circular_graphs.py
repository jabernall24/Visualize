from flask import Flask, render_template, request, redirect
from PIL import Image
from nba_api.stats.static import players
import json
from nba_api.stats.endpoints import PlayerCareerStats, CommonPlayerInfo
from pprint import pprint
from matplotlib import pyplot as plt
import matplotlib as mpl
import os
import datetime
from constants import TO_MONTH
import io
import boto3
from botocore.exceptions import ClientError
from config import S3_BUCKET, S3_KEY, S3_SECRET
from constants import TEAM_COLORS, NO_COLLEGE
import requests
from multiprocessing.pool import ThreadPool


class PlayerCareerStatsGraphs:

    def __init__(self, player, mode="PerGame"):
        self.player = player
        self.mode = mode

    @staticmethod
    def get_regular_season_stats_dict(stats):
        organized_stats = {
            "GP": stats[3],
            "GS": stats[4],
            "FG_PCT": stats[8],
            "FG3_PCT": stats[11],
            "FT_PCT": stats[14],
            "REB": stats[17],
            "AST": stats[18],
            "STL": stats[19],
            "BLK": stats[20],
            "TOV": stats[21],
            "PTS": stats[23],
        }
        return organized_stats

    def get_all_chart(self):
        a = datetime.datetime.now()
        stats = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FT_PCT', 'FG3_PCT', 'GP', 'GS']
        stats_max = [35, 23, 12, 3, 4, 5, 1, 1, 1, 1700, 1700]
        season_types = ['Regular Season', 'Playoffs', 'College']
        STATS_HEADERS = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        print("Got here")
        player_career_stats = PlayerCareerStats(player_id=self.player['id'], per_mode36=self.mode)
        print("End of api call")
        b = datetime.datetime.now()
        print(f"Api call took: {b - a}")
        regular_paths = list()
        playoff_paths = list()
        college_paths = list()

        for season_type in season_types:
            if season_type == 'Regular Season':
                career_stats = player_career_stats.career_totals_regular_season.get_dict()['data']
                if len(career_stats) == 0:
                    continue
                career_stats = career_stats[0]
            elif season_type == "Playoffs":
                career_stats = player_career_stats.career_totals_post_season.get_dict()['data']
                if len(career_stats) == 0:
                    continue
                career_stats = career_stats[0]
            else:
                career_stats = player_career_stats.career_totals_college_season.get_dict()['data']
                if len(career_stats) == 0:
                    continue
                career_stats = career_stats[0]

            career_stats = self.get_regular_season_stats_dict(career_stats)

            for stat, stat_max in zip(stats, stats_max):
                key = f"Career/{self.player['full_name']}/PlayerCareerStats/{self.player['full_name']}-" \
                      f"{self.player['id']}-{season_type}-career_stats_{stat}.png"
                if season_type == 'Regular Season':
                    regular_paths.append(key)
                elif season_type == "Playoffs":
                    playoff_paths.append(key)
                else:
                    college_paths.append(key)
                # create data
                size_of_groups = [career_stats[stat], stat_max - career_stats[stat]]
                colors = ["purple", "white"]

                # Create a pieplot
                fig, ax = plt.subplots()
                ax.pie(size_of_groups, colors=colors)
                plt.title(stat)

                # add a circle at the center
                my_circle = plt.Circle((0, 0), 0.7, color='white')

                p = plt.gcf()
                p.gca().add_artist(my_circle)
                p.text(0.45, 0.5, career_stats[stat])

                # Prepping images to upload
                img_data = io.BytesIO()
                plt.savefig(img_data, format='png')
                img_data.seek(0)
                img = img_data.read()
                plt.close('all')

                s3 = boto3.resource('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
                s3.Object(S3_BUCKET, S3_KEY).put(ACL='public-read', Body=img, Key=key)
        b = datetime.datetime.now()
        print(f"This took: {b - a}")
        return [regular_paths, playoff_paths, college_paths]
