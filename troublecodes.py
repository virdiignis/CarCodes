import requests
from bs4 import BeautifulSoup
import csv
from multiprocessing import Pool
from re import compile as com


class CarCodesScraper:
    def __init__(self):
        links = []
        for i in ('', '1', '2', '3'):
            x = requests.get("http://www.troublecodes.net/p%scodes/" % i)
            b = BeautifulSoup(x.text)
            links.extend([a['href'] for a in b.find_all('a', {'href': com("http://www.troublecodes.net/p*")})])

        print("Starting pool")
        p = Pool(processes=4)
        with open('troublecodes.csv', 'w') as fp:
            writer = csv.writer(fp)
            for res in p.imap_unordered(self.scrape, links):
                writer.writerow(res)
                print("Succesfully written %s" % res[0])

    @staticmethod
    def scrape(link: str) -> list:
        response = requests.get(link).text
        ret = [link.split('/')[-2], BeautifulSoup(response).select("td:nth-of-type(2)")[0].text]

        def find(text):
            temp = response.find(text)
            if temp != -1:
                code = response[temp:]
                code = code[:code[4:].find("<h2>")+4]
                ret.append(' '.join([tag.text for tag in BeautifulSoup(code).find_all('p')]))
            else:
                ret.append('')

        find("<h2>What Does ")
        find("<h2>Symptoms of ")
        find("<h2>Common Causes of ")
        find("<h2>Troubleshooting ")
        ret.append(link)
        return ret


CarCodesScraper()
