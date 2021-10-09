# Rift Stats - LoL Stats Discord Bot

# Current Features:
# Live Game Lookup
# Individual Player Lookup


import discord
from riotwatcher import LolWatcher, ApiError
import requests

# Setup
lol_watcher = LolWatcher("your Riot API key here")
my_region = 'na1'

# GET CHAMPION NAME FROM ID

versions = lol_watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
champ_list = lol_watcher.data_dragon.champions(champions_version)
champ_dict = {}
for champ in champ_list['data']:
    champ_dict[champ] = champ_list['data'][champ]['key']


def id_to_champ(id):
    for champions in champ_dict:
        if int(champ_dict.get(champions)) == id:
            return champions


def current_game(name):
    me = lol_watcher.summoner.by_name(my_region, name)  # provides id / account id / puuid / name

    try:
        s = lol_watcher.spectator.by_summoner(my_region, me['id'])
    except requests.exceptions.HTTPError:
        final = name + " is not currently in a game!"
        return final

    # blue side is id 100 (first 5 in list)
    players = []
    champion = []
    ranked_tier = []
    division = []
    LP = []
    GP = []
    WR = []

    for participants in s['participants']:
        players.append((participants['summonerName']))
        champion.append(int((participants['championId'])))

    for p in players:
        watcher = lol_watcher.summoner.by_name(my_region, p)
        player_data = lol_watcher.league.by_summoner(my_region, watcher['id'])
        if len(player_data) == 0:
            ranked_tier.append("UNRANKED")
            division.append("N/A")
            LP.append("N/A")
            GP.append("N/A")
            WR.append("N/A")
        else:
            if player_data[0]['queueType'] == 'RANKED_SOLO_5x5':
                ranked_tier.append(player_data[0]['tier'])
                division.append(player_data[0]['rank'])
                LP.append(player_data[0]['leaguePoints'])
                num_of_wins = float(player_data[0]['wins'])
                num_of_losses = float(player_data[0]['losses'])
                total_games = int(num_of_wins + num_of_losses)
                GP.append(total_games)
                WR.append(num_of_wins / total_games)
            elif player_data[1]['queueType'] == 'RANKED_SOLO_5x5':
                ranked_tier.append(player_data[1]['tier'])
                division.append(player_data[1]['rank'])
                LP.append(player_data[1]['leaguePoints'])
                num_of_wins = float(player_data[1]['wins'])
                num_of_losses = float(player_data[1]['losses'])
                total_games = int(num_of_wins + num_of_losses)
                GP.append(total_games)
                WR.append(num_of_wins / total_games)
            else:
                ranked_tier.append("UNRANKED")
                division.append("N/A")
                LP.append("N/A")
                GP.append("N/A")
                WR.append("N/A")

    team = "*********BLUE TEAM***********\n"
    for i in range(0, len(players)):
        if i == 5:
            team += "*********RED TEAM***********\n"
        if i == 4:
            if ranked_tier[i] != "UNRANKED":
                team += players[i] + " (" + id_to_champ(champion[i]) + "): " + ranked_tier[i] + " " + division[
                    i] + " - " + str(LP[i]) + " LP, " + str(GP[i]) + " games (" + str(round((100 * WR[i]), 2)) + "% WR)\n\n"
            else:
                team += players[i] + " (" + id_to_champ(champion[i]) + "): " + ranked_tier[i] + " " + division[
                    i] + " - " + LP[i] + " LP, " + GP[i] + " games (" + WR[i] + "% WR)\n\n"
        else:
            if ranked_tier[i] != "UNRANKED":
                team += players[i] + " (" + id_to_champ(champion[i]) + "): " + ranked_tier[i] + " " + division[i] + " - " + str(LP[i]) + " LP, " + str(GP[i]) + " games (" + str(round((100 * WR[i]), 2)) + "% WR)\n"
            else:
                team += players[i] + " (" + id_to_champ(champion[i]) + "): " + ranked_tier[i] + " " + division[
                    i] + " - " + LP[i] + " LP, " + GP[i] + " games (" + WR[i] + "% WR)\n"
    return team


def player_lookup(name):
    player = lol_watcher.summoner.by_name(my_region, name)
    player_details = lol_watcher.league.by_summoner(my_region, player['id'])
    if len(player_details) == 0:
        tier = "UNRANKED"
    else:
        if player_details[0]['queueType'] == 'RANKED_SOLO_5x5':
            tier = player_details[0]['tier']
            division = player_details[0]['rank']
            lp = player_details[0]['leaguePoints']
            wins = player_details[0]['wins']
            losses = player_details[0]['losses']
            gp = wins + losses
            wr = float(wins) / gp
        elif player_details[1]['queueType'] == 'RANKED_SOLO_5x5':
            tier = player_details[1]['tier']
            division = player_details[1]['rank']
            lp = player_details[1]['leaguePoints']
            wins = player_details[1]['wins']
            losses = player_details[1]['losses']
            gp = wins + losses
            wr = float(wins) / gp
        else:
            tier = "UNRANKED"
    if tier == "UNRANKED":
        stats = name + ": UNRANKED"
    else:
        stats = name + ": " + tier + " " + division + " - " + str(lp) + " LP, " + str(gp) + " games " + str(wins) + "W " + str(losses) + "L " + "(" + str(round((100 * wr), 2)) + "% WR)"
    return stats


# Discord Implementation


client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as " + str(client.user))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!cg"):
        name = message.content.split(' ')
        if len(name) > 2:
            for i in range(1, len(name)):
                if i == 1:
                    new_name = name[i]
                else:
                    new_name += " " + name[i]
        else:
            new_name = name[1]
        await message.channel.send(current_game(new_name))

    if message.content.startswith("!stats"):
        name = message.content.split(' ')
        if len(name) > 2:
            for i in range(1, len(name)):
                if i == 1:
                    new_name = name[i]
                else:
                    new_name += " " + name[i]
        else:
            new_name = name[1]
        await message.channel.send(player_lookup(new_name))

client.run("your discord bot token here")

