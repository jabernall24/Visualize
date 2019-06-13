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

    def get_chart(self, stat, stat_max, season_type="Regular Season"):
        s3 = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

        key = f"Career/{self.player['full_name']}/PlayerCareerStats/{self.player['full_name']}-{self.player['id']}-" \
              f"{season_type}-career_stats_{stat}.png"

        try:
            s3.head_object(Bucket=S3_BUCKET, Key=key)
            return key
        except ClientError as e:
            if e.response['Error']['Code'] != "404":
                print(f"Something went wrong{e.response}")
                return None

        career_stats = PlayerCareerStats(player_id=self.player['id'], per_mode36=self.mode)
        if season_type == "Regular Season":
            career_stats = career_stats.career_totals_regular_season.get_dict()['data'][0]
        elif season_type == "Playoffs":
            career_stats = career_stats.career_totals_post_season.get_dict()['data'][0]
        elif season_type == "College":
            if self.player['full_name'] in NO_COLLEGE:
                return None
            career_stats = career_stats.career_totals_college_season.get_dict()['data']
            if len(career_stats) == 0:
                return None
            career_stats = career_stats[0]
        else:
            print("Error: Only valid types are Regular Season, Playoffs, College")
            return None

        career_stats = self.get_regular_season_stats_dict(career_stats)

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

        # upload to aws
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        img = img_data.read()

        s3 = boto3.resource('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
        s3.Object(S3_BUCKET, S3_KEY).put(ACL='public-read', Body=img, Key=key)

        return key

    def get_path_dict_for(self, season_type):
        return {
            "PTS": self.get_chart(stat="PTS", stat_max=35, season_type=season_type),
            "REB": self.get_chart(stat="REB", stat_max=23, season_type=season_type),
            "AST": self.get_chart(stat="AST", stat_max=12, season_type=season_type),
            "STL": self.get_chart(stat="STL", stat_max=3, season_type=season_type),
            "BLK": self.get_chart(stat="BLK", stat_max=4, season_type=season_type),
            "TOV": self.get_chart(stat="TOV", stat_max=5, season_type=season_type),
            "FG_PCT": self.get_chart(stat="FG_PCT", stat_max=1, season_type=season_type),
            "FT_PCT": self.get_chart(stat="FT_PCT", stat_max=1, season_type=season_type),
            "FG3_PCT": self.get_chart(stat="FG3_PCT", stat_max=1, season_type=season_type),
            "GP": self.get_chart(stat="GP", stat_max=1700, season_type=season_type),
            "GS": self.get_chart(stat="GS", stat_max=1700, season_type=season_type),
        }
