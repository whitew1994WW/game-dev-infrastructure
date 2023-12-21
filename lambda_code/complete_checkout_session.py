import json
import stripe


stripe.api_key = 'sk_test_51OPTkdEBfnJt852SuMxwdwcg8wyfwSlUikJSWIq4QpdjunECzwzDQ5ZZxxEQUqEmXbdEbEFR6D77tpaltwEkOyP200Ij264v1g'

# def alternative_verification(session):
#     sig_header = request.headers['STRIPE_SIGNATURE']

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         # Invalid payload
#         raise e
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         raise e

#     # Handle the event
#     if event['type'] == 'checkout.session.completed':
#       session = event['data']['object']
#     # ... handle other event types
#     else:
#       print('Unhandled event type {}'.format(event['type']))
#     pass

def verify_session(session):
    payment_completed = session['payment_status'] == 'paid'
    if payment_completed:
        return True
    else:
        return False
    
def get_token_details(session):
    username = session['metadata']['username']
    num_tokens = session['metadata']['num_tokens']
    return username, num_tokens

def complete_checkout_session(event):
    body = json.loads(event['body'])
    session = body
    
    if verify_session(session):
        username, num_tokens = get_token_details(session)
        token_handler = TokenHandler(username)
        token_handler.add_tokens_to_user(num_tokens)
        return {
            'statusCode' : 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : 'Token added'
        }
    else:
        return {
            'statusCode' : 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body' : 'Payment not completed'
        }



class TokenHandler:
    def __init__(self, username):
        print(f'Creating token handler for user: {username}')
        self.username = username
    def add_tokens_to_user(self, num_tokens):
        print(f'Adding {num_tokens} tokens to user: {self.username}')
        # Store the session id as having been completed
        pass

    def get_available_tokens(self):
        print(f'Getting available tokens for user: {self.username}')
        pass

    def spend_tokens(self, num_tokens):
        print(f'Spending {num_tokens} tokens for user: {self.username}')
        pass