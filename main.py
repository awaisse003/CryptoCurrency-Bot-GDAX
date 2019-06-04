import base64, hashlib, hmac, time
import json, csv
import random
import time
from threading import Thread
import requests
from requests.auth import AuthBase


class GDAXRequestAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


# use our request auth object
def create_buy_order():
    # ---------------------------------------------change your data here :

    order_data = {
        'type': 'limit',
        'side': 'buy',
        'product_id': 'BTC-USD',
        'size': '1',
        'price': '6452.65',
        'time_in_force': 'GTC',
        'post_only': 'true'
    }
    response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
    print('Success in creating Open Buy Order')
    get_order_id()


def get_order_id():
    response = requests.get(api_base + "/orders?status=open", auth=auth)
    order = response.json()
    i = 0
    with open('active_orders.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        while i < len(order):
            data = order[i]['id']
            wr.writerow([data])
            i = i + 1
    print('Updated active_Order.csv .... ')


def check_order_status(order_id):
    response = requests.get(order_url + '/' + order_id, auth=auth)
    result = response.json()
    return result


def create_sell_order():
    # ---------------------------------------------change your data here :
    profit_percentage = 3
    check = False

    try:
        with open('active_orders.csv') as f:
            lines = f.readlines()
            l = len(lines)
        i = 0
        with open('active_orders.csv', newline='') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                order = check_order_status(row[i])
                if order['side'] == 'buy':
                    if order['settled']:
                        print('Found a filled order and creating seller order')
                        with open(order['id'] + '.csv', 'w',
                                  newline='') as myfile:
                            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                            wr.writerow(['order ID : ', order['id']])
                            wr.writerow(['Size ', order['size']])
                            wr.writerow(['product_id', order['product_id']])
                            wr.writerow(['side', order['side']])
                            wr.writerow(['created_at', order['created_at']])
                            wr.writerow(['done_at', order['done_at']])
                            wr.writerow(['done_reason', order['done_reason']])
                            total = ((profit_percentage * (float(order['price']))) / 100)
                            total = total + (float(order['price']))
                            total = "%.2f" % total

                        order_data = {

                            'type': 'limit',
                            'side': 'sell',
                            'product_id': 'BTC-USD',
                            'size': '0.9542',
                            'price': total,

                        }
                        check = True
                        response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
                        print(response.json())
                        i = i + 1
                        if i == (l - 1):
                            break
        if check:
            get_order_id()
    except:
        print('Order is being cancelled and bot will update the active_order.csv File')
        get_order_id()


api_base = 'https://api-public.sandbox.gdax.com'

# ---------------------------------------------change your data here :

api_key = '42496087cb419497c25afb9dbe49ff09'
api_secret = 'G4GzzfzPzD5L6U4mf/+aNfKc2JE1bSTtlXzgSpmxIltr7iUBVAbirMfIdcAcRMXRrx8uv5ONDWG6cpPEk+yflg=='
passphrase = 'zl2439mpyn'

auth = GDAXRequestAuth(api_key, api_secret, passphrase)
order_url = api_base + '/orders'


def timer(name, delay, repeat):
    while repeat > 0:
        time.sleep(delay)
        get_order_id()
        repeat -= 1


def timer1(name, delay, repeat):
    while repeat > 0:
        time.sleep(delay)
        create_sell_order()
        repeat -= 1


def timer2(name, delay, repeat):
    while repeat > 0:
        time.sleep(delay)
        create_sell_order()
        repeat -= 1


create_buy_order()
get_order_id()
print('Running .... ')
try:

    t1 = Thread(target=timer, args=("Timer1", 36000, 500))
    t2 = Thread(target=timer1, args=("Timer2", 1, 99999999999))

    t1.start()
    t2.start()


except:
    t1 = Thread(target=timer, args=("Timer1", 36000, 500))
    t2 = Thread(target=timer1, args=("Timer2", 1, 99999999999))

    t1.start()
    t2.start()
