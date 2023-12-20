import json
import stripe
import os

domain = 'https://d2g616vd3ybkz1.cloudfront.net'
def create_checkout_session(event, context):
    # stripe.api_key = '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' LIVE KEY
    stripe.api_key = 'sk_test_51OPTkdEBfnJt852SuMxwdwcg8wyfwSlUikJSWIq4QpdjunECzwzDQ5ZZxxEQUqEmXbdEbEFR6D77tpaltwEkOyP200Ij264v1g'
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1OPTxIEBfnJt852SEBqU2nFE',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url= f'{domain}/success.html',
            cancel_url= f'{domain}/cancel.html',
        )
        return {
            'statusCode': 303,
            'headers': {'Location': checkout_session.url},
            'body': json.dumps({'url': checkout_session.url})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }