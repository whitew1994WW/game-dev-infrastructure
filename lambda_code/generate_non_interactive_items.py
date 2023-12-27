from generate_character_tilesheet import call_image_api
from generate_all_details import query_openai_chat_gpt4
import json
from errors import ValidationError



def generate_non_interactive_items(event):

    list_of_environment_details_prompt = """You are a game designer for a video game company. You are tasked with listing the non-interactive objects required in a specific game scene. 
game description: {gameDescription}
graphic view (eg. side scroller, isometric, top down): {graphicView}
game type (eg. action, adventure, role playing): {gameType}
style keywords: {styleKeywords}
colour scheme (e.g. (Black, main colour), (Green, accent colour)): {colourSchemes}
envionment name: {environmentName}
environment description: {environmentDescription}
non-interactive objects in comma seperated non-numbered list (e.g. "lamppost, vines, suit of armour, painting"): """

    environment_detail_prompt = """My prompt has full detail so DO NOT add more. DO NOT INCLUDE THE NAME OF THE GAME OR GENERATE A SCENE: Generate an non-interactive object tilesheet for a 2D {gameType} game from a {graphicView} perspective. The tilesheet should contain multiple tiles with each containing a non-interactive object. Each tile should be standalone. The tiles should not have any background graphics. Each tile should be non-overlapping. The image should contain no text. Include a border around the edge of the tilesheet.
Keywords that describe the style of the image: {styleKeywords}
Colours to use in the image: {colourSchemes}
envionment name: {environmentName}
environment description: {environmentDescription}
Some non-interactive objects that the image could contain: {nonInteractiveObjects}
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
    list_of_environment_details_prompt = list_of_environment_details_prompt.format(**variables)
    print(list_of_environment_details_prompt)
    non_inteactive_items_list = query_openai_chat_gpt4(list_of_environment_details_prompt, api_key)
    print('Got interactive items')

    variables['nonInteractiveObjects'] = non_inteactive_items_list
    environment_detail_prompt = environment_detail_prompt.format(**variables)
    print('Got interactive items prompt')

    image_url = call_image_api(environment_detail_prompt, size='1792x1024', quality='standard', n=1, api_key=api_key)
    print('Got image url')
    return json.dumps({'imageUrl': image_url, 'nonInteractiveItems': non_inteactive_items_list})