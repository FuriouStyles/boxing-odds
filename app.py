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
        conn = db_handler.get_connection()
        tables = odds.parse_proboxingodds(odds.make_soup())
        html_tables = []
        for table in tables:
            html = table.to_dict('list')
            html_tables.append(html)
            # db_handler.odds_to_db(table)
            table.drop(labels=['Time', 'Date', 'modeled'], axis=1).to_sql('fight_odds', con=conn, index=False, if_exists='append')
        conn.close()
        ### TODO: write the odds data to the database
        return render_template('home.html', odds_tables=html_tables)

    @application.route('/deets')
    def deets():
        fight_id = request.args.get('fightid')
        red = request.args.get('red')
        blue = request.args.get('blue')
        date = request.args.get('date')
        time = request.args.get('time')

        return render_template('deets.html',
                                red=red,
                                blue=blue,
                                date=date,
                                time=time,
                                fight_id=fight_id)

    @application.route('/fight_deets', methods=['GET', 'POST'])
    def fight_deets():
        if request.args.get('modeled') == 'False':
            fight_id = request.form.get('fight-id')
            red_id = request.form.get('red-br-id')
            red = request.form.get('red-name')
            red_born = request.form.get('red-born')
            red_debut = request.form.get('red-debut')
            blue_id = request.form.get('blue-br-id')
            blue = request.form.get('blue-name')
            blue_born = request.form.get('blue-born')
            blue_debut = request.form.get('blue-debut')
            title_fight = request.form.get('title-fight')
            sex = request.form.get('sex')
            weight_class = request.form.get('weight-class')
            venue = request.form.get('venue')
            date = request.form.get('date')
            time = request.form.get('time')
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

            red = modeling.fighter_df(red_id, red, red_born,
                                    weight_class, red_height, red_nationality, red_debut,
                                    red_reach, red_stance, red_wins, red_losses, red_draws)

            blue = modeling.fighter_df(blue_id, blue, blue_born,
                                    weight_class, blue_height, blue_nationality, blue_debut,
                                    blue_reach, blue_stance, blue_wins, blue_losses, blue_draws)

            red_new_fight = modeling.fight_df(red, blue, title_fight, sex, weight_class, venue)
            blue_new_fight = modeling.fight_df(blue, red, title_fight, sex, weight_class, venue)

            db_handler.fights_to_db(fight_id, red['name'], blue['name'], weight_class, venue, date, time, sex, title_fight, red_id, blue_id)

            red_probas, red_shap = modeling.prediction(red_new_fight)
            blue_probas, blue_shap = modeling.prediction(blue_new_fight)
            
            pred_df = modeling.pred_df(red_probas[0], blue_probas[0], red_id, blue_id, fight_id, red_shap, blue_shap)
            
            
            db_handler.fighter_to_db(red)
            db_handler.fighter_to_db(blue)

            db_handler.pred_to_db(pred_df)

            return render_template('fight_deets.html',
                                    preds=pred_df.to_dict('records')[0],
                                    red=red.to_dict('records')[0],
                                    blue=blue.to_dict('records')[0],
                                    fight=red_new_fight.to_dict('records')[0],
                                    red_shap=f'force_plots/{red_shap}.html',
                                    blue_shap=f'force_plots/{blue_shap}.html',
                                    date=date,
                                    time=time
                                    )
        
        else:
            fight_id = request.args.get('fightid')
            pred_df = db_handler.get_preds(fight_id)
            red = pred_df['red_id'][0]
            blue = pred_df['blue_id'][0]

            red_shap = pred_df['red_shap'][0]
            blue_shap = pred_df['blue_shap'][0]

            red = db_handler.get_fighter(red)
            blue = db_handler.get_fighter(blue)
            fight = db_handler.get_fight_details(fight_id)

            date = fight['date'][0]
            time = fight['time'][0]

            print("-------------- PRED DF --------------")
            print(pred_df.to_dict('records'))
            print("-------------- RED --------------")
            print(red.to_dict('records'))
            print("-------------- BLUE --------------")
            print(blue.to_dict('records'))
            print("-------------- FIGHT --------------")
            print(fight.to_dict('records'))

            print("-------------- PRED DF --------------")
        
            return render_template('fight_deets.html',
                                    preds=pred_df.to_dict('records')[0],
                                    red=red.to_dict('records')[0],
                                    blue=blue.to_dict('records')[0],
                                    fight=fight.to_dict('records')[0],
                                    red_shap=f'force_plots/{red_shap}.html',
                                    blue_shap=f'force_plots/{blue_shap}.html',
                                    date=date,
                                    time=time
                                    )

    ### TODO: update the odds database once every hour
    return application
