# -*- coding: utf-8 -*-
"""
@author: Gil Sorek

Season Summary for Fantasy Premier-League (FPL)
"""

import requests
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
        
def get_player_webname(id): return players_stats[id]['web_name']
def get_team_name(id): return team_name[id]

# Settings
league_id = '416585'
highlight_keys = {}

# Pull FPL data
league_data = requests.get(f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/').json()
fpl_data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
last_gw = 1
e = next(event for event in fpl_data['events'] if event['is_current'])
last_gw = e['id']
teams_id_to_name = {team['id']: team['name'] for team in fpl_data['teams']}

# players_stats = {}
# ppp_season = {}
# for el in fpl_data['elements']:
#     players_stats[el['id']] = el
#     ppp_season[el['id']] = el['total_points'] / (el['now_cost'] / 10)
# ppp_season_top3 = sorted(ppp_season.items(), key=lambda item: item[1], reverse=True)[:3]

# league_data = requests.get('https://fantasy.premierleague.com/api/leagues-classic/997095/standings/').json()

weekly_stats = {}
weekly_picks = {}
for manager in league_data['standings']['results']:
    id = manager['entry']
    weekly_stats[id] = {event['event']: event for event in requests.get(f'https://fantasy.premierleague.com/api/entry/{id}/history/').json()['current']}
    weekly_picks[id] = {gw: requests.get(f'https://fantasy.premierleague.com/api/entry/{id}/event/{gw}/picks/').json() for gw in range(1,last_gw+1)}
all_gws_players_stats = {gw: {player['id']: player['stats'] for player in requests.get(f'https://fantasy.premierleague.com/api/event/{gw}/live/').json()['elements']} for gw in range(1,last_gw+1)}

# Setup datasets
team_name, total_points, rank, team_value, top_gw_points, num_transfers, num_hits, bench_points, subs_points, captain_points, best_captain, most_started, most_benched, most_captained, gk_total_points, def_total_points, mid_total_points, fwd_total_points, favorite_team, points_per_team = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
for manager in league_data['standings']['results']:
    id = manager['entry']
    team_name[id] = manager['entry_name']
    total_points[id] = manager['total']
    rank[id] = manager['rank']
    team_value[id] = weekly_stats[id][last_gw]['value']/10
    top_gw_points[id] = 0
    num_transfers[id] = 0
    num_hits[id] = 0
    bench_points[id] = 0
    subs_points[id] = 0
    captain_points[id] = 0
    best_captain[id] = {'points': 0}
    most_started[id] = {'player': 0, "starts": 0}
    most_benched[id] = {'player': 0, "benched": 0}
    most_captained[id] = {'player': 0, "captained": 0}
    gk_total_points[id] = 0
    def_total_points[id] = 0
    mid_total_points[id] = 0
    fwd_total_points[id] = 0
    favorite_team[id] = {id: 0 for id in range(1,21)}
    points_per_team[id] = {id: 0 for id in range(1,21)}

players_stats = {element['id']: element for element in fpl_data['elements']}

for gw in range(1,last_gw+1):
    # Top points
    gw_points = {id: weekly_stats[id][gw]['points'] for id in top_gw_points}
    max_points = max(gw_points.values()); _ = [top_gw_points.update({key: top_gw_points[key] + 1}) for key in gw_points if gw_points[key] == max_points]
    # Number of transfers
    _ = [num_transfers.update({id: num_transfers[id] + weekly_stats[id][gw]['event_transfers']}) for id in num_transfers]
    # Number of hits
    _ = [num_hits.update({id: num_hits[id] + weekly_stats[id][gw]['event_transfers_cost']}) for id in num_hits]
    # Bench points
    _ = [bench_points.update({id: bench_points[id] + weekly_stats[id][gw]['points_on_bench']}) for id in bench_points]
    # Substitutes points
    _ = [subs_points.update({id: subs_points[id] + all_gws_players_stats[gw][sub['element_in']]['total_points']}) for id in subs_points for sub in weekly_picks[id][gw]['automatic_subs']]
    # Captain points
    _ = [captain_points.update({id: captain_points[id] + player['multiplier']*all_gws_players_stats[gw][player['element']]['total_points']}) for id in captain_points for player in weekly_picks[id][gw]['picks'] if player['multiplier'] > 1]
    # Best captain
    _ = [best_captain.update({id: {'gw': gw, 'player': player['element'], 'points': player['multiplier']*all_gws_players_stats[gw][player['element']]['total_points']}}) for id in best_captain for player in weekly_picks[id][gw]['picks'] if player['multiplier']*all_gws_players_stats[gw][player['element']]['total_points'] > best_captain[id]['points']]

for id in weekly_stats.keys():
    # Most starts
    starts = {player['element']: 0 for gw in range(1,last_gw+1) for player in weekly_picks[id][gw]['picks']}
    _ = [starts.update({player['element']: starts[player['element']] + 1}) for gw in range(1,last_gw+1) for player in weekly_picks[id][gw]['picks'] if player['multiplier']>0]
    most_starts = max(starts.values()); _ = [most_started.update({id: {'player': player, 'starts': starts[player]}}) for player in starts if starts[player] == most_starts]
    # Most benched
    benched = {player['element']: 0 for gw in range(1,last_gw+1) for player in weekly_picks[id][gw]['picks']}
    _ = [benched.update({player['element']: benched[player['element']] + 1}) for gw in range(1,last_gw+1) for player in weekly_picks[id][gw]['picks'] if player['multiplier']==0]
    most_bench = max(benched.values()); _ = [most_benched.update({id: {'player': player, 'benched': benched[player]}}) for player in benched if benched[player] == most_bench]
    # Most captained
    captained = {player['element']: 0 for gw in range(1,last_gw+1) for player in weekly_picks[id][gw]['picks']}
    _ = [captained.update({player['element']: captained[player['element']] + 1}) for gw in range(1,last_gw+1) for player in weekly_picks[id][gw]['picks'] if player['multiplier']>1]
    most_captain = max(captained.values()); _ = [most_captained.update({id: {'player': player, 'captained': captained[player]}}) for player in captained if captained[player] == most_captain]
    for week in range(1,gw+1):
        for pick in weekly_picks[id][week]['picks']:
            if pick['multiplier'] > 0:
                favorite_team[id][players_stats[pick['element']]['team']] += 1
                points_per_team[id][players_stats[pick['element']]['team']] += all_gws_players_stats[week][pick['element']]['total_points']*pick['multiplier']
                if players_stats[pick['element']]['element_type'] == 1:
                    gk_total_points[id] += all_gws_players_stats[week][pick['element']]['total_points']*pick['multiplier']
                elif players_stats[pick['element']]['element_type'] == 2:
                    def_total_points[id] += all_gws_players_stats[week][pick['element']]['total_points']*pick['multiplier']
                elif players_stats[pick['element']]['element_type'] == 3:
                    mid_total_points[id] += all_gws_players_stats[week][pick['element']]['total_points']*pick['multiplier']
                else:
                    fwd_total_points[id] += all_gws_players_stats[week][pick['element']]['total_points']*pick['multiplier']
            else:
                break
    
# Prepare data for summary
max_top_gw_points = [key for key, value in top_gw_points.items() if value == max(top_gw_points.values())]
max_transfers = [key for key, value in num_transfers.items() if value == max(num_transfers.values())]
max_hits = [key for key, value in num_hits.items() if value == max(num_hits.values())]
max_bench_points = [key for key, value in bench_points.items() if value == max(bench_points.values())]
max_subs_points = [key for key, value in subs_points.items() if value == max(subs_points.values())]
max_captain_points = [key for key, value in captain_points.items() if value == max(captain_points.values())]
max_best_captain = [key for key, value in best_captain.items() if value['points'] == max(d['points'] for d in best_captain.values())]
max_team_value = [key for key, value in team_value.items() if value == max(team_value.values())]
min_team_value = [key for key, value in team_value.items() if value == min(team_value.values())]
top_favorite_team = {key: {'team': teams_id_to_name[max(inner_dict, key=inner_dict.get)], 'starts': max(inner_dict.values())} for key, inner_dict in favorite_team.items()}
top_points_per_team = {key: {'team': teams_id_to_name[max(inner_dict, key=inner_dict.get)], 'points': max(inner_dict.values())} for key, inner_dict in points_per_team.items()}

# Season Summary
season_summary = ""
season_summary += f"** Summary: {league_data['league']['name']} - GW {gw} **\n"
season_summary += "Standings: " + ' '.join([f"({item['rank']}) {get_team_name(item['entry'])}" for item in league_data['standings']['results'][0:3]]) + "\n------------------------------\n"
season_summary += "Most Highest GW Points: " + ' & '.join(list(map(get_team_name, max_top_gw_points))) + " (" + str(top_gw_points[max(top_gw_points, key=top_gw_points.get)]) + " GWs)" + "\n"
season_summary += "Most Transfers: " + ' & '.join(list(map(get_team_name, max_transfers))) + " (" + str(num_transfers[max(num_transfers, key=num_transfers.get)]) + " Transfers)" + "\n"
season_summary += "Most Hits: " + ' & '.join(list(map(get_team_name, max_hits))) + " (" + str(int(num_hits[max(num_hits, key=num_hits.get)]/4)) + " Hits, -" + str(num_hits[max(num_hits, key=num_hits.get)]) + " Points)" + "\n"
season_summary += "Most Bench Points: " + ' & '.join(list(map(get_team_name, max_bench_points))) + " (" + str(bench_points[max(bench_points, key=bench_points.get)]) + " Points)" + "\n"
season_summary += "Most Substitution Points: " + ' & '.join(list(map(get_team_name, max_subs_points))) + " (" + str(subs_points[max(subs_points, key=subs_points.get)]) + " Points)" + "\n"
season_summary += "Most Captain Points: " + ' & '.join(list(map(get_team_name, max_captain_points))) + " (" + str(captain_points[max(captain_points, key=captain_points.get)]) + " Points)" + "\n"
season_summary += "Best Captain: " + ' & '.join(f"{get_team_name(id)} ({get_player_webname(best_captain[id]['player'])}, {best_captain[id]['points']} Points, GW {best_captain[id]['gw']})" for id in max_best_captain) + "\n"
season_summary += "Highest Team Value: " + ' & '.join(list(map(get_team_name, max_team_value))) + " (" + str(team_value[max(team_value, key=team_value.get)]) + "M £)" + "\n"
season_summary += "Lowest Team Value: " + ' & '.join(list(map(get_team_name, min_team_value))) + " (" + str(team_value[min(team_value, key=team_value.get)]) + "M £)" + "\n"
print(season_summary)

# Graphics
dict_list = [total_points, top_gw_points, num_transfers, num_hits, bench_points, subs_points, captain_points, {id: info['points'] for id, info in best_captain.items()}, team_value, {id: info['starts'] for id, info in most_started.items()}, {id: info['benched'] for id, info in most_benched.items()}, {id: info['captained'] for id, info in most_captained.items()}, {id: info['starts'] for id, info in top_favorite_team.items()}, {id: info['points'] for id, info in top_points_per_team.items()}, {}, gk_total_points, def_total_points, mid_total_points, fwd_total_points]
dict_list_sorted = [dict(sorted(d.items(), key=lambda item: item[1], reverse=False)) for d in dict_list]
dict_list_sorted[0] = {key: total_points[key] for key in sorted(rank, key=lambda x: (rank[x], x), reverse=True)}
titles = [
    "Total Points", "Top Gameweek Scorer", "Transfers Made", "Hits Taken", "Bench Points", "Substitution Points",
    "Captain Points", "Best Captain", "Team Value", "Most Started", "Most Benched", "Most Captained", "Favorite Team (Player Starts)",
    "Most Team Points", "", "Goalkeeper Total Points", "Defender Total Points", "Midfielder Total Points", "Forward Total Points"
]
# Total Points
tp_lower = math.ceil((min(total_points.values())-100) / 100) * 100 if min(total_points.values())>100 else 0
# Transfers
tm_lower = min(num_transfers.values())-2 if min(num_transfers.values())>0 else 0
# Captain Points
cp_lower = math.floor(min(captain_points.values()) / 50) * 50
# Team Value
tv_lower = math.ceil(min(team_value.values())-1)
# Most Started
start_lower = min(entry['starts'] for entry in most_started.values())-5 if min(entry['starts'] for entry in most_started.values())>5 else 0
# Favorite Team
fav_lower = min(entry['starts'] for entry in top_favorite_team.values())-10 if min(entry['starts'] for entry in top_favorite_team.values())>10 else 0
# Team Points
tpts_lower = min(entry['points'] for entry in top_points_per_team.values())-200 if min(entry['points'] for entry in top_points_per_team.values())>200 else 0
# Position Points
gk_lower = math.ceil((min(gk_total_points.values())-10) / 10) * 10
def_lower = math.ceil((min(def_total_points.values())-10) / 10) * 10
mid_lower = math.ceil((min(mid_total_points.values())-10) / 10) * 10
fwd_lower = math.ceil((min(fwd_total_points.values())-10) / 10) * 10
fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(20, 15))
axes = axes.flatten()
for i, (ax, data_dict) in enumerate(zip(axes, dict_list_sorted)):
    if not data_dict:
        ax.axis('off')
        continue
    keys = [get_team_name(key) for key in data_dict.keys()]
    values = list(data_dict.values())
    colors = [highlight_keys[key] if key in highlight_keys else 'skyblue' for key in data_dict.keys()]
    bars = ax.barh(keys, values, color=colors)  
    ax.set_title(titles[i]) 
    for bar in bars:
        width = bar.get_width()
        if width != 0:
            if i+1==8:
                key_id = list(data_dict.keys())[bars.index(bar)]
                captain_info = best_captain.get(key_id, {})
                player_name = get_player_webname(int(captain_info.get('player', '')))
                gw_value = captain_info.get('gw', '')
                bar_label = f'{player_name} ({width} Points, GW {gw_value})'
                ax.text(width/2, bar.get_y() + bar.get_height()/2, f'{player_name} (GW {gw_value})', 
                    va='center', ha='center', color='black', fontsize=10)
            elif i+1==10:
                key_id = list(data_dict.keys())[bars.index(bar)]
                info = most_started.get(key_id, {})
                player_name = get_player_webname(int(info.get('player', '')))
                ax.text((width+start_lower)/2, bar.get_y() + bar.get_height()/2, f'{player_name}', 
                    va='center', ha='center', color='black', fontsize=10)
            elif i+1==11:
                key_id = list(data_dict.keys())[bars.index(bar)]
                info = most_benched.get(key_id, {})
                player_name = get_player_webname(int(info.get('player', '')))
                ax.text(width/2, bar.get_y() + bar.get_height()/2, f'{player_name}', 
                    va='center', ha='center', color='black', fontsize=10)
            elif i+1==12:
                key_id = list(data_dict.keys())[bars.index(bar)]
                info = most_captained.get(key_id, {})
                player_name = get_player_webname(int(info.get('player', '')))
                ax.text(width/2, bar.get_y() + bar.get_height()/2, f'{player_name}', 
                    va='center', ha='center', color='black', fontsize=10)
            elif i+1==13:
                key_id = list(data_dict.keys())[bars.index(bar)]
                info = top_favorite_team.get(key_id, {})
                team = info['team']
                ax.text((width+fav_lower)/2, bar.get_y() + bar.get_height()/2, f'{team}', 
                    va='center', ha='center', color='black', fontsize=10)
            elif i+1==14:
                key_id = list(data_dict.keys())[bars.index(bar)]
                info = top_points_per_team.get(key_id, {})
                team = info['team']
                ax.text((width+tpts_lower)/2, bar.get_y() + bar.get_height()/2, f'{team}', 
                    va='center', ha='center', color='black', fontsize=10)
            if i+1==4:
                ax.text(width, bar.get_y() + bar.get_height()/2, f'-{width}', 
                    va='center', ha='left', color='black', fontsize=10)
            else:
                ax.text(width, bar.get_y() + bar.get_height()/2, f'{width}', 
                    va='center', ha='left', color='black', fontsize=10)
    if i+1 in [2,3,4,6,10,11,12,13]:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if i+1==4:
        x_ticks = ax.get_xticks()
        ax.set_xticklabels([f'-{int(tick)}' if tick != 0 else '0' for tick in x_ticks])
        
    max_value = max(values)
    min_value = min(values)
    label_length_factor = 0.02
    if i+1==1:
        buffer = (max_value-tp_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-tp_lower)
        ax.set_xlim(tp_lower, max_value+buffer)
    elif i+1==3:
        buffer = (max_value-tm_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-tm_lower)
        ax.set_xlim(tm_lower, max_value+buffer)
    elif i+1==7:
        buffer = (max_value-cp_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-cp_lower)
        ax.set_xlim(cp_lower, max_value+buffer)
    elif i+1==9:
        buffer = (max_value-tv_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-tv_lower)
        ax.set_xlim(tv_lower, max_value+buffer)
    elif i+1==10:
        buffer = (max_value-start_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-start_lower)
        ax.set_xlim(start_lower, max_value+buffer)
    elif i+1==13:
        buffer = (max_value-fav_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-fav_lower)
        ax.set_xlim(fav_lower, max_value+buffer)
    elif i+1==14:
        buffer = (max_value-tpts_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-tpts_lower)
        ax.set_xlim(tpts_lower, max_value+buffer)
    elif i+1==16:
        buffer = (max_value-gk_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-gk_lower)
        ax.set_xlim(gk_lower, max_value+buffer)
    elif i+1==17:
        buffer = (max_value-def_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-def_lower)
        ax.set_xlim(def_lower, max_value+buffer)
    elif i+1==18:
        buffer = (max_value-mid_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-mid_lower)
        ax.set_xlim(mid_lower, max_value+buffer)
    elif i+1==19:
        buffer = (max_value-fwd_lower) * 0.05 + label_length_factor * len(str(max_value)) * (max_value-fwd_lower)
        ax.set_xlim(fwd_lower, max_value+buffer)
    else:
        buffer = max_value * 0.05 + label_length_factor * len(str(max_value)) * max_value
        ax.set_xlim(0, max_value + buffer)
for j in range(len(dict_list_sorted), len(axes)):
    fig.delaxes(axes[j])
plt.suptitle(f"Season Summary - Gameweeks 1-{last_gw}", fontsize=24)
plt.tight_layout()
plt.savefig(f"Season_Summary_GW{last_gw}.png", format="png", bbox_inches="tight")
