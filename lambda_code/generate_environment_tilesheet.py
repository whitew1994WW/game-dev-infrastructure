from generate_character_tilesheet import call_image_api
import json
from errors import ValidationError


def generate_environment_tilesheet(event):
    body = json.loads(event['body'])

    if 'apiKey' not in body:
        raise ValidationError('API key not provided')
    

    api_key = body['apiKey']
    story_board = body['storyBoardState']
    environment = body['environment']
    username = body['username']
    environment_prompt = """Generate an environment tilesheet for a 2D {gameType} game from a {graphicView} perspective. The name of the environment is {environmentName} and a visual description is; {environmentDescription}.The tilesheet should contain multiple tiles with each tile corresponding to a section of ground or interactable environment. The tiles should be building blocks that can be used to build more complex scenes. The tiles should not have any background graphics. Each tile should be non-overlapping. The image should contain no text. Include a border around the edge of the tilesheet. Do not display gridlines in the image.
    style keywords: {styleKeywords}
    colour scheme (e.g. (Black, main colour), (Green, accent colour)): {colourScheme}
    """

    variables = {
        'styleKeywords': story_board['styleKeywords'],
        'graphicView': story_board['graphicView'],
        'gameType': story_board['gameType'],
        'environmentDescription': environment['description'],
        'environmentName': environment['name'],
        'colourScheme': '',
    }

    variables['colourScheme'] = ','.join([f" ({colour['colour']}, {colour['label']})" for colour in story_board["colourSchemes"]]).strip()
    this_sprite_prompt = environment_prompt.format(**variables)
    image_url = call_image_api(this_sprite_prompt, size='1792x1024', quality='standard', n=1, api_key=api_key)
    return json.dumps({'imageUrl': image_url})