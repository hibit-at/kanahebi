import requests
from bs4 import BeautifulSoup
import pandas as pd

data = pd.read_csv('data.csv',index_col=0)
songs = data.columns[1:]
scraping_range = 10
for name,url in zip(data.index.values,data.ScoreSaberID):
    r = requests.get(url)
    t = r.text
    s = BeautifulSoup(t,'html.parser')
    print("scraping {} #debug".format(name))
    for p in range(1,scraping_range+1):
        url = '{}&page={}&sort=2'.format(url,p)
        r = requests.get(url)
        t = r.text
        s = BeautifulSoup(t,'html.parser')
        names = s.select('.songTop.pp')
        accs = s.select('.scoreBottom')
        for n,a in zip(names,accs):
            if n.text in songs:
                print("課題譜面 {} を検出しました。{}".format(n.text,a.text))
                data.at[name,n.text] = int(a.text[7:-3].replace(',',''))

data.to_csv('data.csv')