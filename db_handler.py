from sqlalchemy import create_engine
import odds, modeling, app
import sqlite3
import datetime

db = 'boxing.db'

# engine = create_engine(db)

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
        SELECT * from fights
            WHERE fightID = "{}"
    """
    create_button = """
        <a class="btn btn-warning" href="deets?fightid={}">Create Model</a>
    """
    view_model_button = """
        <a class="btn btn-warning" href="fight_deets?fightid={}">View Model</a>
    """
    fight_odds['modeled'] = None
    for i in range(len(fight_odds)):
        result = curs.execute(query.format(fight_odds.at[i,'fight_id']))
        if result == None:
            fight_odds['modeled'] = view_model_button.format(fight_odds.at[i, 'fight_id'])
        else:
            fight_odds['modeled'] = create_button.format(fight_odds.at[i, 'fight_id'])
    conn.close()
    
    return fight_odds

def odds_to_db(fight):
    """
    Writes the odds of a fight to the database.

    Input: A list of Pandas DataFrames
    Output: None
    """
    # conn = sqlite3.connect(db)
    # curs = conn.cursor()

    fight['last_updated'] = datetime.datetime.now()

    fight.to_sql('fight_odds', con=engine, index=False, if_exists='append')

    # conn.close()

def fights_to_db(table):
    """
    Takes a table of two rows consisting of a single fight,
    scraped from proboxingodds.com, and checks to see if the 
    fight exists in the database. If no fight exists, the 
    fight is written to the database.

    Row 0 is the red corner, Row 1 is the blue corner.

    Input: a two row fight Pandas DataFrame
    Output: boolean
            True - fight did not exist and was written to db
            False - fight existed, no action taken
    """
    fights = [table[x:x+2] for x in range(0, len(table), 2)]
    for fight in fights:
        fight['Time'] = fight['Time'][0]
        fight_slice = fight[['Time', 'Fighter', 'Date']]
        fight_slice['red'] = fight_slice.at[0, 'Fighter']
        fight_slice['blue'] = fight_slice.at[1, 'Fighter']
        fight_slice.drop('Fighter')
        query = engine.execute(f"""SELECT * FROM fights 
                            WHERE red={fight_slice['red']} 
                            AND blue={fight_slice['blue']} 
                            AND date={fight_slice['Date']};""").fetchall()
        if len(query) > 0:
            return False
        else:
            fight_slice.to_sql('fights', con=engine, index=False, if_exists='append')
            return True

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

    query = engine.execute(f"""
            SELECT br_id FROM fighter
                WHERE br_id={fighter['br_id']}
            """)

    if len(query) > 0:
        return False
    else:
        fighter.to_sql('fighter', con=engine, index=False, if_exists='append')
        return True

def pred_to_db(pred_df):
    pred_df.to_sql('model_pred', con=engine, index=False, if_exists='append')