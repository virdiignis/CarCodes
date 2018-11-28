import requests
from bs4 import BeautifulSoup
import csv
from multiprocessing import Pool


class CarCodesScraper:
    """
    Scrapes obd-codes.com and autocodes.com
    """

    def __init__(self):
        with open('obd-codes.csv', "w") as fp:
            writer = csv.writer(fp)
            p = Pool(processes=8)
            for i in p.imap_unordered(self.process, range(1, 0x3500)):
                if i is not None:
                    writer.writerow(i)
                    print("Succesfully written %s" % i[0])

    @staticmethod
    def process(code_nr):
        code = 'P' + str(hex(code_nr))[2:].zfill(4)
        link = "https://www.obd-codes.com/%s" % code
        response = requests.get(link)
        if response.status_code != 200:
            print(link)
            print(response.status_code)
            return None
        bs = BeautifulSoup(response.text)
        results = [code]
        try:
            results.append(bs.find('p', {'class': 'tcode'}).text.strip())
        except AttributeError:
            results.append('')

        def search(*texts):
            pos = max((response.text.find(text) for text in texts))
            if pos != -1:
                section = response.text[pos:].strip()
                section = section[:section[4:].find("<h2>")+4]
                results.append(' '.join([tag.text.strip() for tag in BeautifulSoup(section).find_all('p')]))
            else:
                results.append('')

        search("<h2>What does that mean?", "Trouble Code Technical Description")
        search("<h2>Symptoms", "<h2>Potential Symptoms", "<h2>Code Severity")
        search("<h2>Potential Causes", "<h2>Causes")
        search("<h2>Diagnostic and Repair Procedures", "<h2>Possible Solutions")
        results.append(link)
        return results


CarCodesScraper()
