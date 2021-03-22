import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re
import datetime
import sqlalchemy
import numpy as np
import modeling
import random
import db_handler


# engine = sqlalchemy.create_engine(db_handler.db)
head={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}

def make_soup():
    print('making soup')
    sess = requests.Session()
    req = sess.get("https://www.proboxingodds.com/", headers=head)
    soup = bs(req.content, features='lxml')
    return soup

# soup = make_soup()
# print(soup)

def parse_proboxingodds(soup):
    """
    Creates pandas dataframes out of all the tables in the beautifulsoup content.
    Input: BeautifulSoup HTML content
    Output: a list of tables containing fights for a particular date

    Note: The date is gathered elsewhere
    """
    # url = 'https://www.proboxingodds.com/'
    tables = []
    # dates = soup.find_all('div', attrs={'class':'table-header'})
    site = pd.read_html(str(soup))
    for idx, table in enumerate(site):
        if idx == 0:
            pass
        elif idx % 2 != 0:
            sliced = table[(table['Unnamed: 0'].str.contains(':')) | (table['Unnamed: 0'] == 'UTC')]
            sliced = sliced.rename({'Unnamed: 0':'Time', 'Unnamed: 1':'Fighter'}, axis=1)
            sliced['Fivedimes'] = sliced['5Dimes']
            sliced['WilliamH'] = sliced['William\xa0H.']
            sliced['SportsInt'] = sliced['SportsInt.']
            sliced.drop(columns=['Props', 'Props.1', 'Props.2', '5Dimes', 'William\xa0H.', 'SportsInt.'], inplace=True)
            sliced['last_updated_date'] = datetime.datetime.now()
            for i in sliced.columns.to_list()[2:-1]:
                sliced[i] = sliced[i].apply(lambda x: remove_arrows(x))
                sliced[i] = sliced[i].apply(lambda x: amer_to_dec(x))
            tables.append(sliced)
    dates = get_dates(soup)
    tables = impute_dates(tables, dates)
    tables = [impute_fightID(table) for table in tables]
    tables = [db_handler.check_db_for_models(table) for table in tables]
    return tables

def remove_arrows(line):
    """
    Helper function to remove the arrows at the end of the odds figures
    in the proboxingodds tables.
    """
    pattern = r'[\+\-][0-9]+'
    if type(line) != str:
        if (pd.isnull(line) == True) | (np.isnan(line) == True):
            return 'NaN'
        else:
            return line
    else:
        line = re.search(pattern, line)
        return line[0]

def amer_to_dec(fig):
    """
    Helper function to convert the American odds to a more readable 
    decimal format.
    """
    sign_pattern = r'[\+\-]'
    if fig == 'NaN':
        return 'No Lines'
    fig = str(fig)
    sign = re.search(sign_pattern, fig)
    if sign == None:
        sign = '+'
        num = float(fig)
    else:
        sign = sign[0]
        num = float(fig.lstrip(sign))
    if sign == '+' :
        return round(1 + (num/100), 2)
    elif sign == '-':
        return round(1 + (100/num), 2)
    else:
        return "error"

def get_dates(soup):
    """
    Helper function to get the dates out of the beautifulsoup response object
    """
    return [res.get_text() for res in soup.find_all('a', attrs={'href':re.compile('/events/')})]

def impute_dates(tables, dates):
    """
    Helper function to impute the dates from the proboxingodds website into the tables
    that contain the fights.
    """
    new_fights = []
    for idx, date in enumerate(dates):
        if date == 'FUTURE EVENTS':
            break
        tables[idx]['Date'] = date
    for table in tables[:-1]:
        fights = [table[x:x+2] for x in range(0, len(table), 2)]       
        for idxf, fight in enumerate(fights):
            fight.reset_index(drop=True, inplace=True)
            fight['Time'] = fight['Time'][0]
            new_fights.append(fight)      
    return new_fights

def impute_fightID(fight):
    """
    Creates a unique fight ID from combining the names of both fighters and the dates, without spaces
    or special characters. This should work with rematches well. A potential edge case, but one we
    probably won't run into, is two fights with fighters of the same name fight on the same date.

    Input: A Pandas DataFrame of two rows, red corner and blue corner
    Output: The DataFrame with the fight ID included
    """
    red = fight.at[0, 'Fighter']
    blue = fight.at[1, 'Fighter']
    date = fight['Date'][0]
    fight_id_red = red + blue + date
    fight_id_blue = blue + red + date
    fight_id_red = fight_id_red.strip('-,').replace(' ', '')
    fight_id_blue = fight_id_blue.strip('-,').replace(' ', '')
    fight.at[0, 'fight_id'] = fight_id_red
    fight.at[1, 'fight_id'] = fight_id_blue

    return fight


def table_to_html(table):
    """
    Converts a pandas dataframe into an HTML table.

    Input: Pandas DataFrame
    Output: HTML Table containing all the data in the DataFrame
    """
    return table.to_html(classes = 'odds_table')

# def check_db_for_models(fight_odds):
#     """
#     Checks the database for the existence of each fight in the table
#     scraped from proboxingodds. If the fight exists in the table, the 
#     data is retrieved and stored in the DataFrame that will be displayed
#     on the home page. If the fight does not exist, a button will be added
#     in the prediction cells to add the data.

#     Input: a list of tables scraped from proboxingodds.
#     Output: a combined Pandas DataFrame with the fights scraped from proboxingodds
#             and the data pulled from the database, if it exists.
#     """
#     query = """
#         SELECT fightID from fights
#             WHERE fightID = {}
#     """
    
#     fight_odds['modeled'] = None
#     for i in range(len(fight_odds)):
#         if len(db_handler.engine.execute(query.format(fight_odds.at[i,'fight_id']))) > 0:
#             fight_odds['modeled'] = True
#         else:
#             fight_odds['modeled'] = False
    
#     return fight_odds

def gen_random_fightID():
    """
    Generates and returns a random six digit number if no BoxRec bout exists for the fight.
    
    Input: None
    Output: Random six digit integer
    """
    pass