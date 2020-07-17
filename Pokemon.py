from random import random, shuffle, choice
import json
import pandas as pd

# Import webscraped moves
with open('static/move_descriptions.json', 'r') as fp:
    pokemon_moves = json.load(fp)

merged_df = pd.read_csv('static/merged.csv')
friendly = pd.read_csv('static/friendly_pokemon.csv')
enemy = pd.read_csv('static/enemy_pokemon.csv')

with open('static/complete_pokemon_moveset.json', 'r') as f:
    complete_moveset = json.load(f)

class Pokemon:
    wins = 0

    # pokemon is a row from merged.csv, of type Series
    def __init__(self, pokemon):
        self.move_set = {}
        self.name = pokemon['Name']
        self.base_hp = pokemon['HP']
        self.base_attack = pokemon['Attack']
        self.base_defense = pokemon['Defense']
        self.base_sp_atk = pokemon['Sp. Atk']
        self.base_sp_def = pokemon['Sp. Def']
        self.base_speed = pokemon['Speed']
        self.type1 = pokemon['Primary Type']
        self.type2 = pokemon['Secondary Type']
        self.status = {'attack': 0, 'defense': 0, 'sp atk': 0, 'sp def': 0, 'speed': 0, 'accuracy': 0, 'evasiveness': 0,
                       'condition': 'NONE'}
        self.battle_stats = {}
        self.generate_battle_stats()
        self.skip_turn = False

        self.dmg_from_normal = pokemon['dmg_from_Normal']
        self.dmg_from_fire = pokemon['dmg_from_Fire']
        self.dmg_from_water = pokemon['dmg_from_Water']
        self.dmg_from_electric = pokemon['dmg_from_Electric']
        self.dmg_from_grass = pokemon['dmg_from_Grass']
        self.dmg_from_ice = pokemon['dmg_from_Ice']
        self.dmg_from_fighting = pokemon['dmg_from_Fighting']
        self.dmg_from_poison = pokemon['dmg_from_Poison']
        self.dmg_from_ground = pokemon['dmg_from_Ground']
        self.dmg_from_flying = pokemon['dmg_from_Flying']
        self.dmg_from_psychic = pokemon['dmg_from_Psychic']
        self.dmg_from_bug = pokemon['dmg_from_Bug']
        self.dmg_from_rock = pokemon['dmg_from_Rock']
        self.dmg_from_ghost = pokemon['dmg_from_Ghost']
        self.dmg_from_dragon = pokemon['dmg_from_Dragon']
        self.dmg_from_dark = pokemon['dmg_from_Dark']
        self.dmg_from_steel = pokemon['dmg_from_Steel']
        self.dmg_from_fairy = pokemon['dmg_from_Fairy']

        self.move_list = complete_moveset[self.name].copy()

        self.generate_move_set()

    def attack(self, enemy_pokemon, move_name):
        move = pokemon_moves[move_name]

        attack = self.get_status('attack') if not move["special"] else self.get_status('sp atk')
        defense = enemy_pokemon.get_status('defense') if not move["special"] else enemy_pokemon.get_status('sp def')
        stab = 1.5 if (move["type"] == self.type1 or move["type"] == self.type2) else 1
        type_effectiveness = getattr(enemy_pokemon, 'dmg_from_' + move['type'].lower())
        randomness = random() * 0.15 + 0.85

        # cannot be resolved in get_status because it relies on the enemy's evasiveness
        acc_modifiers = {
            -6: 3 / 9,
            -5: 3 / 8,
            -4: 3 / 7,
            -3: 3 / 6,
            -2: 3 / 5,
            -1: 3 / 4,
            0: 1,
            1: 4 / 3,
            2: 5 / 3,
            3: 6 / 3,
            4: 7 / 3,
            5: 8 / 3,
            6: 9 / 3
        }

        acc_modifier = self.status['accuracy'] - enemy_pokemon.status['evasiveness']
        if acc_modifier < -6:
            acc_modifier = -6
        elif acc_modifier > 6:
            acc_modifier = 6
        hit_or_miss = move['accuracy'] * (acc_modifiers[acc_modifier])

        if random() < hit_or_miss:
            if move['power'] == 0:
                return 0
            else:
                if 'double hit' in move['effect'].keys():
                    hits = 2
                elif 'multi hit' in move['effect'].keys():
                    l = [2, 3, 4, 5]
                    hits = choice(l)
                else:
                    hits = 1
                return int(((0.1 * move['power'] * attack / defense + 2) * stab * type_effectiveness * randomness) * hits)
        else:
            return 0

    def get_status(self, status):
        modifier = {
            -6: 2 / 8,
            -5: 2 / 7,
            -4: 2 / 6,
            -3: 2 / 5,
            -2: 2 / 4,
            -1: 2 / 3,
            0: 1,
            1: 3 / 2,
            2: 4 / 2,
            3: 5 / 2,
            4: 6 / 2,
            5: 7 / 2,
            6: 4 / 2
        }
        return self.battle_stats[status] * modifier[self.status[status]]

    def generate_battle_stats(self):
        self.battle_stats['attack'] = self.base_attack
        self.battle_stats['hp'] = self.base_hp
        self.battle_stats['defense'] = self.base_defense
        self.battle_stats['sp atk'] = self.base_sp_atk
        self.battle_stats['sp def'] = self.base_sp_def
        self.battle_stats['speed'] = self.base_speed

    def generate_move_set(self):
        self.move_set = {}
        no_dmg_moves = 0
        shuffle(self.move_list)

        for x in range(0, min(len(self.move_list), 4)):
            if pokemon_moves[self.move_list[x]]['power'] == 0:
                no_dmg_moves += 1
            if len(self.move_list) <= x:
                break
            self.move_set[self.move_list[x]] = 0

        if no_dmg_moves == 4:
            self.generate_move_set()

    def poke_center(self):
        self.status = {'attack': 0, 'defense': 0, 'sp atk': 0, 'sp def': 0, 'speed': 0, 'accuracy': 0, 'evasiveness': 0,
                       'condition': 'NONE'}
        self.generate_battle_stats()
        self.skip_turn = False

    def print_info(self):
        print('Name: ', self.name)
        print('Movelist: ', self.move_list)
        print('Moveset: ', self.move_set)

    def randomize(self):
        self.poke_center()
        self.generate_move_set()

    def reset_wins(self):
        self.wins = 0


def generate_pokemon(pokemon_name):
    pokemon_series = merged_df[merged_df['Name'] == pokemon_name].squeeze()
    pokemon = Pokemon(pokemon_series)
    return pokemon


def apply_status(pokemon):
    if pokemon.status['condition'] == 'BURN':
        pokemon.battle_stats['attack'] = pokemon.base_attack / 2
        pokemon.battle_stats['hp'] -= 1 / 16 * pokemon.base_hp
    elif pokemon.status['condition'] == 'POISON':
        pokemon.battle_stats['hp'] -= 1 / 8 * pokemon.base_hp
    elif pokemon.status['condition'] == 'PARALYZE':
        pokemon.battle_stats['speed'] = pokemon.base_speed / 2
        if random() <= 0.25:
            pokemon.skip_turn = True
    elif pokemon.status['condition'] == 'FROZEN':
        if random() <= 0.20:
            pokemon.status['condition'] = 'NONE'
        else:
            pokemon.skip_turn = True
    elif 'SLEEP' in pokemon.status['condition']:
        pokemon.skip_turn = True
        if '0' in pokemon.status['condition']:
            pokemon.status['condition'] = 'NONE'
        elif '1' in pokemon.status['condition']:
            pokemon.status['condition'] = 'SLEEP0'
        elif '2' in pokemon.status['condition']:
            pokemon.status['condition'] = 'SLEEP1'
        elif '3' in pokemon.status['condition']:
            pokemon.status['condition'] = 'SLEEP2'
    elif 'CONFUSION' in pokemon.status['condition']:
        if random() <= 0.33:
            pokemon.skip_turn = True
            pokemon.battle_stats['hp'] -= 10

        if '1' in pokemon.status['condition']:
            pokemon.status['condition'] = 'NONE'
        elif '2' in pokemon.status['condition']:
            pokemon.status['condition'] = 'CONFUSION1'
        elif '3' in pokemon.status['condition']:
            pokemon.status['condition'] = 'CONFUSION2'
        elif '4' in pokemon.status['condition']:
            pokemon.status['condition'] = 'CONFUSION3'
        elif '5' in pokemon.status['condition']:
            pokemon.status['condition'] = 'CONFUSION4'


def apply_debuff(move_name, pokemon):
    move = pokemon_moves[move_name]
    if not move['effect']:
        return
    if 'probability' in move['effect']:
        if random() > float(move['effect']['probability']) / 100:
            return

    for effect in move['effect'].keys():
        if effect == 'sleep':
            if pokemon.status['condition'] == 'NONE':
                turns = random()
                if turns <= 0.33:
                    turns = 1
                elif turns >= 0.67:
                    turns = 2
                else:
                    turns = 3
                pokemon.status['condition'] = 'SLEEP' + str(turns)
        elif effect == 'confusion':
            if pokemon.status['condition'] == 'NONE':
                turns = random()
                if turns <= 0.25:
                    turns = 2
                elif turns <= 0.5:
                    turns = 3
                elif turns <= 0.75:
                    turns = 4
                else:
                    turns = 5
                pokemon.status['condition'] = 'CONFUSION' + str(turns)
        elif effect == 'burn':
            if pokemon.status['condition'] == 'NONE':
                pokemon.status['condition'] = 'BURN'
        elif effect == 'freeze':
            if pokemon.status['condition'] == 'NONE':
                pokemon.status['condition'] = 'FROZEN'
        elif effect == 'poison':
            if pokemon.status['condition'] == 'NONE':
                pokemon.status['condition'] = 'POISON'
        elif effect == 'paralyze':
            if pokemon.status['condition'] == 'NONE':
                pokemon.status['condition'] = 'PARALYZE'
        elif effect == 'probability' or effect == 'ignore acc' or effect == 'flinch' or effect == 'recharge' \
                or effect == 'critical' or effect == 'recoil' or effect == 'multi hit' or effect == 'double hit' \
                or effect == 'one hit ko':
            continue
        else:
            if move['effect'][effect] < 0:
                pokemon.status[effect] += move['effect'][effect]
                if pokemon.status[effect] < -6:
                    pokemon.status[effect] = -6
                elif pokemon.status[effect] > 6:
                    pokemon.status[effect] = 6


def apply_buff(move_name, pokemon):
    move = pokemon_moves[move_name]
    if not move['effect']:
        return
    if 'probability' in move['effect']:
        if random() > float(move['effect']['probability']) / 100:
            return
    for effect in move['effect'].keys():
        if effect == 'probability' or effect == 'ignore acc' or effect == 'flinch' or effect == 'recharge' \
                or effect == 'critical' or effect == 'recoil' or effect == 'multi hit' or effect == 'double hit' \
                or effect == 'one hit ko' or effect == 'burn' or effect == 'poison' or effect == 'freeze' \
                or effect == 'sleep' or effect == 'paralyze' or effect == 'confusion' or effect == 'condition':
            continue
        else:
            if move['effect'][effect] > 0:
                pokemon.status[effect] += move['effect'][effect]
                if pokemon.status[effect] < -6:
                    pokemon.status[effect] = -6
                elif pokemon.status[effect] > 6:
                    pokemon.status[effect] = 6


# Generates sequence of moves until one Pokemon faints
def generate_sequence(p1, p2, optimal, p1_arr=None, p2_arr=None, base_df=None, turn=0):
    turn += 1

    if p1_arr is None:
        p1_arr = []
        p2_arr = []
        base_df = pd.DataFrame()

    apply_status(p1)
    apply_status(p2)

    series = pd.Series({'Turn': turn, 'Current HP': p1.battle_stats['hp'], 'Enemy Current Hp': p2.battle_stats['hp'],
                        'Skip Turn': p1.skip_turn})
    for k, v in p1.move_set.items():
        series[k] = v

    for k,v in p1.status.items():
        if k == 'condition':
            continue
        series[k + ' Status'] = v

    for k, v in p2.status.items():
        if k == 'condition':
            continue
        series['Enemy ' + k + ' Status'] = v

    conditions = ['BURN', 'SLEEP', 'PARALYZE', 'FROZEN', 'POISON', 'CONFUSION']

    for condition in conditions:
        if condition in p1.status['condition']:
            series[condition] = True
        else:
            series[condition] = False

        if condition in p2.status['condition']:
            series['Enemy ' + condition] = True
        else:
            series['Enemy ' + condition] = False

    base_df = base_df.append(series, ignore_index=True)

    if len(p1_arr) > 40:
        return base_df

    # Base Case is when one Pokemon faints
    if p1.battle_stats['hp'] <= 0 or p2.battle_stats['hp'] <= 0:
        if p1.battle_stats['hp'] <= 0:
            p2.wins += 1
        else:
            p1.wins += 1
        return base_df

    # decides which Pokemon attacks first
    if p1.get_status('speed') == p2.get_status('speed'):
        if random() >= 0.50:
            pokemon_1 = p1
            pokemon_2 = p2
            pokemon_1_arr = p1_arr
            pokemon_2_arr = p2_arr

        else:
            pokemon_1 = p2
            pokemon_2 = p1
            pokemon_1_arr = p2_arr
            pokemon_2_arr = p1_arr

    elif p1.get_status('speed') > p2.get_status('speed'):
        pokemon_1 = p1
        pokemon_2 = p2
        pokemon_1_arr = p1_arr
        pokemon_2_arr = p2_arr
    else:
        pokemon_1 = p2
        pokemon_2 = p1
        pokemon_1_arr = p2_arr
        pokemon_2_arr = p1_arr

    # If optimal, move is chosen based on predicted damage output
    if optimal:
        dmg = 0
        key1 = next(iter(pokemon_2.move_set))
        for k, v in pokemon_2.move_set.items():
            # key1 = k if damage(pokemon_1, pokemon_2, key1) >= dmg else key1
            key1 = k if pokemon_1.attack(pokemon_2, key1) >= dmg else key1

        dmg = 0
        key2 = next(iter(pokemon_2.move_set))
        for k, v in pokemon_2.move_set.items():
            # key2 = k if damage(pokemon_2, pokemon_1, key2) >= dmg else key2
            key2 = k if pokemon_2.attack(pokemon_1, key2) >= dmg else key2
    else:
        key1 = choice(list(pokemon_1.move_set.keys()))
        key2 = choice(list(pokemon_2.move_set.keys()))

    attack = pokemon_1.attack(pokemon_2, key1)

    if pokemon_1.battle_stats['hp'] <= 0:
        base_df = generate_sequence(p1, p2, optimal, p1_arr, p2_arr, base_df, turn)
        return base_df

    if not pokemon_1.skip_turn:
        pokemon_2.battle_stats['hp'] -= attack
        apply_buff(key1, pokemon_1)
        apply_debuff(key1, pokemon_2)
        pokemon_1_arr.append(key1)
        pokemon_1.move_set[key1] += 1
    pokemon_1.skip_turn = False

    if pokemon_2.battle_stats['hp'] <= 0:
        base_df = generate_sequence(p1, p2, optimal, p1_arr, p2_arr, base_df, turn)
        return base_df

    attack = pokemon_2.attack(pokemon_1, key2)
    if not pokemon_2.skip_turn:
        pokemon_1.battle_stats['hp'] -= attack
        apply_buff(key2, pokemon_2)
        apply_debuff(key2, pokemon_1)
        pokemon_2_arr.append(key2)
        pokemon_2.move_set[key2] += 1
    pokemon_2.skip_turn = False

    base_df = generate_sequence(p1, p2, optimal, p1_arr, p2_arr, base_df, turn)

    return base_df


def create_base_series(friendly_pokemon, enemy_pokemon, turn):
    friendly_series = friendly[friendly['Name'] == friendly_pokemon.name].squeeze()
    enemy_series = enemy[enemy['Enemy Name'] == enemy_pokemon.name].squeeze()

    for k,v in pokemon_moves.items():
        friendly_series[k] = -1

    series = friendly_series.append(enemy_series)
    series = series.drop(labels=['Name', 'Enemy Name', 'Moves'])
    series['Turn'] = turn

    return series

print('Pokemon loaded')