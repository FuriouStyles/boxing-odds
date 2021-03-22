import pandas as pd
import flask
from flask import Flask, redirect, flash, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import requests
import odds, modeling, db_handler

# db = SQLAlchemy()

def create_app():
    application = Flask(__name__)
    # db.init_app(application)
    application.config['SQLALCHEMY_DATABASE_URI'] = db_handler.db
    # db = SQLAlchemy(application)
    application.debug = True

    @application.route('/')
    def home():
        tables = odds.parse_proboxingodds(odds.make_soup())
        html_tables = []
        for idx, table in enumerate(tables):
            # html = table.to_html(index=False, justify='center', classes='odds-table', table_id=f'odds-table{idx}')
            html = table.to_dict('list')
            html_tables.append(html)
        return render_template('home.html', odds_tables=html_tables)

    @application.route('/deets')
    def deets():
        red_fight_id = request.args('fightid')
        red = request.args('red')
        blue = request.args('blue')
        date = request.args('date')
        blue_fight_id = blue + red + date
        blue_fight_id = blue_fight_id.strip().replace(' ', '')
        red = red.split()
        blue = blue.split()
        return render_template('deets.html', red=red, blue=blue, date=date, red_fight_id=red_fight_id, blue_fight_id=blue_fight_id)

    @application.route('/fight_deets', methods=['GET', 'POST'])
    def fight_deets():
        fight_id = request.form.get('fight-id')
        red_id = request.form.get('red-br-id')
        red_first_name = request.form.get('red-first-name')
        red_last_name = request.form.get('red-last-name')
        red_born = request.form.get('red-born')
        red_debut = request.form.get('red-debut')
        blue_id = request.form.get('blue-br-id')
        blue_first_name = request.form.get('blue-first-name')
        blue_last_name = request.form.get('blue-last-name')
        blue_born = request.form.get('blue-born')
        blue_debut = request.form.get('blue-debut')
        title_fight = request.form.get('title-fight')
        sex = request.form.get('sex')
        weight_class = request.form.get('weight-class')
        venue = request.form.get('venue')
        red_height = request.form.get('red-height')
        blue_height = request.form.get('blue-height')
        red_nationality = request.form.get('red-nationality')
        blue_nationality = request.form.get('blue-nationality')
        red_reach = request.form.get('red-reach')
        blue_reach = request.form.get('blue-reach')
        red_stance = request.form.get('red-stance')
        blue_stance = request.form.get('blue-stance')
        red_wins = request.form.get('red-wins')
        red_losses = request.form.get('red-losses')
        red_draws = request.form.get('red-draws')
        blue_wins = request.form.get('blue-wins')
        blue_losses = request.form.get('blue-losses')
        blue_draws = request.form.get('blue-draws')

        red = modeling.fighter_df(red_id, red_first_name, red_last_name, red_born,
                                  weight_class, red_height, red_nationality, red_debut,
                                  red_reach, red_stance, red_wins, red_losses, red_draws)

        blue = modeling.fighter_df(blue_id, blue_first_name, blue_last_name, blue_born,
                                  weight_class, blue_height, blue_nationality, blue_debut,
                                  blue_reach, blue_stance, blue_wins, blue_losses, blue_draws)

        red_new_fight = modeling.fight_df(red, blue, title_fight, sex, weight_class, venue)
        blue_new_fight = modeling.fight_df(blue, red, title_fight, sex, weight_class, venue)

        # new_fight = modeling.encode_df(red_new_fight)
        # new_fight = modeling.impute_df(red_new_fight)
        red_probas, red_eli5 = modeling.prediction(red_new_fight)
        blue_probas, blue_eli5 = modeling.prediction(blue_new_fight)
        # print(f'RED PROBAS: {red_probas}')
        # print(f'BLUE PROBAS: {blue_probas}')
        # red_eli5 = modeling.eli_pred_html(modeling.loaded_model, red_new_fight)
        # blue_eli5 = modeling.eli_pred_html(modeling.loaded_model, blue_new_fight)
        pred_df = modeling.pred_df(red_probas[0], blue_probas[0], red_id, blue_id, fight_id, red_eli5, blue_eli5)
        
        return render_template('fight_deets.html', context = pred_df.to_html(), red_shap = f'force_plots/{red_eli5}.html', blue_shap=f'force_plots/{blue_eli5}.html')

# D:\Projects\boxing-odds\force_plots\2573236845.html
    return application
