import datetime
import pandas as pd
from sqlalchemy import engine
import odds
import sqlite3
import numpy as np
import joblib
import eli5
import shap
import db_handler
import matplotlib.pyplot as plt
import re

imputer = 'static/knn_imputer.sav'
model = 'static/xgb_model_v3.sav'
encoder = 'static/cat_boost_encoder.sav'

loaded_imputer = joblib.load(imputer)
loaded_model = joblib.load(model)
loaded_encoder = joblib.load(encoder)

explainer = shap.Explainer(loaded_model)

## Predicting new fights

# Function to accept and prepare the form data
def fighter_df(br_id, name, born, division, height,
                nationality, debut, reach, stance, wins, losses, draws):
    labels = ['br_id', 'name', 'born', 'division', 'height_cm',
                'nationality', 'debut', 'reach_cm', 'stance', 'wins', 'losses', 'draws']
    
    df = pd.DataFrame(data=[[br_id, name, born, division, height,
                nationality, debut, reach, stance, wins, losses, draws]], columns=labels)

    df['born'] = pd.to_datetime(born) # may need to use the df call instead of the func param?
    df['debut'] = pd.to_datetime(debut) # same

    return df
    

def fight_df(red, blue, title_fight, sex, weight_class, venue):

    labels = ['red_br_id', 'blue_br_id', 'title_fight', 'sex', 'venue', 'red_height', 'blue_height',
    'red_nationality', 'blue_nationality', 'red_reach', 'blue_reach', 'red_stance', 'blue_stance', 'red_age',
    'blue_age', 'red_years_active', 'blue_years_active', 'red_wins', 'red_losses', 'red_draws', 'blue_wins',
    'blue_losses', 'blue_draws']

    today = pd.to_datetime(datetime.datetime.today())
    red['age'] = today - red['born']
    blue['age'] = today - blue['born']
    red['years_active'] = today - red['debut']
    blue['years_active'] = today - blue['debut']
    red['age'][0] = red['age'][0].days/365
    blue['age'][0] = blue['age'][0].days/365
    red['years_active'][0] = red['years_active'][0].days/365
    blue['years_active'][0] = blue['years_active'][0].days/365
    print(red['age'][0])
    if title_fight == 'on':
        title_fight = 1
    else:
        title_fight = 0
    if sex == 'on':
        sex = 1
    else:
        sex = 0

    df = pd.DataFrame(data=[[red.at[0, 'br_id'], blue.at[0,'br_id'], title_fight, sex, venue, red.at[0, 'height_cm'], blue.at[0, 'height_cm'],
    red.at[0, 'nationality'], blue.at[0, 'nationality'], red.at[0, 'reach_cm'], blue.at[0,'reach_cm'], red.at[0,'stance'], blue.at[0,'stance'], red.at[0,'age'],
    blue.at[0,'age'], red.at[0, 'years_active'], blue.at[0,'years_active'], red.at[0, 'wins'], red.at[0, 'losses'], red.at[0, 'draws'], blue.at[0, 'wins'],
    blue.at[0, 'losses'], blue.at[0, 'draws']]], columns=labels)

    df['red_age_at_fight_time'] = pd.to_numeric(df['red_age'], errors='coerce')
    df['red_years_active'] = pd.to_numeric(df['red_years_active'], errors='coerce')
    df['blue_age_at_fight_time'] = pd.to_numeric(df['blue_age'], errors='coerce')
    df['blue_years_active'] = pd.to_numeric(df['blue_years_active'], errors='coerce')
    df['red_division'] = weight_class
    df['blue_division'] = weight_class

    df = df.replace(r'^\s*$', np.NaN, regex=True)
    print(df.T)
    # df['title_fight'] = 1 if title_fight is 'on' else 0
   
    # df['red_stance'] = [1 if stance == 'orthodox' else 2 if stance == 'southpaw' else np.nan for stance in df['red_stance']]

    return df

# Function to possibly impute and encode

def encode_df(df):
    print("----------------- PRE ENCODED --------------")
    print(df)
    encoded = loaded_encoder.transform(df)
    print("----------------- ENCODED ------------------")
    print(encoded)
    return encoded

def impute_df(df):
    imputed = loaded_imputer.transform(df)
    return imputed

# # return predict_proba

def prediction(df):
    key = str(df['red_br_id'][0]) + str(df['blue_br_id'][0])
    missing_encoder_cols = [x for x in loaded_encoder.get_feature_names() if x not in loaded_model.get_booster().feature_names]
    df[missing_encoder_cols] = None
    encoded = encode_df(df)
    imputed = impute_df(encoded)
    fight = pd.DataFrame(imputed, columns=loaded_encoder.get_feature_names())
    fight = fight[loaded_model.get_booster().feature_names]

    probas = loaded_model.predict_proba(fight)
    html = get_shap_force(fight, explainer, key)

    return probas, key

# # save results to the database
def pred_df(red_proba, blue_proba, red, blue, fight_id, red_html, blue_html):
    """
    Takes the prediction probabilities, fighters, fight ID, and explainer HTML,
    formats them as a dataframe, and saves them to the database.

    Input
        red_proba: D/L/NC/W probabilities of the red corner
        blue_proba: D/L/NC/W probabilities of the blue corner
        red: red corner boxrec ID
        blue: blue corner boxrec ID
        fight_id: the boxrec fight_id (if it exists)
        html: the html output of the prediction explainer 
            (currently only eli5 is supported)
    """
    labels = ['red_id', 'blue_id', 'fight_id', 'red_win_prob', 'red_lose_prob', 'blue_win_prob',
              'blue_lose_prob', 'red_draw_prob', 'blue_draw_prob', 'red_shap', 'blue_shap', 'created']

    created = datetime.datetime.now()

    df = pd.DataFrame(data=[[red, blue, fight_id, round(red_proba[3]*100, 3), round(red_proba[1]*100, 3),
                            round(blue_proba[3]*100, 3), round(blue_proba[1]*100, 3), round(red_proba[0]*100, 3),
                            round(blue_proba[0]*100, 3), red_html, blue_html, created]],
                            columns=labels)

    return df

## Fight Explainability

# Shap plot for model explainability

# SHAP plot for prediction explainability
def get_shap_force(df, explainer, key):
    shap_values = explainer.shap_values(df)
    plot = shap.force_plot(explainer.expected_value[0], shap_values[0], show=False, feature_names = loaded_model.get_booster().feature_names)
    shap.save_html(f'templates/force_plots/{key}.html', plot, full_html=False)

# Eli5 Prediction Explaination
def eli_pred_html(model, df):
    return 'nevermind'