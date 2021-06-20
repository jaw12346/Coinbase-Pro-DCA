from main import *


def validate_config(key, secret, frequency_type, frequency, api_type):
    """Ensure the configuration JSON is formatted correctly for API and orders"""

    if type(key) != str:
        raise TypeError("API Key is not a string. Edit the configuration file and ensure api-key is formatted "
                        "correctly.")

    if type(secret) != str:
        raise TypeError("API Secret is not a string. Edit the configuration file and ensure api-secret is formatted "
              "correctly.")

    valid_types = {"seconds", "minutes", "hours", "days", "day", "weeks"}
    if type(frequency_type) != str or frequency_type not in valid_types:
        raise ValueError(f"Invalid \"frequency-type\" {frequency_type}. Please check the README for acceptable "
                         f"frequencies.")

    valid_days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    if frequency not in valid_days and type(frequency) == str and frequency_type == "day":
        raise ValueError(f"Invalid day name entered in \"frequency\". Please check the spelling of {frequency}.")

    numerical_frequencies = {"seconds", "minutes", "hours", "days", "weeks"}
    if type(frequency) == str and frequency_type in numerical_frequencies:
        raise ValueError(f"\"frequency-type\" / \"frequency\" mismatch. Please ensure numerical-type frequencies "
                         f"{numerical_frequencies} are not in quotations. Please check your spelling and verify types.")

    if api_type != "sandbox" and api_type != "production":
        raise ValueError(f"Config \"api-type\" {api_type} is invalid. The API type must be \"sandbox\" or "
                         f"\"production\".")


def validate_deposit_config(deposit_option, deposit_requested, deposit_amount):
    """Ensure the configuration JSON is formatted correctly for deposits"""

    if (deposit_option is not None) and \
            (deposit_requested == True or str(deposit_requested).lower() == "true" or str(deposit_requested) == "1"):
        deposit_requested = True
    else:
        deposit_requested = False
    print(f"\nAuto-deposit requested: {deposit_requested}\n")

    if deposit_requested:
        deposit_limits = deposit_option["limits"]["deposit"][0]  #TODO: Returns error on 'deposit' when requesting USD Wallet
        deposit_period = deposit_limits["period_in_days"]
        max_per_period = float(deposit_limits["total"]["amount"])
        deposit_currency = deposit_limits["total"]["currency"]
        deposit_symbol = CurrencySymbols.get_symbol(deposit_currency)

        if type(deposit_amount) == str or type(deposit_amount) == bool:
            raise TypeError(f"Invalid auto-deposit type. {deposit_amount} is a {str(type(deposit_amount))}.\n\t"
                            f"Deposit amounts must be in integer or float form.")
        if float(deposit_amount) == 0:
            raise ValueError(f"Requested auto-deposit of {deposit_symbol}0. INVALID REQUEST!")
        if float(deposit_amount) < 0:
            raise ValueError(f"Requested auto-deposit of {deposit_symbol}{deposit_amount} < {deposit_symbol}0. Deposit "
                  f"amounts must be > $0.\n\tINVALID REQUEST!")
        if max_per_period < deposit_amount:
            raise ValueError(f"Requested auto-deposit of {deposit_symbol}{deposit_amount} "
                             f"> {deposit_symbol}{max_per_period} limit per {deposit_period} day(s)."
                             f"\n\tINVALID REQUEST!")
    elif not deposit_requested:
        if float(deposit_amount) != 0:
            print(f"Requested no auto-deposits but provided a deposit amount of: ${deposit_amount}. "
                  f"Script will proceed with no auto-deposit.")
            deposit_amount = 0

    return deposit_requested, deposit_amount


def validate_deposit_request(auth_client, deposit_option, deposit_amount, looping):
    assert deposit_option is not None, "Attempted to validate deposit that was not requested." \
                                       "\n\tCRITICAL DEPOSIT ERROR!"

    deposit_limits = deposit_option["limits"]["deposit"][0]
    deposit_period = deposit_limits["period_in_days"]
    remaining = float(deposit_limits["remaining"]["amount"])
    deposit_currency = deposit_limits["total"]["currency"]
    deposit_symbol = CurrencySymbols.get_symbol(deposit_currency)

    if deposit_amount <= remaining:  # Deposit allowed / end the loop
        return True

    """Starts a recursive loop to check the period deposit limit against the requested deposit amount
       Recursive loop ends once the requested deposit can be filled by CBPro.
    """
    if deposit_amount > remaining and not looping:
        period = lambda deposit_period: "days" if deposit_period > 1 or deposit_period == 0 else "day"
        print(f"Requested deposit of {deposit_symbol}{deposit_amount} > remaining {remaining} in {period} "
              f"{period(deposit_period)}. Script will resume once daily deposit limit is not exceeded.")
        looping = True
        sleep(SECONDS_PER_HOUR)  # Wait 1 hour
        validate_deposit_request(auth_client, deposit_amount, looping)
    if deposit_amount > remaining and looping:
        sleep(SECONDS_PER_HOUR)  # Wait 1 hour
        validate_deposit_request(auth_client, deposit_amount, looping)


def validate_order_request(client, requests):
    """Ensure the order request is valid based on active markets and limits"""

    markets = generate_markets(client)
    valid_orders = list()
    for request in requests:
        trading_pair = request[0]
        if trading_pair in markets:  # Valid trading pair
            min_order = markets[trading_pair]["min_market"]  # Minimum allowable market-order
            max_order = markets[trading_pair]["max_market"]  # Maximum allowable market-order
            enabled = not markets[trading_pair]["enabled"]  # API returns if trading is disabled. Disabled check -> Enabled check
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


def check_transaction(transaction_id, auth_client):
    """Pull the status of an order request from CBPro API"""

    this_order = auth_client.get_order(transaction_id)
    success = bool(this_order["settled"])
    return success, this_order
