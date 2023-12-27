from generate_all_details import generate_all_details
from generate_character_tilesheet import generate_character_tilesheet
from generate_environment_tilesheet import generate_environment_tilesheet
from generate_interactive_items import generate_interactive_items
from generate_non_interactive_items import generate_non_interactive_items
from errors import ValidationError
import traceback

def handler(event, context):
    print(event)
    try:
        if event['path'] == '/api/generate_all_details':
            print('Generating all details')
            return {
                'statusCode' : 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : generate_all_details(event)
            }
        elif event['path'] == '/api/generate_character_tilesheet':
            print('Generating character tilesheet')
            return {
                'statusCode' : 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : generate_character_tilesheet(event)
            }
        elif event['path'] == '/api/generate_environment_tilesheet':
            print('Generating environment tilesheet')
            return {
                'statusCode' : 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : generate_environment_tilesheet(event)
            }
        elif event['path'] == '/api/generate_interactive_items':
            print('Generating interactive items')
            return {
                'statusCode' : 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : generate_interactive_items(event)
            }
        elif event['path'] == '/api/generate_non_interactive_items':
            print('Generating non-interactive items')
            return {
                'statusCode' : 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : generate_non_interactive_items(event)
            }
        else:
            return {
                'statusCode' : 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : 'Endpoint not found'
            }
    except ValidationError as e:
        return {
            'statusCode' : 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : str(e)
        }
    except Exception as e:
        print(traceback.format_exc())
        return {
            'statusCode' : 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : str(e)
        }
    
    
    