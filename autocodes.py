import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import csv


class CarCodesScraper:
    def __init__(self):
        with open('autocodes.csv', "w") as fp:
            writer = csv.writer(fp)
            for i in self.scrape():
                writer.writerow((i['code'], i['short_description'], i['meaning'], i['symptoms'], i['causes'],
                                 i['solutions'], i['link']))

    def scrape(self):
        for l in ('u', 'b', 'c'):
            for i in range(1, 0x3500):
                link = "https://www.autocodes.com/%s%s.html" % (l, str(hex(i))[2:].zfill(4))
                try:
                    response = requests.get(link)
                except ConnectionError:
                    continue
                if response.status_code != 200:
                    continue
                try:
                    ret = self.process(response.text)
                    print("success on %s%s" % (l, str(hex(i))[2:].zfill(4)))
                except AttributeError:
                    print("Error on %s%s" % (l, str(hex(i))[2:].zfill(4)))
                    continue
                ret['link'] = link
                yield ret

    @staticmethod
    def process(page):
        results = {}
        text = BeautifulSoup(page).find("h1", {'class': 'code'}).text.strip()
        if len(text) < 5:
            raise AttributeError('Nothing')
        results['code'] = text.split(' - ')[0]
        results['short_description'] = ' - '.join(
            BeautifulSoup(page).find("h1", {'class': 'code'}).text.split(' - ')[1:])
        if page.find("Possible causes") != -1:
            temp = page[page.find("Possible causes"):]
            temp = temp[:temp.find('What does this mean?')]
            results['causes'] = BeautifulSoup(temp).text.strip()
        else:
            results['causes'] = ''

        if page.find("Possible symptoms") != -1:
            temp = page[page.find("Possible symptoms"):]
            if -1 != min(temp.find('<div class="desc">'), temp.find('Advertisement')):
                temp = temp[:min(temp.find('<div class="desc">'), temp.find('Advertisement'))]
            else:
                temp = temp[:max(temp.find('<div class="desc">'), temp.find('Advertisement'))]
            results['symptoms'] = BeautifulSoup(temp).text.strip()
        else:
            results['symptoms'] = ''

        if page.find("%s Description" % results['code']) != -1:
            temp = page[page.find("%s Description" % results['code']):]
            if -1 != min(temp.find('<div class="desc">'), temp.find('Advertisement')):
                temp = temp[:min(temp.find('<div class="desc">'), temp.find('Advertisement'))]
            else:
                temp = temp[:max(temp.find('<div class="desc">'), temp.find('Advertisement'))]
            results['meaning'] = BeautifulSoup(temp).text.strip()
        else:
            results['meaning'] = ''
        results['solutions'] = ''
        return results


CarCodesScraper()
