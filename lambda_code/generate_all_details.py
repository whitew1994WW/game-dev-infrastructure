import json
import requests


openai_api_key = "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"

def query_openai_chat_gpt4(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",  # Specify the model here
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def query_openai_gpt3_5(prompt):
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo-instruct",  # Specify the model here
        "prompt": prompt,
        "max_tokens": 3000,
        'temperature': 0.5
    }
    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    return response.json()['choices'][0]['text']

def extract_variables(response, missing_options, item_prompts):
    # Trim the final *** from the response
    variables = {}
    for option in missing_options:
        variables[option] = ''
    response = response.replace('START TEMPLATE', '')
    response = response.replace('END TEMPLATE', '')
    response_lines = response.split('\n')
    current_line_idx = 0
    option_starting_lines = [item_prompts[option] for option in missing_options]

    for i, option_starting_line in enumerate(option_starting_lines):
        print(f'option starting line: {option_starting_line}')
        while True:
            this_line = response_lines[current_line_idx]
            if not this_line.strip():
                pass
            elif response_lines[current_line_idx][0].strip().isdigit():
                break
            print(f'{response_lines[current_line_idx]}')
            print(f'Not found starting line. Advancing')
            current_line_idx += 1
        print('Found starting line at idx: ' + str(current_line_idx))
        print(f'Current line: {response_lines[current_line_idx]}')

        variable_lines = []
        while True:
            current_line_idx += 1
            if '***' in response_lines[current_line_idx]:
                print(f'Adding line: {response_lines[current_line_idx]}')
                variable_lines.append(response_lines[current_line_idx].replace('***', ''))
                break
            else:
                if not response_lines[current_line_idx]:
                    continue
                elif response_lines[current_line_idx][0].strip().isdigit():
                    break
                else:
                    print(f'Adding line: {response_lines[current_line_idx]}')
                    variable_lines.append(response_lines[current_line_idx])

        print(f'Stopping at line: {response_lines[current_line_idx]}')
        print(f'Variable {missing_options[i]}: {variable_lines}')
        variables[missing_options[i]] = ' '.join(variable_lines)
    return variables


def handle_inputs(event):
    potential_body_options = ['gameDescription', 'gameType', 'graphicView', 'graphicStyle', 'multiplayerOption', 'plot', 'characters', 'colourSchemes', 'styleKeywords', 'environments']
    body = json.loads(event['body'])
    if 'characters' in body:
        if len(body['characters']) == 0:
            body['characters'] = ''
        elif body['characters'][0]['name'] == '':
            body['characters'] = ''
    
    if 'environments' in body:
        if len(body['environments']) == 0:
            body['environments'] = ''
        elif body['environments'][0]['name'] == '':
            body['environments'] = ''

    if 'colourSchemes' in body:
        if len(body['colourSchemes']) == 0:
            body['colourSchemes'] = ''
        elif body['colourSchemes'][0]['colour'] == '':
            body['colourSchemes'] = ''

    missing_options = []
    present_options = []
    for option in potential_body_options:
        if option not in body:
            missing_options.append(option)
        elif body[option] != '':
            present_options.append(option)
        else:
            missing_options.append(option)


    return body,missing_options,present_options

def build_prompt(body, missing_options, present_options):
    initial_prompt = """You are a script writer for a 2D video game company. You have been given a game description, the graphic view of the game (for instance isometric/top down/side scroller), the game type (for instance action/adventure/role playing) and the multiplayer option (for instance single player/online multiplayer/local multiplayer)."""
    item_prompts = {
        'gameDescription': """game description (minimum 100 words).""",
        'gameType': """game type (e.g. adventure, puzzle, shoot'em up).""",
        'graphicView': """graphic view (e.g. top down, side scroller, isometric).""",
        "graphicStyle": """graphic style (e.g. pixel art, cartoon, animated, vector graphics, hand drawn, minimalist, retro, realistic, abstract, paper cut out, fantasy...).""",
        'multiplayerOption': """multiplayer option (e.g. single player, online multiplayer).""",
        'plot': """plot (minimum 100 words).""",
        'characters': """character list, with a label of either 'player', 'friendly' or 'enemy'. Format the output as a json list with list elements having keys "name", "label" and "description". The description should be a physical description of the character only and not other details.""",
        'colourSchemes': """colour scheme, comma seperated list of at least 5 precise colour names with a label describing how the colour fits into the palette. Format the output as a json list with list elements having keys "colour" and "label".""",
        'styleKeywords': """style keywords, comma seperated list of at least 10 words that describe the style of the game e.g. "fantasy, medieval, futuristic, modern, historic, gory, cute".""",
        'environments': """environments, comma seperated list of at least 5 environments and a short description of the what the scene looks like. Format the output as a valid json list with list elements having keys "name" and "description".""",
    }


    prompt = initial_prompt

    for option in present_options:
        prompt = prompt + '\n\n' + item_prompts[option] + '\n\n' + json.dumps(body[option])
    
    second_prompt = """Complete the template below, only replacing the '[INSERT]' and keeping other text and new lines."""
    prompt = prompt + '\n\n' + second_prompt + '\n\nSTART TEMPLATE'

    for i, option in enumerate(missing_options):
        prompt = prompt + f'\n\n{i+1}. ' + item_prompts[option] + '\n\n[INSERT]'

    prompt = prompt + '\n\n' + 'END TEMPLATE\n\n'
    return item_prompts,prompt

def parse_characters(characters):
    return json.loads(characters)

def parse_environments(environments):
    return json.loads(environments)

def parse_colour_scheme(colour_scheme):
    return json.loads(colour_scheme)

def generate_all_details(event):
    body, missing_options, present_options = handle_inputs(event)
    print(f'Body: {body}')
    print(f'Missing options: {missing_options}')
    print(f'Present options: {present_options}')
    item_prompts, prompt = build_prompt(body, missing_options, present_options)
    print(prompt)
    # raise Exception(prompt)
    generated_text = query_openai_gpt3_5(prompt)
    generated_text = generated_text + '\n***'
    print(generated_text)

    missing_variables = extract_variables(generated_text, missing_options, item_prompts)
    print(missing_variables)
    if 'characters' in missing_variables:
        missing_variables['characters'] = parse_characters(missing_variables['characters'])
    if 'environments' in missing_variables:
        missing_variables['environments'] = parse_environments(missing_variables['environments'])
    if 'colourSchemes' in missing_variables:
        missing_variables['colourSchemes'] = parse_colour_scheme(missing_variables['colourSchemes'])
    variables = {**missing_variables, **{var: body[var] for var in present_options}}
    print(variables)
    return_body = json.dumps(variables)
    return return_body