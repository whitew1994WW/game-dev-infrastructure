from generate_all_details import generate_all_details
from generate_character_tilesheet import generate_character_tilesheet
from errors import ValidationError


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
        else:
            return {
                'statusCode' : 404,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body' : 'Not found'
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
        return {
            'statusCode' : 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : str(e)
        }
    
    
    