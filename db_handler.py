from sqlalchemy import create_engine
import odds, modeling, app
import sqlite3
import datetime
import pandas as pd

db = 'boxing.db'

# engine = create_engine(db)

def get_connection():
    conn = sqlite3.connect(db)
    return conn

def make_connection(database):
    return sqlite3.connect(database)

def check_db_for_models(fight_odds):
    """
    Checks the database for the existence of each fight in the table
    scraped from proboxingodds. If the fight exists in the table, the 
    data is retrieved and stored in the DataFrame that will be displayed
    on the home page. If the fight does not exist, a button will be added
    in the prediction cells to add the data.

    Input: a list of tables scraped from proboxingodds.
    Output: a combined Pandas DataFrame with the fights scraped from proboxingodds
            and the data pulled from the database, if it exists.
    """
    conn = sqlite3.connect(db)
    curs = conn.cursor()

    query = """
        SELECT * from model_pred
            WHERE fight_id = "{}"
    """
    create_button = """
        <a class="btn btn-warning" href="deets?fightid={}&date={}&time={}&red= {}&blue={}">Create Model</a>
    """
    view_model_button = """
        <a class="btn btn-info" href="fight_deets?fightid={}">View Model</a>
    """
    read_query = """
        SELECT red_win_prob, blue_win_prob FROM model_pred
            WHERE fight_id='{}'
    """
    fight_odds['modeled'] = None
    red = fight_odds['Fighter'][0]
    blue = fight_odds['Fighter'][1]
    fight_id = fight_odds['fight_id'][0]
    print(curs.execute(read_query.format(fight_id)).fetchone())
    for i in range(len(fight_odds)):
        result = curs.execute(query.format(fight_id)).fetchone()
        if result == None:
            fight_odds['modeled'] = create_button.format(fight_id, fight_odds.at[i, 'Date'], fight_odds.at[i, 'Time'], red, blue)
        else:
            # fight_odds['modeled'] = view_model_button.format(fight_odds.at[i, 'fight_id'])
            fight_odds.at[i, 'modeled'] = curs.execute(read_query.format(fight_id)).fetchone()[i]
    conn.close()
    
    return fight_odds

def odds_to_db(fight, fighterID=000000):
    """
    Writes the odds of a fight to the database.

    Input: A Pandas DataFrame containing the odds both fighters for a single fight
    Output: None
    """
    ### Think about putting this behind a try/except for error handling
    conn = sqlite3.connect(db)
    curs = conn.cursor()

    query = f"""
        INSERT INTO fight_odds (
            fight_id,
            Fighter,
            Fivedimes,
            WilliamH,
            Bet365,
            BookMaker,
            BetDSI,
            Intertops,
            SportBet,
            Pinnacle,
            SportsInt,
            BetOnline,
            Sportsbook,
            last_updated
        ) VALUES (
            '{fight.at[0, 'fight_id']}',
            '{fight.at[0, 'Fighter']}',
            '{fight.at[0, 'Fivedimes']}',
            '{fight.at[0, 'WilliamH']}',
            '{fight.at[0, 'Bet365']}',
            '{fight.at[0, 'BookMaker']}',
            '{fight.at[0, 'BetDSI']}',
            '{fight.at[0, 'Intertops']}',
            '{fight.at[0, 'SportBet']}',
            '{fight.at[0, 'Pinnacle']}',
            '{fight.at[0, 'SportsInt']}',
            '{fight.at[0, 'BetOnline']}',
            '{fight.at[0, 'Sportsbook']}',
            '{fight.at[0, 'last_updated']}'
        ), (
            '{fight.at[1, 'fight_id']}',
            '{fight.at[1, 'Fighter']}',
            '{fight.at[1, 'Fivedimes']}',
            '{fight.at[1, 'WilliamH']}',
            '{fight.at[1, 'Bet365']}',
            '{fight.at[1, 'BookMaker']}',
            '{fight.at[1, 'BetDSI']}',
            '{fight.at[1, 'Intertops']}',
            '{fight.at[1, 'SportBet']}',
            '{fight.at[1, 'Pinnacle']}',
            '{fight.at[1, 'SportsInt']}',
            '{fight.at[1, 'BetOnline']}',
            '{fight.at[1, 'Sportsbook']}',
            '{fight.at[1, 'last_updated']}'
        );
    """
    curs.execute(query)
    conn.commit()
    conn.close()
    return

def fights_to_db(fight_id, red, blue, weight_class, venue, date, time, sex, title_fight, red_id, blue_id):
    """
    Takes the fight values from the 'deets' page, and saves them to the database.

    Row 0 is the red corner, Row 1 is the blue corner.

    Input: A list of values pulled from the field form and the url parameter
    Output: boolean
            True - fight did not exist and was written to db
            False - fight existed, no action taken
    """
    # fights = [table[x:x+2] for x in range(0, len(table), 2)]
    # for fight in fights:
    #     fight['Time'] = fight['Time'][0]
    #     fight_slice = fight[['Time', 'Fighter', 'Date']]
    #     fight_slice['red'] = fight_slice.at[0, 'Fighter']
    #     fight_slice['blue'] = fight_slice.at[1, 'Fighter']
    #     fight_slice.drop('Fighter')

    conn = sqlite3.connect(db)
    curs = conn.cursor()
    query = curs.execute(f"""SELECT * FROM fights 
                        WHERE red='{red}' 
                        AND blue='{blue}' 
                        AND date='{date}'""").fetchone()
    if query == None:
        print('FIGHT to db write here')
        write_query = f"""
            INSERT INTO fights (
                fight_id,
                red,
                blue,
                venue,
                date,
                weight_class,
                time,
                sex,
                title_fight,
                red_id,
                blue_id
            ) VALUES (
                '{fight_id}',
                '{red}',
                '{blue}',
                '{venue}',
                '{date}',
                '{weight_class}',
                '{time}',
                '{sex}',
                '{title_fight}',
                '{red_id}',
                '{blue_id}'
            )
        """
        curs.execute(write_query)
        conn.commit()
        conn.close()
        return True
    else:
        return False

def fighter_to_db(fighter):
    """
    Add a fighter to the database if the fighter does not already exist
    in the database.

    Input: Pandas DataFrame of a single fighter
    Output: boolean
            True - fighter did not exist and was written to db
            False - fighter existed, no action taken
    """
    # fighter['Fighter'].lstrip()
    # first, last = fighter['Fighter'].str.split(' ', 1)

    conn = sqlite3.connect(db)
    curs = conn.cursor()

    query = curs.execute(f"""
            SELECT br_id FROM fighter
                WHERE br_id='{fighter['br_id']}';
            """).fetchone()

    if query == None:
        print('fighter is here')
        fighter[['br_id',
                 'born',
                 'division',
                 'height_cm',
                 'reach_cm',
                 'nationality',
                 'debut',
                 'stance',
                 'wins',
                 'losses',
                 'draws',
                 'name']].to_sql('fighter', con=conn, index=False, if_exists='append')
        conn.close()
        return True
    else:
        conn.close()
        return False

def pred_to_db(pred_df):
    conn = sqlite3.connect(db)
    print(pred_df)
    pred_df.to_sql('model_pred', con=conn, index=False, if_exists='append')
    conn.close()
    return

def get_preds(fight_id):
    conn = sqlite3.connect(db)
    read_query = """
        SELECT * FROM model_pred
            WHERE fight_id='{}'
    """
    preds = pd.read_sql(read_query.format(fight_id), con=conn)
    conn.close()
    return preds #curs.execute(read_query.format(fight_id)).fetchone()

def get_fighter(fighter):
    conn = sqlite3.connect(db)
    read_query = """
        SELECT * FROM fighter
            WHERE br_id='{}'
    """
    curs = conn.cursor()
    print(curs.execute(read_query.format(fighter)).fetchone)
    fighter = pd.read_sql(read_query.format(fighter), con=conn)
    conn.close()
    return fighter

def get_fight_details(fightid):
    conn=sqlite3.connect(db)
    read_query = """
        SELECT * FROM fights
            WHERE fight_id='{}'
    """
    fight = pd.read_sql(read_query.format(fightid), con=conn)
    conn.close()
    return fight

print('dafuq is this shit')