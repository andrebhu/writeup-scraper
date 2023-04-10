import re
import sys
import json
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

def getOriginalWriteup(url):
    # /writeup/12345
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    original_writeup = url
    for e in soup(text=re.compile('Original writeup')):
        original_writeup = e.parent.parent.find_all('a')[0].attrs['href']
   
    return original_writeup


def getChallengeInfo(url):
    # /task/12345
    links = []
    
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    for tr in soup.find_all('tr')[1:]:
        link = tr.find_all('a')[0].attrs['href']
        links.append('https://ctftime.org' + link)

    tags = []
    spans = soup.find_all('span', class_="label label-info")
    for s in spans:
        tags.append(s.text)

    return links, tags


def getTasks(url):
    # /event/12345/tasks
    tasks = {}

    r = scraper.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    for tr in soup.find_all('tr')[1:]:        
        content = tr.text.split('\n')
        link = tr.find_all('a')[0].attrs['href']
        name = content[0]
        num_writeups = content[-1]
        
        if int(num_writeups) > 0:
            links, tags = getChallengeInfo('https://ctftime.org' + link)
            tasks[name] = {
                'links': links,
                'tags': tags
            }
    return tasks


def main():
    try:
        url = sys.argv[1]
    except:
        print('Usage: python script.py <url>')
        return

    if not re.search(r'https://ctftime.org/event/\d+/tasks/', url):
        print('Invalid URL, should be in the format: https://ctftime.org/event/12345/tasks/')
        return

    print("Getting tasks from: " + url)
    tasks = getTasks(url)
    
    print("Getting info for each task...")
    for k, v in tasks.items():
        links = []

        for l in v['links']:
            links.append(getOriginalWriteup(l))

        tasks[k]['links'] = links

    print("Writing to out.json")
    with open('out.json', 'w') as f:
        json.dump(tasks, f, indent=4)


if __name__ == '__main__':
    main()