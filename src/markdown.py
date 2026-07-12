from collections import defaultdict
from urllib.parse import urlencode
import os
import re
import ast

import chess
import yaml

with open('data/settings.yaml', 'r') as settings_file:
    settings = yaml.load(settings_file, Loader=yaml.FullLoader)


def create_link(text, link):
    return f"[{text}]({link})"

def create_issue_link(source, dest_list):
    issue_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['move'], safe="{}"))

    ret = [create_link(dest, issue_link.format(source=source, dest=dest)) for dest in sorted(dest_list)]
    return ", ".join(ret)

def generate_top_moves():
    with open("data/top_moves.txt", 'r') as file:
        dictionary = ast.literal_eval(file.read())

    markdown = "\n"
    markdown += "| Total moves |  User  |\n"
    markdown += "| :---------: | :----- |\n"

    max_entries = settings['misc']['max_top_moves']
    for key,val in sorted(dictionary.items(), key=lambda x: x[1], reverse=True)[:max_entries]:
        markdown += "| {} | {} |\n".format(val, create_link(key, "https://github.com/" + key[1:]))

    return markdown + "\n"

def generate_last_moves():
    markdown = "\n"
    markdown += "| Move | Author |\n"
    markdown += "| :--: | :----- |\n"

    counter = 0

    with open("data/last_moves.txt", 'r') as file:
        for line in file.readlines():
            parts = line.rstrip().split(':')

            if not ":" in line:
                continue

            if counter >= settings['misc']['max_last_moves']:
                break

            counter += 1

            match_obj = re.search('([A-H][1-8])([A-H][1-8])', line, re.I)
            if match_obj is not None:
                source = match_obj.group(1).upper()
                dest   = match_obj.group(2).upper()

                markdown += "| `" + source + "` to `" + dest + "` | " + create_link(parts[1], "https://github.com/" + parts[1].lstrip()[1:]) + " |\n"
            else:
                markdown += "| `" + parts[0] + "` | " + create_link(parts[1], "https://github.com/" + parts[1].lstrip()[1:]) + " |\n"

    return markdown + "\n"

def generate_moves_list(board):
    # Create dictionary and fill it
    moves_dict = defaultdict(set)

    for move in board.legal_moves:
        source = chess.SQUARE_NAMES[move.from_square].upper()
        dest   = chess.SQUARE_NAMES[move.to_square].upper()

        moves_dict[source].add(dest)

    # Write everything in Markdown format
    markdown = ""

    if board.is_game_over(claim_draw=True) or not os.path.exists('games/current.pgn'):
        issue_link = settings['issues']['link'].format(
            repo=os.environ["GITHUB_REPOSITORY"],
            params=urlencode(settings['issues']['new_game']))

        return "**GAME IS OVER!** " + create_link("Click here", issue_link) + " to start a new game :D\n"

    if board.is_check():
        markdown += "**CHECK!** Choose your move wisely!\n"

    markdown += "|  FROM  | TO (Just click a link!) |\n"
    markdown += "| :----: | :---------------------- |\n"

    for source,dest in sorted(moves_dict.items()):
        markdown += "| **" + source + "** | " + create_issue_link(source, dest) + " |\n"

    resign_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['resign']))
    markdown += f"\n\nOr you can [🏳️ Resign game]({resign_link}) if you think there is no hope!"

    allowed_themes = ['default', 'neon', 'wood', 'cyberpunk']
    theme_links = []
    for t in allowed_themes:
        theme_issue_params = {
            'body': settings['issues']['change_theme']['body'],
            'title': settings['issues']['change_theme']['title'].format(theme=t)
        }
        link = settings['issues']['link'].format(
            repo=os.environ["GITHUB_REPOSITORY"],
            params=urlencode(theme_issue_params)
        )
        theme_links.append(f"[{t.capitalize()}]({link})")

    markdown += f"\n\n🎨 **Change Theme**: {', '.join(theme_links)}"

    return markdown


def get_current_theme():
    if os.path.exists('data/theme.txt'):
        with open('data/theme.txt', 'r') as file:
            return file.read().strip().lower()
    return 'default'

def board_to_markdown(board):
    board_list = [[item for item in line.split(' ')] for line in str(board).split('\n')]
    markdown = ""

    theme = get_current_theme()
    theme_prefix = f"img/themes/{theme}"

    # Write header in Markdown format
    if board.turn == chess.BLACK:
        markdown += "|   | H | G | F | E | D | C | B | A |   |\n"
    else:
        markdown += "|   | A | B | C | D | E | F | G | H |   |\n"
    markdown += "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    # Get Rows
    rows = range(1, 9)
    if board.turn == chess.BLACK:
        rows = reversed(rows)

    # Write board
    for row in rows:
        markdown += "| **" + str(9 - row) + "** | "
        columns = board_list[row - 1]
        
        # Determine files to iterate
        files = list(range(8))
        if board.turn == chess.BLACK:
            files = list(reversed(files))

        for col_idx in files:
            elem = columns[col_idx]
            
            # Find rank_idx (0 to 7)
            # Row 1 corresponds to rank 7 (8th rank)
            # Row 8 corresponds to rank 0 (1st rank)
            rank_idx = 8 - row
            
            # Get square and color
            square = chess.square(col_idx, rank_idx)
            is_light = bool(chess.BB_LIGHT_SQUARES & (1 << square))
            sq_type = 'light' if is_light else 'dark'
            
            # Map elements dynamically
            if elem == '.':
                img_path = f"{theme_prefix}/blank_{sq_type}.svg"
            else:
                piece_names = {
                    "r": "rook", "n": "knight", "b": "bishop", "q": "queen", "k": "king", "p": "pawn",
                    "R": "rook", "N": "knight", "B": "bishop", "Q": "queen", "K": "king", "P": "pawn"
                }
                piece_color = "black" if elem.islower() else "white"
                piece_name = piece_names[elem]
                img_path = f"{theme_prefix}/{piece_color}/{piece_name}_{sq_type}.svg"
                
            markdown += f'<img src="{img_path}" width=50px> | '

        markdown += "**" + str(9 - row) + "** |\n"

    # Write footer in Markdown format
    if board.turn == chess.BLACK:
        markdown += "|   | **H** | **G** | **F** | **E** | **D** | **C** | **B** | **A** |   |\n"
    else:
        markdown += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"

    return markdown
