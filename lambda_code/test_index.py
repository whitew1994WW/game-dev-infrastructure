from index import handler
import json
from unittest.mock import patch
import ast


def test_handler():
    event = {
        'body': '{"gameDescription":"","gameType":"Action-adventure","graphicView":"Side scroller","graphicStyle":"Fantasy, hand drawn","multiplayerOption":"Single player, local multiplayer","plot":"The kingdom has been plunged into darkness by an evil sorcerer who seeks to gain ultimate power. As the last remaining ninja warrior, it is up to the player to defeat the sorcerer and save the kingdom. Along the way, they will encounter various challenges and obstacles, from treacherous terrain to powerful enemies. With the help of their ninja skills and special abilities, the player must navigate through different environments and battle their way to the sorcerer\'s castle. But the sorcerer is not alone, as he has summoned powerful creatures to defend him. The player must use all their skills and wit to defeat the sorcerer and restore peace to the kingdom.","characters":[{"name":"ninja warrior","player":"player","description":"agile and skilled"},{"name":"sorcerer","player":"enemy","description":"powerful and menacing"},{"name":"magical creatures","player":"enemy","description":"various types and abilities"},{"name":"king","player":"friendly","description":"wise and kind"},{"name":"queen","player":"friendly","description":"brave and resourceful"}],"colourSchemes":[{"colour":"black","label":"main colour"},{"colour":"red","label":"accent colour"},{"colour":"green","label":"accent colour"},{"colour":"purple","label":"accent colour"},{"colour":"gold","label":"accent colour"}],"styleKeywords":"Fantasy, action-packed, magical, adventurous, fast-paced, challenging, epic, mystical, heroic, mythical","environments":[{"name":"forest","description":"a mystical forest filled with magical creatures"},{"name":"mountains","description":"treacherous mountains with steep cliffs and icy terrain"},{"name":"cave","description":"a dark and dangerous cave with hidden treasures"},{"name":"village","description":"a peaceful village with friendly inhabitants"},{"name":"sorcerer\'s castle","description":"a towering castle with powerful defenses)"}]}'
    }
    context = {}
    response = handler(event, context)
    response = response['body']
    response = json.loads(response)
    # Check keys are in response
    assert 'plot' in response
    assert 'colourSchemes' in response
    assert 'environments' in response
    assert 'characters' in response
    assert 'styleKeywords' in response
    assert 'gameDescription' in response
    assert 'graphicView' in response
    assert 'gameType' in response
    assert 'multiplayerOption' in response
    # Check values are not empty
    assert response['plot'] != ''
    assert response['colourSchemes'] != ''
    assert response['environments'] != ''
    assert response['characters'] != ''
    assert response['styleKeywords'] != ''
    assert response['gameDescription'] != ''
    assert response['graphicView'] != ''
    assert response['gameType'] != ''
    assert response['multiplayerOption'] != ''


def test_handler_patched():
    api_output = ast.literal_eval("""{'id': 'chatcmpl-8X6hQ0IL4AHk7G4Q2JIFUTYw77JZ0', 'object': 'chat.completion', 'created': 1702901268, 'model': 'gpt-4-0613', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': ''}, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 369, 'completion_tokens': 406, 'total_tokens': 775}, 'system_fingerprint': None}""")
    api_output['choices'][0]['message']['content'] = """plot:\n\nWhen the heroine of our story, a courageous feline named Whiskers, stumbles upon an ancient paw-shaped amulet, she is granted superpowers and embarks on a mission to save her city from an evil rat syndicate. \n\ncolour scheme, comma seperated list of precise colour names with a label describing how the colour fits into the palette e.g. "(colour; main colour)::(colour; accent colour)":\n\n(buff orange; main colour - Whiskers\' fur colour)::(jet black; accent colour - outline detail colour)::(crimson; secondary colour - evil rat syndicate logo colour)\n\nenvironments, comma seperated list of environments and a short description of the scene e.g. "(forest; a dark forest with tall trees)::(cave; a dark cave with stalagmites and stalactites)::(castle; a castle with a moat and drawbridge)":\n\n(city streets; gritty and bustling urban environment with tall buildings and neon lights)::(sewers; dark and labyrinthine, filled with treacherous rat traps and hidden rat syndicate bases)::(sky scraper; final level, a towering glass skyscraper housing the rat syndicate’s mastermind)\n\ncharacter list, with flags indicating if the character is an enemy and if they are the player e.g. "(character; enemy_flag; player_flag; visual description)::(character; enemy_flag; player_flag; visual description)":\n\n(Whiskers; false; true; a brave orange tabby with bright green eyes and the ancient paw-shaped amulet)::(Rat minion; true; false; evil grey rats, wearing syndicate bandanas)::(Rat Boss; true; false; a formidable black rat wearing a crimson cape and crown)\n\nstyle keywords, comma seperated list of words that describe the style of the game e.g. "fantasy, medieval, futuristic, modern, historic, gory, cute":\n\n"urban, superhero, fantasy, cute, action-packed, vibrant"\n\n***"""
    print(api_output['choices'][0]['message']['content'])
    # raise ValueError()
    event = {
        'body': '{"gameDescription": "a game about a cat", "graphicView": "top down", "gameType": "action", "multiplayerOption": "single player"}'
    }
    with patch('index.query_openai_chat_gpt4') as mock_query_openai_chat_gpt4:
        mock_query_openai_chat_gpt4.return_value = api_output
        response = handler(event, {})
    raise Exception(response)

test_handler()