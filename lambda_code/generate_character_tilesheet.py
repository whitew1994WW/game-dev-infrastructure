import json
import requests
import os


def call_image_api(prompt, size, quality, n):
    openai_api_key = "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"
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "dall-e-3",  # Specify the model here
        "prompt": prompt,
        "n": n,
        "size": size
    }

    response = requests.post(url, headers=headers, json=data)
    body = json.loads(response.text)
    print(body)
    image_url = body['data'][0]['url']
    return image_url


def generate_character_tilesheet(event):
    openai_api_key = "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"
    os.environ["OPENAI_API_KEY"] = openai_api_key
    body = json.loads(event['body'])
    story_board = body['storyBoardState']
    character = body['character']
    sprite_prompt = """Generate a character sprites for a 2D {gameType} game with the details provided below. The image should contain multiple sprites arranged in the image. The sprites should not have any background graphics. Each sprite should be non-overlapping. The image should contain no text. Include a border around the edge of the image. There should be different sprites for each perspective that the character could be viewed in the game, only show perspectives that are possible for a game with the graphic view {graphicView}. Only display the character sprites and no additional information. Do not display the colour palette.
    graphic style keywords: {styleKeywords}
    visual description of the character: {characterDescription}
    character type: {characterLabel}
    colour palette: {colourScheme}
    """

    variables = {
        'styleKeywords': story_board['styleKeywords'],
        'graphicView': story_board['graphicView'],
        'gameType': story_board['gameType'],
        'characterDescription': character['description'],
        'characterLabel': character['label'],
        'colourScheme': '',
    }

    variables['colourScheme'] = ','.join([f" ({colour['colour']}, {colour['label']})" for colour in story_board["colourSchemes"]]).strip()
    this_sprite_prompt = sprite_prompt.format(**variables)
    image_url = call_image_api(this_sprite_prompt, size='1792x1024', quality='standard', n=1)
    return json.dumps({'imageUrl': image_url})