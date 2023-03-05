from bs4 import BeautifulSoup
import requests	
# series_link = "indian-premier-league-2023-1345038"
# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
series_link = "pakistan-super-league-2022-23-1332128"
# series_link = "women-s-premier-league-2022-23-1348825"


# https://www.espncricinfo.com/series/women-s-premier-league-2022-23-1348825/royal-challengers-bangalore-women-vs-delhi-capitals-women-2nd-match-1358930/live-cricket-score
match_link = "islamabad-united-vs-quetta-gladiators-21st-match-1354944"
# match_link = "royal-challengers-bangalore-women-vs-delhi-capitals-women-2nd-match-1358930"

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

print(batting)    
print(bowling)
# print(len(matches_data))