from main import *


# Ensure the configuration JSON is formatted correctly for API and orders
def validate_config(key, secret, frequency_type, frequency, api_type):
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


# Ensure the configuration JSON is formatted correctly for deposits
def validate_deposit_config(deposit_option, deposit_requested, deposit_amount):
    if (deposit_option is not None) and (deposit_requested == True or str(deposit_requested).lower() == "true" or
                                         str(deposit_requested) == "1"):
        deposit_requested = True
    else:
        deposit_requested = False
    print(f"\nAuto-deposit requested: {deposit_requested}\n")

    if deposit_requested:
        deposit_limits = deposit_option["limits"]["deposit"][0]
        deposit_period = deposit_limits["period_in_days"]
        max_per_period = float(deposit_limits["total"]["amount"])
        deposit_currency = deposit_limits["total"]["currency"]
        deposit_symbol = CurrencySymbols.get_symbol(deposit_currency)

        if type(deposit_amount) == str or type(deposit_amount) == bool:
            print(f"Invalid auto-deposit type. {deposit_amount} is a {str(type(deposit_amount))}.\n\tDeposit amounts "
                  f"must be in integer or float form.\n\tABORT!")
            exit(-1)
        if float(deposit_amount) == 0:
            print(f"Requested auto-deposit of {deposit_symbol}0. INVALID REQUEST... ABORT!")
            exit(-1)
        if float(deposit_amount) < 0:
            print(f"Requested auto-deposit of {deposit_symbol}{deposit_amount} < {deposit_symbol}0. Deposit "
                  f"amounts must be > $0.\n\tINVALID REQUEST... ABORT!")
            exit(-1)
        if max_per_period < deposit_amount:
            print(f"Requested auto-deposit of {deposit_symbol}{deposit_amount} > {deposit_symbol}{max_per_period}"
                  f" limit per {deposit_period} day(s).\n\tINVALID REQUEST... ABORT!")
            exit(-1)
    elif not deposit_requested:
        if float(deposit_amount) != 0:
            print(f"Requested no auto-deposits but provided a deposit amount of: ${deposit_amount}. "
                  f"Script will proceed with no auto-deposit.")
            deposit_amount = 0

    return deposit_requested, deposit_amount


def validate_deposit_request(auth_client, deposit_option, deposit_amount, looping):
    # deposit_option = generate_deposit_option(auth_client)
    if deposit_option is None:
        print("\n\tCRITICAL ERROR... ABORT!")  # Partial error message already printed by generation function
        exit(-1)

    deposit_limits = deposit_option["limits"]["deposit"][0]
    deposit_period = deposit_limits["period_in_days"]
    remaining = float(deposit_limits["remaining"]["amount"])
    deposit_currency = deposit_limits["total"]["currency"]
    deposit_symbol = CurrencySymbols.get_symbol(deposit_currency)

    if deposit_amount <= remaining:  # Deposit allowed / end the loop
        looping = False
        return True

    # Starts a recursive loop to check the period deposit limit against the requested deposit amount
    # Recursive loop ends once the requested deposit can be filled by CBPro
    if deposit_amount > remaining and not looping:
        period = lambda deposit_period: "days" if deposit_period > 1 or deposit_period == 0 else "day"
        print(f"Requested deposit of {deposit_symbol}{deposit_amount} > remaining {remaining} in {period} "
              f"{period(deposit_period)}. Script will resume once daily deposit limit is not exceeded.")
        looping = True
        sleep(3600)  # Wait 1 hour
        validate_deposit_request(auth_client, deposit_amount, looping)
    if deposit_amount > remaining and looping:
        sleep(3600)  # Wait 1 hour
        validate_deposit_request(auth_client, deposit_amount, looping)


# Ensure the order request is valid based on active markets and limits
def validate_order_request(client, requests):
    markets = generate_markets(client)
    valid_orders = list()
    for request in requests:
        trading_pair = request[0]
        if trading_pair in markets:  # Valid trading pair
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


# Pull the status of an order request from CBPro API
def check_transaction(transaction_id, auth_client):
    this_order = auth_client.get_order(transaction_id)
    success = bool(this_order['settled'])
    return success, this_order
