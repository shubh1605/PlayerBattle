from bs4 import BeautifulSoup
import requests	

series_link = "indian-premier-league-2023-1345038"
# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
# series_link = "pakistan-super-league-2022-23-1332128"

team_src =  requests.get("https://www.espncricinfo.com/series/"+series_link+"/squads").text
team_soup = BeautifulSoup(team_src,'lxml')
teams = team_soup.find('div', class_ = "ds-flex ds-space-x-5").find('div', class_ = "ds-bg-fill-content-prime").findAll('div', class_="ds-flex lg:ds-flex-row sm:ds-flex-col lg:ds-items-center lg:ds-justify-between ds-py-2 ds-px-4 ds-flex-wrap odd:ds-bg-fill-content-alternate")
teams_link = []
for t in teams:
    link = t.find('a')['href']
    teams_link.append("https://www.espncricinfo.com"+link)
all_players = {}

for team in teams_link:
    t = " ".join(team.split("/")[-2].split("-")[:-2])
    team_src =  requests.get(team).text
    team_soup = BeautifulSoup(team_src,'lxml')
    teams = team_soup.find('div', class_ = "ds-flex ds-space-x-5").find('div', class_ = "ds-grid lg:ds-grid-cols-2").findAll('a')
    team_players = set()
    for player_links in teams:
        if player_links['href'].startswith("/cricketers"):
            team_players.add(player_links['href'])
    all_players[t] = [" ".join(x.split("/")[-1].split("-")[:-1]) for x in list(team_players)]
    print(all_players[t])
# print(all_players)    


