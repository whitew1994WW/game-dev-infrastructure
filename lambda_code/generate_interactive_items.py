from generate_character_tilesheet import call_image_api
import json
from errors import ValidationError
from generate_all_details import query_openai_chat_gpt4




def generate_interactive_items(event):
    list_of_interactive_items_prompt = """You are a game designer for a video game company. You are tasked with listing the interactive objects required in a specific game scene. These are non-environment and non-character objects such as power ups, health, potions, weapons, lives etc.
game description: {gameDescription}
graphic view (eg. side scroller, isometric, top down): {graphicView}
game type (eg. action, adventure, role playing): {gameType}
style keywords: {styleKeywords}
envionment name: {environmentName}
environment description: {environmentDescription}
interactive objects in comma seperated non-numbered list: """


    interactive_items_prompt = """My prompt has full detail so DO NOT add more. DO NOT INCLUDE THE NAME OF THE GAME OR GENERATE A SCENE: Generate a landscape object tilesheet for a 2D game based on the parameters below. The tilesheet should contain multiple tiles arranged on the tilesheet, with each containing a interactive object. Each tile should be standalone. The tiles should not have any background graphics. Each tile should be non-overlapping. The image should contain no text. Include a border around the edge of the tilesheet.
game type: {gameType}
graphic view: {graphicView}
style keywords: {styleKeywords}
colour scheme: {colourSchemes}
interactive objects: {interactiveObjects}
"""
    body = json.loads(event['body'])
    story_board = body['storyBoardState']
    environment = body['environment']
    api_key = body['apiKey']

    required_fields = ['gameDescription', 'graphicView', 'gameType', 'styleKeywords', 'colourSchemes', 'environments']
    for field in required_fields:
        if field not in story_board:
            raise ValidationError(f'{field} not provided')
        elif story_board[field] == '':
            raise ValidationError(f'{field} not provided') 
    for field in ['name', 'description']:
        if field not in environment:
            raise ValidationError(f'{field} not provided')
        elif environment[field] == '':
            raise ValidationError(f'{field} not provided')
    print('Validated')
    if 'apiKey' not in body:
        raise ValidationError('API key not provided')
    
    variables = {
        'gameDescription': story_board['gameDescription'],
        'styleKeywords': story_board['styleKeywords'],
        'graphicView': story_board['graphicView'],
        'gameType': story_board['gameType'],
        'environmentDescription': environment['description'],
        'environmentName': environment['name'],
        'colourSchemes': '',
    }

    variables['colourSchemes'] = ','.join([f" ({colour['colour']}, {colour['label']})" for colour in story_board["colourSchemes"]]).strip()
    print('Got variables')
    list_of_interactive_items_prompt = list_of_interactive_items_prompt.format(**variables)
    print(interactive_items_prompt)
    inteactive_items_list = query_openai_chat_gpt4(list_of_interactive_items_prompt, api_key)
    print('Got interactive items')
    variables['interactiveObjects'] = inteactive_items_list
    interactive_items_prompt = interactive_items_prompt.format(**variables)
    print('Got interactive items prompt')
    print(interactive_items_prompt)
    image_url = call_image_api(interactive_items_prompt, size='1792x1024', quality='standard', n=1, api_key=api_key)
    print('Got image url')
    return json.dumps({'imageUrl': image_url, 'interactiveItems': inteactive_items_list})