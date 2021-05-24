import cbpro
import schedule
import json
import csv
from time import sleep
from os.path import isfile


def generate_accounts(raw_accounts):  # Pull account balances from Coinbase API
    accounts = dict()
    print("Balances:\n--------------------")
    for account in raw_accounts:
        coin = account['currency']
        balance = float(account['balance'])
        if balance > 0:
            accounts[coin] = balance
            print(coin, balance)
    print("--------------------")
    return accounts


def check_transaction(transaction_id, auth_client):  # Pull the status of an order request from Coinbase API
    this_order = auth_client.get_order(transaction_id)
    success = bool(this_order['settled'])
    return success, this_order


def place_order(auth_client, order, writer):  # Orders are passed in individually from DCA and create a market order
    coin = order[0]
    amount = order[1]

    if amount is not None and not 0:
        response = auth_client.place_market_order(product_id=coin, side='buy', funds=amount)
        if 'message' in response and response['message'] == 'Insufficient funds':
            print("INSUFFICIENT FUNDS! Ending loop.")
            exit(-1)
        sleep(2)
        transaction_id = response['id']
        success, order = check_transaction(transaction_id, auth_client)

        if not success:
            attempts = 1
            while attempts < 9:
                sleep(2)
                success, order = check_transaction(transaction_id, auth_client)
                if not success:
                    attempts += 1
                    print(f"Unsuccessful purchase of {coin}. Attempt #{attempts}")
                    continue
                if success:
                    purchase_amount = order['filled-size']
                    print(order)
                    print(f"Successful purchase of {purchase_amount} {coin} for ${amount} after {attempts + 1} attempts.\n")
                    date_time = str(order['done_at']).split('T')
                    transaction_time = date_time[1]
                    transaction_date = date_time[0]
                    to_write = [transaction_date, transaction_time, coin, purchase_amount, amount, "True"]
                    writer.writerow(to_write)
                    return True
            if not success:
                print(f"ABSOLUTE FAILURE:\tUnsuccessful purchase of {coin}. Attempt #{attempts + 1}")
                date_time = str(order['done_at']).split('T')
                transaction_time = date_time[1]
                transaction_date = date_time[0]
                to_write = [transaction_date, transaction_time, coin, "X", "X", "False"]
                writer.writerow(to_write)
                print("\n")
                return False
        else:
            print(order)
            purchase_amount = str(order['filled_size'])
            print(f"Successful purchase of {purchase_amount} {coin} for ${amount}.\n")
            date_time = str(order['done_at']).split('T')
            transaction_time = date_time[1]
            transaction_date = date_time[0]
            to_write = [transaction_date, transaction_time, coin, purchase_amount, amount, "True"]
            writer.writerow(to_write)
            return True


def validate_config(key, secret, frequency_type, frequency, api_type):  # Ensure the configuration JSON is formatted correctly
    if type(key) != str:
        print("API Key is not a string. Edit the configuration file and ensure api-key is formatted "
              "correctly.\nEnding loop.")
        exit(-1)

    if type(secret) != str:
        print("API Secret is not a string. Edit the configuration file and ensure api-secret is formatted "
              "correctly.\nEnding loop.")
        exit(-1)

    valid_types = {"seconds", "minutes", "hours", "days", "day", "weeks"}
    if type(frequency_type) != str or frequency_type not in valid_types:
        print(f"Invalid 'frequency-type' {frequency_type}. Please check the example config file for acceptable "
              f"frequencies.\nEnding loop.")
        exit(-1)

    valid_days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    if frequency not in valid_days and type(frequency) == str and frequency_type == "day":
        print(f"Invalid day name entered in 'frequency'. Please check the spelling of {frequency}.\nEnding loop.")
        exit(-1)

    numerical_frequencies = {"seconds", "minutes", "hours", "days", "weeks"}
    if type(frequency) == str and frequency_type in numerical_frequencies:
        print(
            f"'frequency-type' / 'frequency' mismatch. Please ensure numerical-type frequencies {numerical_frequencies}"
            f"are not in quotations. Please check your spelling and verify types against the example config file."
            f"\nEnding loop.")
        exit(-1)

    if api_type != "sandbox" and api_type != "production":
        print(f"'api-type' {api_type} is invalid. The API type must be 'sandbox' or 'production'.")
        exit(-1)


def validate_order_request(client, requests):  # Ensure the order request is valid based on active markets and limits
    markets = generate_markets(client)
    valid_orders = list()
    for request in requests:
        trading_pair = request[0]
        if trading_pair in markets:  # Valid trading pair
            min_order = markets[trading_pair]['min_market']  # Minimum allowable market-order
            max_order = markets[trading_pair]['max_market']  # Maximum allowable market-order
            enabled = not markets[trading_pair][
                'enabled']  # API returns if trading is disabled. Disabled check -> Enabled check
            order_size = request[1]
            if not enabled:
                print(f"Order of {trading_pair} cannot be processed because Coinbase Pro has disabled market-orders. "
                      f"This transaction will be ignored!")
                continue
            if order_size > max_order:
                print(f"Order of {trading_pair} cannot be processed because Coinbase Pro's maximum market-order size is"
                      f" {max_order}. This transaction will be ignored!")
                continue
            if order_size < min_order:
                print(f"Order of {trading_pair} cannot be processed because Coinbase Pro's minimum market-order size is"
                      f" {min_order}. This transaction will be ignored!")
                continue
            valid_orders.append(request)  # Valid order request
        else:  # Invalid trading-pair
            print(f"Order of {trading_pair} cannot be processed because it does not match any valid trading-pair on "
                  f"Coinbase Pro. Please check your spelling and confirm the validity of the provided trading pair on "
                  f"Coinbase Pro's website. This transaction will be ignored!")
    return valid_orders


def generate_markets(client):  # Pull available markets from Coinbase API
    markets = client.get_products()
    valid_pairs = dict()
    for market in markets:
        this_market = dict()
        trading_pair = market['id']
        min_market = market['min_market_funds']
        max_market = market['max_market_funds']
        enabled = market['status'] == 'False' and market['post_only'] == 'False' and market['cancel_only'] == 'False' \
                  and market['limit_only'] == 'False'  # API returns if trading is DISABLED
        this_market['min_market'] = float(min_market)
        this_market['max_market'] = float(max_market)
        this_market['enabled'] = enabled
        valid_pairs[trading_pair] = this_market
    return valid_pairs


def DCA(public_client, auth_client, raw_orders, writer, file):  # Main driver function
    valid_orders = validate_order_request(public_client, raw_orders)
    for order in valid_orders:
        place_order(auth_client, order, writer)
        file.flush()


if __name__ == '__main__':
    public_client = cbpro.PublicClient()

    with open('config-personal.json') as config_file:
        config = json.load(config_file)
    api_type = config['api-type'].lower()
    key = config['api-key']
    secret = config['api-secret']
    passphrase = config['api-passphrase']
    frequency = config['frequency']
    frequency_type = str(config['frequency-type'].lower())
    if type(frequency) == str:
        frequency = frequency.lower()
    raw_orders = config['purchase']
    validate_config(key, secret, frequency_type, frequency, api_type)

    requested_orders = list()
    print("Order requests:\n--------------------")
    for request in raw_orders:
        trading_pair = request['trading-pair'].upper()
        amount = request['amount']
        print(trading_pair, amount)
        order = tuple((trading_pair, amount))
        requested_orders.append(order)
    print("--------------------\n")

    log_file_name = "transaction_log.csv"
    if isfile(log_file_name):  # Log file exists
        log_file = open(log_file_name, 'a', newline='')
        writer = csv.writer(log_file)
    else:  # Create the log file
        log_file = open(log_file_name, 'x', newline='')
        headers = ['Date', 'UTC Time', 'Trading Pair', 'Purchased', 'Cost', 'Successful']
        writer = csv.writer(log_file)
        writer.writerow(headers)  # Write the column headers
        log_file.flush()

    if api_type == "sandbox":
        auth_client = cbpro.AuthenticatedClient(key, secret, passphrase,
                                                api_url="https://api-public.sandbox.pro.coinbase.com")  # Sandbox/testing API
    elif api_type == "production":
        auth_client = cbpro.AuthenticatedClient(key, secret, passphrase)  # Live-market API

    raw_accounts = auth_client.get_accounts()
    accounts = generate_accounts(raw_accounts)

    generic_types = {'seconds', 'minutes', 'hours', 'days', 'weeks'}
    if frequency_type in generic_types:
        req = getattr(schedule.every(frequency), frequency_type)
        req.do(DCA, public_client=public_client, auth_client=auth_client,
               raw_orders=requested_orders, writer=writer, file=log_file)
    elif frequency_type == 'day':
        req = getattr(schedule.every(1), frequency)
        req.do(DCA, public_client=public_client, auth_client=auth_client,
               raw_orders=requested_orders, writer=writer, file=log_file)

    while True:
        schedule.run_pending()
