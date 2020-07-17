from random import choice

from flask import Flask, render_template, request, Response, redirect
from Pokemon import Pokemon, complete_moveset, generate_pokemon, apply_buff, apply_debuff, apply_status
import pandas as pd
import json

from neural_network import pick_move

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# friendly = pd.read_csv('static/friendly_pokemon.csv')
# enemy = pd.read_csv('static/enemy_pokemon.csv')

# with open('static/complete_pokemon_moveset.json', 'r') as f:
#     moveset = json.load(f)

data = {'enemy condition': 'NONE', 'friendly condition': 'NONE', 'turn': 0}
gui = {}


@app.route('/', methods=['POST', 'GET', 'PUT'])
def index():
    return render_template('index.html')


@app.route('/choose-pokemon', methods=['POST', 'GET'])
def choose_pokemon():
    req = request.get_json()
    name = req
    return Response(json.dumps(complete_moveset[name]), mimetype='application/json')


@app.route('/initialize-fight', methods=["POST", "GET"])
def init_fight():
    print('init fight')
    req = request.get_json()
    f_moves = req['friendly moves']
    e_moves = req['enemy moves']
    friendly = generate_pokemon(req['friendly'])
    enemy = generate_pokemon(req['enemy'])
    print('friendly: ', friendly.name)
    print('enemy: ', enemy.name)

    def change_moveset(pokemon, include_moves):
        temp = {}
        for move in include_moves:
            if move not in pokemon.move_list:
                continue
            else:
                temp[move] = 0

        i = 0

        while len(temp) != 4:
            m = choice(complete_moveset[pokemon.name])
            if m in temp:
                continue
            else:
                temp[m] = 0
            i += 1
            if i == 20:
                break

        pokemon.move_set = temp

    change_moveset(friendly, f_moves)
    change_moveset(enemy, e_moves)

    data['friendly'] = friendly
    data['enemy'] = enemy

    return fight()


@app.route('/fight', methods=["GET", "POST"])
def fight():
    js = {'moves': list(data['friendly'].move_set.keys()),
          'enemy current hp': max(data['enemy'].battle_stats['hp'], 0),
          'enemy max hp': data['enemy'].base_hp,
          'enemy name': data['enemy'].name,
          'enemy percent hp': max(data['enemy'].battle_stats['hp'] / data['enemy'].base_hp, 0),

          'friendly current hp': max(data['friendly'].battle_stats['hp'], 0),
          'friendly max hp': data['friendly'].base_hp,
          'friendly name': data['friendly'].name,
          'friendly percent hp': max(data['friendly'].battle_stats['hp'] / data['friendly'].base_hp, 0),
          }

    return render_template('fight.html', js=js)


@app.route('/neural-network', methods=["GET", "POST"])
def neural_network():
    req = request.get_json()
    gui['end'] = False
    gui['stage'] = 0

    # Simplified calc for who goes first
    if data['friendly'].battle_stats['speed'] >= data['enemy'].battle_stats['speed']:
        apply_status(data['friendly'])

        if data['friendly'].battle_stats['hp'] <= 0:
            gui['stage'] = 1
            gui['end'] = True
            gui['win'] = False

        if not gui['end']:
            friendly_attack_dmg = data['friendly'].attack(data['enemy'], req)
            data['enemy'].battle_stats['hp'] -= friendly_attack_dmg
            if data['enemy'].battle_stats['hp'] <= 0:
                gui['stage'] = 2
                gui['end'] = True
                gui['win'] = True

        if not gui['end']:
            # buffs and debuffs dont need to be applied if the battle is finished
            apply_buff(req, data['friendly'])
            apply_debuff(req, data['enemy'])

            enemy_move = pick_move(data['enemy'], data['friendly'], data['turn'])
            apply_status(data['enemy'])

            if data['enemy'].battle_stats['hp'] <= 0:
                gui['stage'] = 3
                gui['end'] = True
                gui['win'] = True

            if not gui['end']:
                enemy_attack_dmg = data['enemy'].attack(data['friendly'], enemy_move)
                data['friendly'].battle_stats['hp'] -= enemy_attack_dmg

                if data['friendly'].battle_stats['hp'] <= 0:
                    gui['stage'] = 4
                    gui['end'] = True
                    gui['win'] = False

                apply_buff(enemy_move, data['enemy'])
                apply_debuff(enemy_move, data['friendly'])

    else:
        apply_status(data['enemy'])
        enemy_move = pick_move(data['enemy'], data['friendly'], data['turn'])
        if data['enemy'].battle_stats['hp'] <= 0:
            gui['stage'] = 1
            gui['end'] = True
            gui['win'] = True

        if not gui['end']:
            enemy_attack_dmg = data['enemy'].attack(data['friendly'], enemy_move)
            data['friendly'].battle_stats['hp'] -= enemy_attack_dmg
            if data['friendly'].battle_stats['hp'] <= 0:
                gui['stage'] = 2
                gui['end'] = True
                gui['win'] = False

        if not gui['end']:
            # buffs and debuffs dont need to be applied if the battle is finished
            apply_buff(enemy_move, data['enemy'])
            apply_debuff(enemy_move, data['friendly'])


            apply_status(data['friendly'])

            if data['friendly'].battle_stats['hp'] <= 0:
                gui['stage'] = 3
                gui['end'] = True
                gui['win'] = False

            if not gui['end']:
                friendly_attack_dmg = data['friendly'].attack(data['enemy'], req)
                data['enemy'].battle_stats['hp'] -= friendly_attack_dmg

                if data['enemy'].battle_stats['hp'] <= 0:
                    gui['stage'] = 4
                    gui['end'] = True
                    gui['win'] = True

                apply_buff(req, data['friendly'])
                apply_debuff(req, data['enemy'])


    gui['friendly move'] = req
    gui['enemy move'] = enemy_move
    gui['friendly hp loss'] = enemy_attack_dmg
    gui['enemy hp loss'] = friendly_attack_dmg
    gui['friendly condition'] = data['friendly'].status['condition']
    gui['enemy condition'] = data['enemy'].status['condition']
    gui['friendly hp percent'] = max(data['friendly'].battle_stats['hp'] / data['friendly'].base_hp, 0)
    gui['enemy hp percent'] = max(data['enemy'].battle_stats['hp'] / data['enemy'].base_hp, 0)

    if data['friendly'].get_status('speed') >= data['enemy'].get_status('speed'):
        gui['friendly first'] = True
    else:
        gui['friendly first'] = False

    print(gui)

    return fight()


@app.route('/gui', methods=["GET"])
def gui_info():
    print(gui)
    return Response(json.dumps(gui), mimetype='application/json')


if __name__ == '__main__':
    app.run()
