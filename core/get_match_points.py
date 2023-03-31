from bs4 import BeautifulSoup
import requests	


points = {}
match_link = "gujarat-titans-vs-chennai-super-kings-1st-match-1359475"
series_link = "indian-premier-league-2023-1345038"
# series_link = "icc-men-s-t20-world-cup-2022-23-1298134"
# series_link = "pakistan-super-league-2022-23-1332128"
source = requests.get("https://www.espncricinfo.com/series/"+series_link+"/"+match_link+"/full-scorecard").text
soup=BeautifulSoup(source,'lxml')

tables = soup.findAll("table",class_ = 'ds-w-full')

for table in tables[:4]:
    tbody = table.find("tbody")
    trs = tbody.findAll("tr", class_ = "")

    thead = table.find("thead").find("tr").find("th").text
    
    tp = []
    for tr in trs:
        td = tr.findAll("td")
        
        if thead=="BATTING" and len(td) > 6:
            name_temp = td[0].find('a').attrs['href'].split('/')
            name = name_temp[2].split('-')[:-1]
            name = (" ".join(name)).lower()
            runs = int(td[2].find('strong').text)
            if(name not in points):
                points[name] = [0.0,0.0,0.0]
            points[name][0] += runs
            points[name][2] += runs


        elif thead == "BOWLING":
            name_temp = td[0].find('a').attrs['href'].split('/')
            name = name_temp[2].split('-')[:-1]
            name = (" ".join(name)).lower()
            wicks = int(td[4].find('strong').text)
            if(name not in points):
                points[name] = [0.0,0.0,0.0]
            points[name][1] += (wicks*25)
            points[name][2] += (wicks*25)

print(points)