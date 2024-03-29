# -*- coding: utf-8 -*-
import whois
from time import sleep
import csv
import requests
from bs4 import BeautifulSoup

print(whois.whois("https://arenavision.cc"))

class Event:
    def __init__(self, date, time, sport, competition, event, channels):
    
        self.date = date
        self.time = time
        self.sport = sport
        self.competition = competition
        self.event = event
        self.channels = channels
    
    
class Channel:
    def __init__(self, channel, languaje, aceStream):
        self.channel = channel
        self.languaje = languaje
        self.aceStream = aceStream
        
        
def getHTML(page): 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    html = requests.get("https://arenavision.cc" + page, headers=headers)
    return html


def getMenuLinks():
    html = getHTML("")
    content = BeautifulSoup(html.content)
    menu = content.find(id="navigation")
    links = menu.find_all('a')
    cookie = html.cookies.get_dict()
    return links


def getAceStreamLink(page):
    result = ""
    html = getHTML(page)
    content = BeautifulSoup(html.content)
    links = content.find_all('a')
    for link in links:
        if "acestream://" in link.get('href'):
            result = link.get('href')
    return result


def getEvents(page, mapLinks):
    result = []
    
    html = getHTML(page)
    content = BeautifulSoup(html.content)
    main = content.find(id="main")
    table = main.find('table')
    rows = table.find_all('tr')

    firstRow = True;

    for row in rows:
        columns = row.find_all('td')

        if not firstRow and len(columns) == 6:
            #<td class="auto-style12">DAY</td>
            date = columns[0].text
            #<td class="auto-style12">TIME</td>
            time = columns[1].text
            #<td class="auto-style12">SPORT</td>
            sport = columns[2].text
            #<td class="auto-style12">COMPETITION</td>
            competition = columns[3].text.replace("\n", "")
            #<td class="auto-style12">EVENT</td>
            event = columns[4].text
            #<td class="auto-style12">LIVE</td>
            channels = getChannels(columns[5].text, mapLinks)
            
            result.append(Event(date, time, sport, competition, event, channels))
        
        firstRow = False; 
        
    return result


def getChannels(live, mapLinks): 
    result = []
    infoChannels = live.split("\n")
    
    for info in infoChannels:
        
        channelsAndLanguaje = info.split(' ')
        
        if len(channelsAndLanguaje) == 2:
            languaje = channelsAndLanguaje[1].replace("[", "").replace("]", "")
            channels = channelsAndLanguaje[0].split('-')
            
            if len(channels) == 1:
                aceStream = mapLinks[channels[0]]
                result.append(Channel(channels[0], languaje, aceStream))
            elif len(channels) == 2:
                aceStream = mapLinks.get(channels[0])
                for num in range(int(channels[0]),int(channels[1])+ 1): 
                    result.append(Channel(num, languaje, aceStream))    
            
    return result     


links = getMenuLinks()

mapLinks = {}
eventsGuideURL = "";

for link in links:
    
    if 'ArenaVision' in link.text:
        aceStreamLink = getAceStreamLink(link.get('href'))
        channelNumber = link.text.replace("ArenaVision ", "")
        mapLinks[channelNumber] = (aceStreamLink)
        sleep(0.5)
    elif 'EVENTS GUIDE' in link.text:
        eventsGuideURL = link.get('href')   
        
        
        
events = getEvents(eventsGuideURL, mapLinks)


with open('EnlacesAceStreamArenavision.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["Channel", "Date", "Time", "Sport", "Competition", "Event", "Languaje", "AceStream"])
    for event in events:
        for channel in event.channels:
            spamwriter.writerow([channel.channel, event.date, event.time, event.sport, event.competition, event.event, channel.languaje, channel.aceStream])
            
            
with open('EnlacesAceStreamArenavision.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        print(', '.join(row))            