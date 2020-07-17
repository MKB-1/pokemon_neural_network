import copy
from random import random, choice
import pandas as pd
from joblib import dump, load
from pandas import DataFrame
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from Pokemon import Pokemon, apply_buff, apply_debuff, generate_pokemon, pokemon_moves, create_base_series


#               precision    recall  f1-score   support
#
#            0       0.92      0.92      0.92     58966
#            1       0.92      0.92      0.92     56329
#
#     accuracy                           0.92    115295
#    macro avg       0.92      0.92      0.92    115295
# weighted avg       0.92      0.92      0.92    115295
#
#   [54247  4719]
#   [ 4677 51652]

neural_network = load('static/neural_network_model.joblib')
columns = load('static/columns.joblib')




def pick_move(friendly_pokemon, enemy_pokemon, turn):
    # Speed does not matter, because it is simply creating projections of instances, not simulating an actual fight
    enemy_attack = choice(enemy_pokemon.move_list)
    pred = 0
    friendly_attack = ''
    base_series = create_base_series(friendly_pokemon, enemy_pokemon, turn)

    for move, count in friendly_pokemon.move_set.items():
        temp = base_series.copy()
        temp['Turn'] = temp['Turn'] + 1

        temp_friendly = copy.deepcopy(friendly_pokemon)
        temp_enemy = copy.deepcopy(enemy_pokemon)

        for m, c in friendly_pokemon.move_set.items():
            temp[m] = c + 1 if move == m else c

        temp_friendly.battle_stats['hp'] -= enemy_pokemon.attack(friendly_pokemon, enemy_attack)
        temp_enemy.battle_stats['hp'] -= friendly_pokemon.attack(enemy_pokemon, move)
        apply_buff(move, temp_friendly)
        apply_buff(enemy_attack, temp_enemy)
        apply_debuff(enemy_attack, temp_friendly)
        apply_debuff(move, temp_enemy)

        series = pd.Series(
            {'Current HP': temp_friendly.battle_stats['hp'], 'Enemy Current Hp': temp_enemy.battle_stats['hp'],
             'Skip Turn': temp_friendly.skip_turn})

        for k, v in temp_friendly.status.items():
            if k == 'condition':
                continue
            series[k + ' Status'] = v

        for k, v in temp_enemy.status.items():
            if k == 'condition':
                continue
            series['Enemy ' + k + ' Status'] = v

        conditions = ['BURN', 'SLEEP', 'PARALYZE', 'FROZEN', 'POISON', 'CONFUSION']

        for condition in conditions:
            if condition in temp_friendly.status['condition']:
                series[condition] = True
            else:
                series[condition] = False

            if condition in temp_enemy.status['condition']:
                series['Enemy ' + condition] = True
            else:
                series['Enemy ' + condition] = False

        # ORDER OF COLUMNS MATTERS. The columns must have the same order than the data frame used to train the model!
        temp_s = temp.append(series)
        temp_df = DataFrame()
        temp_df = temp_df.append(temp_s, ignore_index=True)
        temp_df = temp_df.reindex(columns=columns)

        # Since some moves were removed after the neural network was trained, the removed moves have a value of nan
        temp_df = temp_df.fillna(-1)

        for col in temp_df.columns:
            if col not in columns:
                print('Not in x_test: ', col)

        for col in columns:
            if col not in temp_df.columns:
                print('Not in temp_df: ', col)

        prediction_list = neural_network.predict_proba(temp_df)
        prediction = prediction_list[0][1]

        if prediction > pred:
            pred = prediction
            friendly_attack = move

    return friendly_attack


print('neural_network loaded')

