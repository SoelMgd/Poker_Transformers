from pathlib import Path
import json

def struct_to_format_llm(hand, stop_turn=1):
    """
    Convert hand structure to format required by LLM model
    """

    
    players_names_to_ano = {hand['players'][i]: f"P{i+1}" for i in range(len(hand['players']))}
    players_seat_to_ano = {hand['players_seats'][i]: f"P{i+1}" for i in range(len(hand['players']))}
    BB_amount = hand['big_blind']
    stacks_player = hand['starting_stacks'].copy()
    players_in_game = hand['players'].copy()
    
    out_str = ""
    # [TABLE_CONFIGURATION]
    table_config = f""" 
[TABLE_CONFIGURATION]
BTN={players_seat_to_ano[hand['button_seat']]}
SB={players_names_to_ano[hand['player_small_blind']]} 0.5BB
BB={players_names_to_ano[hand['player_big_blind']]} 1BB\n"""
    pot = 1.5*BB_amount
    turn = 0
    dealed_cards = []
    stacks_player[hand['players'].index(hand['player'])] -= 1*BB_amount
    stacks_player[hand['players'].index(hand['player_small_blind'])] -= 0.5*BB_amount
    out_str += table_config
    for street_key, street_upercase, steet in zip(['pre-flop', 'post-flop', 'post-turn', 'post-river'], ['PREFLOP', 'FLOP', 'TURN', 'RIVER'], [None, 'flop', 'turn', 'river']):
        # [STACKS]
        stacks_str, pot = compute_stacks(hand, pot, stacks_player, BB_amount, players_names_to_ano, players_in_game)
        out_str +=  stacks_str
        # [ACTIONS]
        dealed_cards += hand['dealed_cards'].get(steet, [])
        actions_str, stacks_player, pot, turn, value_strt = compute_actions(hand, hand['actions'][street_key], street_upercase, stacks_player, pot, players_names_to_ano, BB_amount, turn, stop_turn, dealed_cards, players_in_game)
        out_str += actions_str
        if value_strt:
            return out_str, value_strt
    return out_str, None
    
def compute_stacks(hand, pot, stacks_player, BB_amount, players_names_to_ano, players_in_game):
    stacks_str = "\n[STACKS]\n"
    for i, player in enumerate(hand['players']):
        if player not in players_in_game:
            continue
        stack_player_bb = stacks_player[i]/BB_amount
        stacks_str += f"{players_names_to_ano[hand['players'][i]]}: {stack_player_bb:.1f}BB"
        if hand['players'][i] == hand['player']:
            stacks_str += f" [{hand['cards_player'][0]} {hand['cards_player'][1]}]"
        stacks_str += "\n"
    pot_bb = pot/BB_amount
    stacks_str += f"POT={pot_bb:.1f}BB\n"
    return stacks_str, pot

def compute_actions(hand, street_actions, street, stacks_player, pot, players_names_to_ano, BB_amount, turn, stop_turn, deeled_cards, players_in_game):
    actions_str = f"\n[{street}]"
    if deeled_cards:
        actions_str += "["
        for card in deeled_cards:
            actions_str += f" {card}"
        actions_str += "]"
    actions_str += "\n"
    actions_str = actions_str.replace("[ ", "[")
    
    for i, player in enumerate(street_actions['players']):
        action = street_actions['actions'][i]
        
        value = street_actions['values'][i]
        value_str = ""
        if value:
            value_bb = int(value/BB_amount)
            value_str += f" {value_bb}BB\n"
        else:
            value_str += "\n"
        if action in ["BET", "RAISE", "CALL"]:
            stacks_player[hand['players'].index(player)] -= value
            pot += value
        elif action == 'ALLIN':
            stacks_player[hand['players'].index(player)] = 0
            pot += value
        elif action == 'FOLD':
            players_in_game.remove(player)
            
        if player == hand['player']:
            turn += 1
            if turn == stop_turn:
                actions_str += f"{players_names_to_ano[player]}: "
                return actions_str, stacks_player, pot, turn, f"{action}{value_str}"
        actions_str += f"{players_names_to_ano[player]}: {action}{value_str}"
    return actions_str, stacks_player, pot, turn, None

def count_nb_turn(hand):
    count = 0
    for street in hand['actions'].values():
        count += street['players'].count(hand['player'])
    return count

if __name__ == "__main__":
    
    hand = {'date': '2016/11/29 15:22:4', 'game_id': '787026454', 'variant': 'PRR', 'table_name': 'Kraken-10', 'type_game': "Hold'em", 'button_seat': 3, 'players': ['AironVega', 'aleks0v', 'ElvenEyes', 'IlxxxlI', 'WeakAndWeary', 'Sephiroth1'], 'players_seats': [1, 2, 3, 4, 5, 6], 'starting_stacks': [101.0, 100.23, 205.91, 40.0, 100.0, 101.5], 'player_small_blind': 'IlxxxlI', 'small_blind': 0.5, 'player_big_blind': 'WeakAndWeary', 'big_blind': 1.0, 'player': 'IlxxxlI', 'cards_player': ['7s', 'Kh'], 'dealed_cards': {'flop': ['Qh', '2s', '4s'], 'turn': ['Qd'], 'river': ['5c']}, 'actions': {'pre-flop': {'players': ['Sephiroth1', 'AironVega', 'aleks0v', 'ElvenEyes', 'IlxxxlI', 'WeakAndWeary'], 'actions': ['FOLD', 'FOLD', 'FOLD', 'FOLD', 'CALL', 'CHECK'], 'values': [None, None, None, None, 0.5, None]}, 'post-flop': {'players': ['IlxxxlI', 'WeakAndWeary'], 'actions': ['BET', 'CALL'], 'values': [1.26, 1.26]}, 'post-turn': {'players': ['IlxxxlI', 'WeakAndWeary'], 'actions': ['CHECK', 'CHECK'], 'values': [None, None]}, 'post-river': {'players': ['IlxxxlI', 'WeakAndWeary', 'IlxxxlI'], 'actions': ['CHECK', 'BET', 'FOLD'], 'values': [None, 2.15, None]}}, 'card_shown_by_players': [None, None, None, None, None, None], 'finishing_stack': [101.0, 100.23, 205.91, 37.74, 102.03999999999999, 101.5]}
    print(struct_to_format_llm(hand)[0])
    
    PATH_DATA = Path(__file__).resolve().parents[2] / "data" / "structured" / "poker_dataset"
    PATH_DATA_OUT = Path(__file__).resolve().parents[2] / "data" / "train" / "poker_dataset"
    
    with open(PATH_DATA / "hand_8.json", "r") as f:
        hand = json.load(f)
    out_str, value_str = struct_to_format_llm(hand, 4)
    print(out_str)
    print(value_str)
    
    for file in PATH_DATA.glob("*.json"):
        print(f"Processing {file}")
        with open(file, "r") as f:
            hand = json.load(f)
        nb_turn = count_nb_turn(hand)
        for i in range(1, nb_turn+1):
            print(f"Processing turn {i}")
            out_str, value_str = struct_to_format_llm(hand, i)
            out = {'context': out_str, 'truth': value_str}
            name = file.name.split(".")[0]
            with open(PATH_DATA_OUT / f'{name}_{i}.json', "w") as f:
                json.dump(out, f)


"""
[TABLE_CONFIGURATION]
BTN=P7
SB=P1 0.5BB
BB=P2 1BB

[STACKS]
P1: 174.3BB
P2: 126.2BB
P3: 195.6BB
P4: 62.1BB [Ad Kd]
P5: 98.4BB
P6: 190.2BB
P7: 40.0BB
POT=1.5BB

[PREFLOP]
P3: FOLD
P4: RAISE 3BB
P5: CALL 3BB
P6: CALL 3BB
P7: FOLD
P1: FOLD
P2: FOLD

[STACKS]
P4: 58.6BB [Ad Kd]
P5: 94.9BB
P6: 186.7BB
POT=12.0BB

[FLOP][10d 2h 5s]
P4: CHECK
P5: CHECK
P6: CHECK

[STACKS]
P4: 58.6BB [Ad Kd]
P5: 94.9BB
P6: 186.7BB
POT=12.0BB

[TURN][10d 2h 5s 2c]
P4: CHECK
P5: CHECK
P6: CHECK

[STACKS]
P4: 58.6BB [Ad Kd]
P5: 94.9BB
P6: 186.7BB
POT=12.0BB

[RIVER][10d 2h 5s 2c 4d]
P4:
CHECK
"""