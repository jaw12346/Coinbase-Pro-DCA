from main import *


def config_reader(config):
    """Read the configuration file and create script variables"""

    api_type = config["api-type"].lower()
    key = config["api-key"]
    secret = config["api-secret"]
    passphrase = config["api-passphrase"]

    frequency = config["frequency"]
    frequency_type = str(config["frequency-type"].lower())
    if type(frequency) == str:
        frequency = frequency.lower()

    raw_orders = config["purchase"]
    deposit_requested = config["auto-deposit"]
    deposit_amount = config["deposit-amount"]

    return api_type, key, secret, passphrase, frequency, frequency_type, raw_orders, deposit_requested, deposit_amount


def generate_accounts(raw_accounts):
    """Pull account balances from CBPro API"""

    accounts = dict()
    for account in raw_accounts:
        coin = account["currency"]
        balance = float(account["balance"])
        if balance > 0:
            accounts[coin] = balance
    return accounts


def generate_deposit_option(auth_client):
    """Determine deposit payment method and use it for auto-deposits"""

    raw_options = auth_client.get_payment_methods()

    if "message" in raw_options:  # An error has occurred
        message = raw_options["message"]
        if message == "Invalid API Key":
            raise Exception("Coinbase has detected an invalid API key. Please check the \"api-key\" tag in the "
                            "configuration file.")
        else:
            raise Exception(f"Coinbase returns: \"{message}\".\n\tTHIS IS AN UNKNOWN ERROR.\n\tPlease open an issue on "
                            f"the GitHub repository with this error message.")

    print("\nAuto-deposit payment options:\n-----------------------------")
    options = list()
    options.append("Exit")
    print("0:\tEXIT SCRIPT")
    options.append("Turn off auto-deposit")
    print("1:\tTurn off auto-deposit")
    counter = 2
    for option in raw_options:
        allow_buy = option["allow_buy"]
        allow_deposit = option["allow_deposit"]
        if allow_buy and allow_deposit:
            name = option["name"]
            print(f"{counter}:\t{name}")
            options.append(option)
            counter += 1
    print("-----------------------------")
    option_num = int(input("Please select the number corresponding to the payment method you wish to use: "))
    selected = options[option_num]
    while option_num < 0 or option_num >= len(options):  # Selection out of range
        print("\tInvalid selection!")
        option_num = int(input("Please select the number corresponding to the payment method you wish to use: "))
        selected = options[option_num]
    if selected == "Exit":
        print("You selected option 0. Script terminates.")
        exit(0)
    elif selected == "Turn off auto-deposit":
        print("You have selected option 1. Auto-deposit is now turned off for this session.")
        selected = None
        return selected
    else:
        print(f"Auto-deposit selection confirmed: {selected}")
        return selected


def generate_markets(client):
    """Pull available markets from CBPro API"""

    markets = client.get_products()
    valid_pairs = dict()
    for market in markets:
        this_market = dict()
        trading_pair = market["id"]
        min_market = market["min_market_funds"]
        max_market = market["max_market_funds"]
        enabled = market["status"] == "False" and market["post_only"] == "False" and market["cancel_only"] == "False" \
            and market["limit_only"] == "False"  # API returns if trading is DISABLED
        this_market["min_market"] = float(min_market)
        this_market["max_market"] = float(max_market)
        this_market["enabled"] = enabled
        valid_pairs[trading_pair] = this_market
    return valid_pairs


def balance(auth_client, currency):
    """Generate the available balance of a given currency"""

    raw_accounts = auth_client.get_accounts()
    accounts = generate_accounts(raw_accounts)
    this_balance = 0
    if currency in accounts:
        this_balance = accounts[currency]
    return this_balance
