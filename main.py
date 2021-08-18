from currency_symbols import CurrencySymbols
from validation import *
from generation import *
import cbpro
import schedule
import json
import csv
import datetime
from time import sleep
from os.path import isfile
import sys
from os import environ

from PyQt5 import QtCore, QtGui, QtWidgets
from setup_gui import Ui_MainWindow
from edit_dca_list_gui import Ui_dca_list_dialog
from add_dca_gui import Ui_add_dca_dialog

PUBLIC_CLIENT = cbpro.PublicClient()

SANDBOX_URL = "https://api-public.sandbox.pro.coinbase.com"
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600


def deposit_fiat(auth_client, deposit_option, deposit_amount, writer, file):
    if validate_deposit_request(auth_client, deposit_option, deposit_amount, False):
        currency = str(deposit_option["currency"])
        payment_method_id = str(deposit_option["id"])
        deposit_order = auth_client.deposit(deposit_amount, currency, payment_method_id)  # Deposit

    # Generate deposit currency symbol for log file
    symbol = CurrencySymbols.get_symbol(currency)
    deposit_w_symb = symbol + str(deposit_amount)

    # Generate timestamp
    month = str(datetime.datetime.today().month)
    day = str(datetime.datetime.today().day)
    year = str(datetime.datetime.today().year)
    date = month + "/" + day + "/" + year
    time = str(datetime.datetime.now().isoformat().split("T")[1]) + "Z"

    if "message" in deposit_order:  # Deposit error
        message = deposit_order["message"]
        to_write = [date, time, currency, deposit_w_symb, deposit_w_symb, message]
        writer.writerow(to_write)
        file.flush()

        if message.startswith("Invalid account"):
            raise Exception(f"Coinbase returns: \"{message}\". Chosen deposit account is broken and cannot be used for "
                            f"DCA.\n\tCRITICAL ERROR... ABORT!")
        elif message.startswith("This amount would exceed"):
            raise Exception(f"Coinbase returns: \"{message}\". Chosen deposit amount exceeds the limit.\n\t"
                            f"CRITICAL ERROR... ABORT!")
        else:
            raise Exception(f"Coinbase returns: \"{message}\".\n\tTHIS IS AN UNKNOWN ERROR... ABORT!")
    else:
        print("\nDeposit request result: " + str(deposit_order))
        to_write = [date, time, currency, deposit_w_symb, deposit_w_symb, "True"]
        writer.writerow(to_write)
        file.flush()


def place_order(auth_client, order, writer, file, deposit_option, deposit_amount):
    """Orders are passed in individually from DCA and create a market order"""

    coin = order[0]
    amount = order[1]
    buy_with = coin.split("-")[0]
    sell_with = coin.split("-")[1]
    buy_symb = str(CurrencySymbols.get_symbol(buy_with))
    sell_symb = str(CurrencySymbols.get_symbol(sell_with))

    if amount is not None and not 0:
        response = auth_client.place_market_order(product_id=coin, side="buy", funds=amount)  # Place market order
        if "message" in response and response["message"] == "Insufficient funds":
            if deposit_option is None or deposit_amount == 0:  # Auto-deposit off

                # Generate timestamp
                month = str(datetime.datetime.today().month)
                day = str(datetime.datetime.today().day)
                year = str(datetime.datetime.today().year)
                date = month + "/" + day + "/" + year
                time = str(datetime.datetime.now().isoformat().split("T")[1]) + "Z"

                # Write critical error message to log
                to_write = [date, time, coin, "X", "X", response["message"]]
                writer.writerow(to_write)
                file.flush()

                raise Exception("INSUFFICIENT FUNDS!")

            else:  # Auto-deposit on
                if validate_deposit_request(auth_client, deposit_option, deposit_amount,
                                            False):  # Validate deposit request
                    deposit_fiat(auth_client, deposit_option, deposit_amount, writer, file)
                    print("Waiting 60 seconds for deposit order response.")
                    sleep(SECONDS_PER_MINUTE)
                    sell_balance = balance(auth_client, sell_with)
                    num_hr_wait = 0
                    while sell_balance < amount:
                        print(f"Waiting for deposit to finish pending... Hour {num_hr_wait}.")
                        sleep(SECONDS_PER_HOUR)  # Wait 1 hr
                        response = auth_client.place_market_order(product_id=coin, side="buy",
                                                                  funds=amount)  # Place market order
                        if "message" in response and "message" == "Insufficient funds":
                            success = False
                            num_hr_wait += 1
                            continue
                        else:
                            transaction_id = response["id"]
                            success, order = check_transaction(transaction_id, auth_client)
                            if success:
                                if sell_symb is None: sell_symb = ""
                                print(f"Deposit of {sell_symb}{deposit_amount} successful! Hour {num_hr_wait + 1}\n")
                                break
                            num_hr_wait += 1
                    if success is not True:
                        response = auth_client.place_market_order(product_id=coin, side="buy",
                                                                  funds=amount)  # Place market order

        sleep(2)  # Wait 2 seconds
        transaction_id = response["id"]
        success, order = check_transaction(transaction_id, auth_client)

        if not success:
            attempts = 1
            while attempts < 9:
                sleep(2)  # Wait 2 seconds
                success, order = check_transaction(transaction_id, auth_client)
                if not success:
                    attempts += 1
                    print(f"Unsuccessful purchase of {coin}. Attempt #{attempts}")
                    continue
                if success:
                    purchase_amount = order["filled-size"]
                    print(order)
                    if buy_symb is None: buy_symb = ""
                    if sell_symb is None: sell_symb = ""
                    print(f"Successful purchase of {buy_symb}{purchase_amount} {coin} for {sell_symb}{amount} after "
                          f"{attempts + 1} attempts.\n")
                    date_time = str(order["done_at"]).split("T")
                    transaction_time = date_time[1]
                    transaction_date = date_time[0]
                    to_write = [transaction_date, transaction_time, coin, purchase_amount, amount, "True"]
                    writer.writerow(to_write)
                    return True
            if not success:
                print(f"ABSOLUTE FAILURE:\tUnsuccessful purchase of {coin}. Attempt #{attempts + 1}")
                date_time = str(order["done_at"]).split("T")
                transaction_time = date_time[1]
                transaction_date = date_time[0]
                to_write = [transaction_date, transaction_time, coin, "X", "X", "False"]
                writer.writerow(to_write)
                print("\n")
                return False
        else:
            print(order)
            purchase_amount = str(order["filled_size"])
            if buy_symb is None: buy_symb = ""
            if sell_symb is None: sell_symb = ""
            print(f"Successful purchase of {buy_symb}{purchase_amount} {coin} for {sell_symb}{amount}.\n")
            date_time = str(order["done_at"]).split("T")
            transaction_time = date_time[1]
            transaction_date = date_time[0]
            to_write = [transaction_date, transaction_time, coin, purchase_amount, amount, "True"]
            writer.writerow(to_write)
            return True


def DCA(public_client, auth_client, raw_orders, writer, file, deposit_option, deposit_amount):
    valid_orders = validate_order_request(public_client, raw_orders)
    for order in valid_orders:
        place_order(auth_client, order, writer, file, deposit_option, deposit_amount)
        file.flush()


def start_pressed(main_window, main_ui):
    main_window.hide()


def main():
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    main_ui = Ui_MainWindow()
    main_ui.setupUi(main_window)
    main_window.setFocus()  # Forces placeholder text to appear
    main_window.show()

    main_ui.edit_configuration_button.clicked.connect(main_ui.open_list_window)
    main_ui.start_button.clicked.connect(lambda: start_pressed(main_window, main_ui))



    sys.exit(app.exec_())  # Keeps the window on screen until it's closed

# -------------------------------------------------------------------------------------------------------------------
    # with open("config.json") as config_file:
    #     config = json.load(config_file)
    #
    # # Generate variables from configuration file
    # api_type, key, secret, passphrase, frequency, frequency_type, raw_orders, deposit_requested, \
    #     deposit_amount = config_reader(config)
    #
    # # Validate configuration file variables
    # validate_config(key, secret, frequency_type, frequency, api_type)
    #
    # requested_orders = list()
    # print("Order requests:\n---------------")
    # for request in raw_orders:
    #     trading_pair = request["trading-pair"].upper()
    #     amount = request["amount"]
    #     buy_with_symbol = CurrencySymbols.get_symbol(trading_pair.split("-")[1])
    #     print(trading_pair, (buy_with_symbol + str(amount)))
    #     order = tuple((trading_pair, amount))
    #     requested_orders.append(order)
    # print("---------------")
    #
    # log_file_name = "transaction_log.csv"
    # if isfile(log_file_name):  # Log file exists
    #     log_file = open(log_file_name, "a", newline="")
    #     writer = csv.writer(log_file)
    # else:  # Create the log file
    #     log_file = open(log_file_name, "x", newline="")
    #     headers = ["Date", "UTC Time", "Trading Pair", "Purchased", "Cost", "Successful"]
    #     writer = csv.writer(log_file)
    #     writer.writerow(headers)  # Write the column headers
    #     log_file.flush()
    #
    # if api_type == "sandbox":  # Sandbox/testing API
    #     auth_client = cbpro.AuthenticatedClient(key, secret, passphrase, SANDBOX_URL)
    # elif api_type == "production":  # Live-market API
    #     auth_client = cbpro.AuthenticatedClient(key, secret, passphrase)
    # else:  # Invalid API option
    #     raise ValueError(f"\nInvalid \"api-type\": {api_type}.\n\tAPI-Type must be \"sandbox\" or \"production\".")
    #
    # raw_accounts = auth_client.get_accounts()
    # accounts = generate_accounts(raw_accounts)
    #
    # deposit_option = None
    # if deposit_requested:
    #     deposit_option = generate_deposit_option(auth_client)
    # deposit_requested, deposit_amount = validate_deposit_config(deposit_option, deposit_requested, deposit_amount)
    # if deposit_option is None:
    #     deposit_requested = False
    #     deposit_amount = 0
    #
    # generic_types = {"seconds", "minutes", "hours", "days", "weeks"}  # Doesn't include specified "day"
    # if frequency_type in generic_types:
    #     req = getattr(schedule.every(frequency), frequency_type)
    #     req.do(DCA, public_client, auth_client, requested_orders, writer, log_file, deposit_option, deposit_amount)
    # elif frequency_type == "day":
    #     req = getattr(schedule.every(1), frequency)
    #     req.do(DCA, public_client, auth_client, requested_orders, writer, log_file, deposit_option, deposit_amount)
    #
    # while True:
    #     schedule.run_pending()


if __name__ == "__main__":
    main()
