from bs4 import BeautifulSoup
import requests	

# series_link = "indian-premier-league-2023-1345038"
# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
series_link = "pakistan-super-league-2022-23-1332128"

matches_src =  requests.get("https://www.espncricinfo.com/series/"+series_link+"/match-schedule-fixtures-and-results").text
matches_soup = BeautifulSoup(matches_src,'lxml')

matches_data = matches_soup.find('div', class_ = "ds-w-full ds-bg-fill-content-prime ds-overflow-hidden ds-rounded-xl ds-border ds-border-line").find('div', class_ = "ds-p-0").findAll('div', class_ = "ds-p-4")
matches_link = []

all_matches_points = {}

for match in matches_data:
    temp = match.find('div', class_ = "ds-flex").find('div', class_ = "ds-grow ds-px-4 ds-border-r ds-border-line-default-translucent").find('a').attrs['href']
    temp_list = temp.split('/')
    matches_link.append(temp_list[3])

print(matches_link)

# all_players = []
# for match in matches_link[0:1]:
#     source = requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match+"/full-scorecard").text
#     player_src = requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match+"/match-playing-xi").text
#     soup=BeautifulSoup(source,'lxml')
#     soup2 = BeautifulSoup(player_src, 'lxml')
#     points = {}
#     players = soup2.find('table', class_ = 'ds-table')
#     pls = players.find('tbody', class_ = "").findAll('tr')

#     for pl in pls[:11]:
#         x = pl.findAll('td')
#         y = x[1].find('a').attrs['href'].split('/')
#         z = y[2].split('-')[:-1]
#         points[" ".join(z)] = 0
#         y = x[2].find('a').attrs['href'].split('/')
#         z = y[2].split('-')[:-1]
#         points[" ".join(z)] = 0
#     tables = soup.findAll("table",class_ = 'ds-w-full')
#     for table in tables:
#         tbody = table.find("tbody")
#         trs = tbody.findAll("tr", class_ = "")
#         tp = []
#         for tr in trs:
#             td = tr.findAll("td")
#             if len(td) == 8:
#                 name_temp = td[0].find('a').attrs['href'].split('/')
#                 name = name_temp[2].split('-')[:-1]
#                 name = (" ".join(name)).lower()
#                 runs = int(td[2].find('strong').text)
#                 if(name not in points):
#                     points[name] = 0
#                 points[name] += runs
#             elif len(td) > 8:
#                 name_temp = td[0].find('a').attrs['href'].split('/')
#                 name = name_temp[2].split('-')[:-1]
#                 name = (" ".join(name)).lower()
#                 wicks = int(td[4].find('strong').text)
#                 if(name not in points):
#                     points[name] = 0
#                 points[name] += (wicks*25)
#     all_matches_points[match] = points
# print(all_matches_points)