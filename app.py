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
from circular_graphs import PlayerCareerStatsGraphs
from bar_graphs import BarGraph
import mpld3
import boto3
from config import S3_BUCKET, S3_KEY, S3_SECRET


mpl.rcParams.update({'font.size': 24})

app = Flask(__name__)


@app.route('/load/plots')
def load_plots():
    player = {
        "id": request.args.get('id'),
        "full_name": request.args.get('name')
    }
    a = datetime.datetime.now()
    s3 = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

    key = f"Career/{player['full_name']}/PlayerCareerStats"

    objects = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=key)
    if 'Contents' in objects:
        paths = [obj['Key'] for obj in objects['Contents']]
        regular_season = list()
        playoffs = list()
        college = list()
        for path in paths:
            if 'Regular Season' in path:
                regular_season.append(path)
            elif 'Playoffs' in path:
                playoffs.append(path)
            elif 'College' in path:
                college.append(path)
        b = datetime.datetime.now()
        print(f"It took {b - a}")
        return json.dumps([regular_season, playoffs, college])

    career_stats = PlayerCareerStatsGraphs(player=player).get_all_chart()
    return json.dumps(career_stats)


@app.route('/load/headers')
def load_headers():
    player_id = request.args.get('id')
    common_player = CommonPlayerInfo(player_id=player_id).common_player_info.get_dict()['data'][0]

    team = f"{common_player[20]} {common_player[17]}" if common_player[17] != "" else "No Team/Retired"

    header_stats = {
        "Years Pro": common_player[12],
        "Position": common_player[14],
        "Jersey": common_player[13],
        "Team": team,
        "Draft Year": common_player[27],
        "Draft Pick": f"Round {common_player[28]} Pick {common_player[29]}",
        "Born": transform_date(common_player[6]),
        "Height": common_player[10],
        "Weight": f"{common_player[11]} lbs",
        "Age": get_age_from_date(common_player[6]),
        "Pro": f"{common_player[22]} - {common_player[23]}",
    }
    return json.dumps(header_stats)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/players/list')
def get_players():
    text = request.args.get('name')
    all_players = players.find_players_by_full_name(text)
    return json.dumps(all_players)


@app.route('/players/<name>/stats')
def player_career_stats(name):
    player = players.find_players_by_full_name(name)[0]

    # career_stats = PlayerCareerStatsGraphs(player=player)
    # common_player = CommonPlayerInfo(player_id=player['id']).common_player_info.get_dict()['data'][0]
    #
    # team = f"{common_player[20]} {common_player[17]}" if common_player[17] != "" else "No Team/Retired"
    #
    # header_stats = {
    #     "Years Pro": common_player[12],
    #     "Position": common_player[14],
    #     "Jersey": common_player[13],
    #     "Team": team,
    #     "Draft Year": common_player[27],
    #     "Draft Pick": f"Round {common_player[28]} Pick {common_player[29]}",
    #     "Born": transform_date(common_player[6]),
    #     "Height": common_player[10],
    #     "Weight": f"{common_player[11]} lbs",
    #     "Age": get_age_from_date(common_player[6]),
    #     "Pro": f"{common_player[22]} - {common_player[23]}",
    # }
    # a = datetime.datetime.now()
    # regular_season_img = career_stats.get_path_dict_for(season_type="Regular Season")
    # b = datetime.datetime.now()
    # print(f"Regular season takes {b - a}")
    # a = datetime.datetime.now()
    # playoffs_img = career_stats.get_path_dict_for(season_type="Playoffs")
    # b = datetime.datetime.now()
    # print(f"Playoffs takes {b - a}")
    # a = datetime.datetime.now()
    # college_img = career_stats.get_path_dict_for(season_type="College")
    # b = datetime.datetime.now()
    # print(f"College takes {b - a}")

    return render_template('player_home.html',
                           player=player,)
                           # regular_season_img_path=regular_season_img,
                           # playoffs_img_path=playoffs_img,
                           # college_img_path=college_img,)
                           # header_stats=header_stats)


@app.route('/players/<name>/stats/circular-bar-graphs')
def another(name):
    return name


@app.route('/players/<name>/stats/bar-graphs/points-binned')
def points_binned(name):
    img = BarGraph(player_name=name).games_with_x_amount_of_points(season="2016-17", season_type="Regular Season")
    return render_template('show_img.html', img=img)


def transform_date(date):
    temp = date.split('-')
    new_date = f"{TO_MONTH[int(temp[1])]} {temp[2][:2]}, {temp[0]}"
    return new_date


def get_age_from_date(date):
    temp = date.split('-')
    b_day = datetime.datetime.strptime(f"{temp[1]}-{temp[2][:2]}-{temp[0]}", "%m-%d-%Y")
    days = datetime.datetime.now() - b_day

    return f"{int(days.days / 365)} yrs"


if __name__ == '__main__':
    app.run()
