from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import scipy
from scipy.stats import poisson
import numpy as np
from selenium.webdriver.chrome.options import Options
import os, underscores

#__location__ is the path of the current working directory
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

#Setting variables
date = str(date.today() + timedelta(days=1))
url = 'https://www.livescore.com/soccer/' + date

#Setting up selenium's webdriver
options = Options()
options.headless = True
driver = webdriver.Chrome(os.path.join(__location__, 'chromedriver.exe'), options=options)
driver.get(url)
driver.set_page_load_timeout(10)

print("\nExtracting Tomorrow's matches...")

#Parsing HTML with BeaitifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser',)
home = soup.find_all('div', class_='ply tright name')
away = soup.find_all('div', class_='ply name')

#Writing the parsed text into a CSV
Tomorrow = open(os.path.join(__location__, 'Tomorrow.csv'), 'w+', encoding='Windows-1250')
Tomorrow.write('Date' + ',' + 'Home' + ',' + 'Away' + '\n')
for h, a in zip(home, away):
    if h.text == '__home_team__':
            pass
    else:
        try:
            Tomorrow.write(date + ',' + h.text + ',' + a.text + '\n')
        except UnicodeEncodeError:
            continue
Tomorrow.close()

print('\nMatches extracted!')

#Creating pandas dataframes out of the CSVs
TomorrowRead = open(os.path.join(__location__, 'Tomorrow.csv'), 'r', encoding='Windows-1250')
tm = pd.read_csv(TomorrowRead, delimiter=',')
ScoresR = open(os.path.join(__location__, 'Scores.csv'), 'r', encoding='Windows-1250')
df = pd.read_csv(ScoresR, delimiter=',')

homeT = df['HomeT'].tolist()
awayT = df['AwayT'].tolist()
Home = tm['Home'].tolist()
Away = tm['Away'].tolist()

print("\nPreparing statistics needed...")
StatsW = open(os.path.join(__location__, 'stats.csv'), 'w', encoding='Windows-1250')
#Preparing stats needed to make calculations
StatsW.write('HomeTeam' + ',' + 'MatchesHome' + ',' + 'GoalsHome'
        + ',' + 'AVGHome' + ',' + 'AwayTeam' + ',' + 'MatchesAway'
        + ',' + 'GoalsAway' + ',' + 'AVGAway' + '\n')

for h, a, ht, at in zip(homeT, awayT, Home, Away):
    StatsW.write(str(ht) + ',' + str(df[df['HomeT'] == ht]['HomeS'].sum())+ ','
    + str(homeT.count(ht)) + ','
    + str(round((df[df['HomeT'] == ht]['HomeS'].sum()) / (homeT.count(ht)), 2)) + ','
    + str(at) + ',' + str(df[df['AwayT'] == at]['AwayS'].sum())
    + ',' + str(awayT.count(at)) + ','
    + str(round((df[df['AwayT'] == at]['AwayS'].sum()) / (awayT.count(at)), 2)) + '\n')
StatsW.close()
TomorrowRead.close()


StatsR = open(os.path.join(__location__, 'stats.csv'), 'r', encoding='Windows-1250')
stats = pd.read_csv(StatsR, delimiter=',')
homeT = stats['HomeTeam'].tolist()
awayT = stats['AwayTeam'].tolist()
homeAVG = stats['AVGHome'].tolist()
awayAVG = stats['AVGAway'].tolist()
StatsR.close()

print("\nStatistics calculated!")

print("\nPredicting results of tomorrow's matches...")

#Calculating results and exporting them into CSV
Predictions = open(os.path.join(__location__, 'Predictions.csv'), 'w+', encoding='Windows-1250')
Predictions.write('Home' + ',' + 'Away' + ',' + 'Under 0.5' + ',' + 'Over 0.5'
+ ',' + 'Under 1.5' + ',' + 'Over 1.5' + ',' + 'Under 2.5' + ',' + 'Under 2.5'
+ ',' + 'BTTS' + ',' + 'BTTSNo' + '\n')

for h, a, ha, aa in zip(homeT, awayT, homeAVG, awayAVG):
    Predictions.write(h + ',' + a
    + ',' + str(underscores.under05(ha, aa)) + ',' + str(100 - underscores.under05(ha, aa))
    + ',' + str(underscores.under15(ha, aa)) + ',' + str(100 - underscores.under15(ha, aa))
    + ',' + str(underscores.under25(ha, aa)) + ',' + str(100 - underscores.under25(ha, aa))
    + ',' + str(100 - underscores.bttsno(ha, aa)) + ',' + str(underscores.bttsno(ha, aa)) + '\n')
Predictions.close()

driver.close()
print('\nALL DONE!')