import cbpro
import schedule
import json
from time import sleep


def generate_accounts(raw_accounts):
    accounts = dict()
    for account in raw_accounts:
        coin = account['currency']
        balance = float(account['balance'])
        if balance > 0:
            accounts[coin] = balance
            print(coin, balance)
    return accounts


def place_order(auth_client, order):
    coin = order[0]
    amount = order[1]

    if amount is not None and not 0:
        response = auth_client.place_market_order(product_id=coin, side='buy', funds=amount)
        if 'message' in response and response['message'] == 'Insufficient funds':
            print("INSUFFICIENT FUNDS! Ending loop.")
            exit(-1)

        transaction_id = response['id']
        check_transaction = auth_client.get_order(transaction_id)
        success = check_transaction['settled'] == "True"

        if not success:
            attempts = 0
            while attempts < 10:
                sleep(5)
                check_transaction = auth_client.get_order(transaction_id)
                print(check_transaction)
                success = check_transaction['settled'] == "True"
                if not success:
                    attempts += 1
                    purchase_amount = check_transaction['filled_size']
                    print(f"Successful purchase of {purchase_amount} {coin} for ${amount} after {attempts} attempts.")
                    break
                else:
                    check_transaction = True
                    purchase_amount = check_transaction['filled-size']
                    print(
                        f"Successful purchase of {purchase_amount} {coin} for ${amount} after {attempts + 1} attempts.")
                    break
            if not check_transaction:
                print(f"ABSOLUTE FAILURE:\tUnsuccessful purchase of {coin}. Attempt #{attempts + 1}")
        else:
            purchase_amount = response['filled_size']
            print(f"Successful purchase of {purchase_amount} {coin} for ${amount}.")


def validate_config(key, secret, frequency_type, frequency):
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


def validate_order_request(client, requests):
    markets = generate_markets(client)
    valid_orders = list()
    for request in requests:
        trading_pair = request[0]
        if trading_pair in markets:  # Valid trading pair
            print(str(trading_pair) + " " + str(markets[trading_pair]))
            min_order = markets[trading_pair]['min_market']  # Minimum allowable market-order
            max_order = markets[trading_pair]['max_market']  # Maximum allowable market-order
            enabled = not markets[trading_pair]['enabled']  # API returns if trading is disabled. Disabled check -> Enabled check
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


def generate_markets(client):
    markets = client.get_products()
    valid_pairs = dict()
    for market in markets:
        this_market = dict()
        trading_pair = market['id']
        min_market = market['min_market_funds']
        max_market = market['max_market_funds']
        enabled = market['status'] == 'False' and market['post_only'] == 'False' and market[
            'cancel_only'] == 'False' and market['limit_only'] == 'False'  # API returns if trading is DISABLED

        this_market['min_market'] = float(min_market)
        this_market['max_market'] = float(max_market)
        this_market['enabled'] = enabled

        valid_pairs[trading_pair] = this_market
    return valid_pairs


def DCA(public_client, auth_client, raw_orders):
    valid_orders = validate_order_request(public_client, raw_orders)
    for order in valid_orders:
        place_order(auth_client, order)


if __name__ == '__main__':
    public_client = cbpro.PublicClient()

    config = None
    with open('config.json') as config_file:
        config = json.load(config_file)

    key = config['api-key']
    secret = config['api-secret']
    passphrase = config['api-passphrase']
    frequency = config['frequency']
    frequency_type = str(config['frequency-type'].lower())
    if type(frequency) == str:
        frequency = frequency.lower()
    raw_orders = config['purchase']
    requested_orders = list()
    for request in raw_orders:
        trading_pair = request['trading-pair'].upper()
        amount = request['amount']
        print(trading_pair, amount)
        order = tuple((trading_pair, amount))
        requested_orders.append(order)

    auth_client = cbpro.AuthenticatedClient(key, secret, passphrase,
                                            api_url="https://api-public.sandbox.pro.coinbase.com")  # Sandbox/testing API
    # auth_client = cbpro.AuthenticatedClient(key, secret, passphrase)  # Live-market API
    raw_accounts = auth_client.get_accounts()
    accounts = generate_accounts(raw_accounts)

    generic_types = {'seconds', 'minutes', 'hours', 'days', 'weeks'}
    if frequency_type in generic_types:
        req = getattr(schedule.every(frequency), frequency_type)
        req.do(DCA, public_client=public_client, auth_client=auth_client,
                                                    raw_orders=requested_orders)
    elif frequency_type == 'day':
        req = getattr(schedule.every(1), frequency)
        req.do(DCA, public_client=public_client, auth_client=auth_client,
                                      raw_orders=requested_orders)

    while True:
        schedule.run_pending()
