from bs4 import BeautifulSoup
import requests	
# series_link = "indian-premier-league-2023-1345038"
# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
series_link = "pakistan-super-league-2022-23-1332128"

match_link = "quetta-gladiators-vs-islamabad-united-13th-match-1354936"

live_match_src =  requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match_link+"/live-cricket-score").text
live_score = BeautifulSoup(live_match_src,'lxml')

matches_data = live_score.find('table', class_ = "ds-w-full").findAll('tbody', class_ = "ds-text-right")
batting = []
bowling = []
if matches_data[0] != None:
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

if matches_data[1] != None:
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