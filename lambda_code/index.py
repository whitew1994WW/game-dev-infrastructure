from generate_all_details import generate_all_details
from generate_character_tilesheet import generate_character_tilesheet
from create_checkout_session import create_checkout_session


def handler(event, context):
    # call the relevant function based on the api path
    print(event)
    if event['path'] == '/api/generate_all_details':
        return {
            'statusCode' : 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : generate_all_details(event)
        }
    elif event['path'] == '/api/generate_character_tilesheet':
        return {
            'statusCode' : 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : generate_character_tilesheet(event)
        }
    elif event['path'] == '/api/create_checkout_session':
        response = create_checkout_session(event, context)
        return response
    else:
        return {
            'statusCode' : 404,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : 'Not found'
        }
    
    