from bs4 import BeautifulSoup
import requests	
# series_link = "indian-premier-league-2023-1345038"
# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
# series_link = "pakistan-super-league-2022-23-1332128"
series_link = "women-s-premier-league-2022-23-1348825"


# https://www.espncricinfo.com/series/women-s-premier-league-2022-23-1348825/royal-challengers-bangalore-women-vs-delhi-capitals-women-2nd-match-1358930/live-cricket-score
# match_link = "islamabad-united-vs-quetta-gladiators-21st-match-1354944"
match_link = "delhi-capitals-women-vs-up-warriorz-women-5th-match-1358933"

live_match_src =  requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match_link+"/live-cricket-score").text
live_score = BeautifulSoup(live_match_src,'lxml')

matches_data = live_score.find('table', class_ = "ds-w-full").findAll('tbody', class_ = "ds-text-right")
batting = []
bowling = []
if len(matches_data) > 0:
    bat_scores = matches_data[0].findAll('tr')
    for i in range(len(bat_scores)):
        batsman_details = []
        if bat_scores[i] != None:
            batter = bat_scores[i].findAll('td')
            batsman_details.append(" ".join(batter[0].find('a')['href'].split('/')[-1].split('-')[:-1]))
            batsman_details.append(batter[1].find('strong').text)
            batsman_details.append(batter[2].text)
            batsman_details.append(batter[3].text)
            batsman_details.append(batter[4].text)
        batting.append(batsman_details)

if len(matches_data) > 1:
    bowl_scores = matches_data[1].findAll('tr')
    for i in range(len(bowl_scores)):
        bowler_details = []
        if bowl_scores[i] != None:
            bowler = bowl_scores[i].findAll('td')
            bowler_details.append(" ".join(bowler[0].find('a')['href'].split('/')[-1].split('-')[:-1]))
            bowler_details.append(bowler[1].text)
            bowler_details.append(bowler[2].text)
            bowler_details.append(bowler[3].text)
            bowler_details.append(bowler[4].text)
        bowling.append(bowler_details)

team_scores = live_score.find('div', class_ = "ds-flex ds-flex-col ds-mt-3 md:ds-mt-0 ds-mt-0 ds-mb-1").findAll('div', class_ = "ci-team-score")
team_updates = {}
if len(team_scores) > 0:
    team1_name = team_scores[0].find('div', class_ = "ds-flex ds-items-center ds-min-w-0 ds-mr-1")['title']
    if team_scores[0].find('span', class_ = "ds-text-compact-s ds-mr-0.5") != None:
        t1_overs = team_scores[0].find('span', class_ = "ds-text-compact-s ds-mr-0.5").text
    if team_scores[0].find('strong') != None:
        t1_score = team_scores[0].find('strong').text
    team_updates[team1_name] = [t1_overs, t1_score]
    

if len(team_scores) > 1:
    team2_name = team_scores[1].find('div', class_ = "ds-flex ds-items-center ds-min-w-0 ds-mr-1")['title']
    t2_overs = None
    t2_score = None
    if team_scores[1].find('span', class_ = "ds-text-compact-s ds-mr-0.5") != None:
        t2_overs = team_scores[1].find('span', class_ = "ds-text-compact-s ds-mr-0.5").text
    if team_scores[1].find('strong') != None:
        t2_score = team_scores[1].find('strong').text
    team_updates[team2_name] = [t2_overs, t2_score]

print(team_updates)
print(batting)    
print(bowling)
# print(len(matches_data))