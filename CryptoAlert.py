from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import smtplib
from email.message import EmailMessage
import time
import ui


def Send_Email_Alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "cryptoalert.alert@gmail.com"
    msg['from'] = user
    password = "zthljbqoddydbvxd"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()


# Dictionary containing the a list of SMS gateways based on the first 3 digits of the phone number
domains = {
    "Koodo": '@msg.telus.com',
    "Virgin": '@vmobile.ca',
    "Bell": '@txt.bell.ca',
    "Rogers": '@sms.rogers.com'
}


def Send_SMS_Alert(subject, body, to):
    address = str(to) + str(domains.get(ui.carrier))
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = address

    user = "cryptoalert.alert@gmail.com"
    msg['from'] = user
    password = "zthljbqoddydbvxd"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()


# Set the driver to start headless
options = Options()
options.headless = True

base_url = 'https://www.coindesk.com/price/'
driver = webdriver.Chrome(options=options)

hasStarted = False
value = 0

# HTML Selectors

selector = '#export-chart-element > div > section > div.coin-info-list.price-list > div:nth-child(1) > div.data-definition > div'
counter = 0

update_interval = 1  # seconds
start_time = time.time()


def Update():
    global start_time
    elapsed = time.time() - start_time

    # Update
    if elapsed >= update_interval:
        start_time = time.time()
        elapsed = time.time() - start_time
        CheckValue()


# Checks if value is higher or lower than specified  in the coin tracker(in the UI)
def CheckValue():
    # Loop list of coin tracker instances (from ui) and get higher or lower values with the 'Bitcoin' ID
    for coin_tracker in ui.coin_tracker_list:
        # For each tracker, grab actual value from the coin and compare
        Check(coin_tracker)


def Check(coin_tracker):
    current_simplified_val = int(GetCurrentValue(coin_tracker.id, simplified=True))

    priceIsHigher = current_simplified_val >= int(coin_tracker.high_value)
    priceIsLower = current_simplified_val <= int(coin_tracker.low_value)

    # Check if checkbox is checked and input box is not empty
    if coin_tracker.high_value_check.get() == 1 and len(coin_tracker.high_value) != 0:
        if priceIsHigher:
            TriggerAlerts(coin_tracker, is_higher=True)
            priceIsHigher = False
    if coin_tracker.low_value_check.get() == 1 and len(coin_tracker.low_value) != 0:  # If price is lower
        if priceIsLower:
            TriggerAlerts(coin_tracker, is_higher=False)
            priceIsLower = False


# Returns the current value of the coin by id
def GetCurrentValue(coin_id, simplified=False):
    global original_value

    driver.get(base_url + coin_id.lower())
    element = driver.find_element_by_css_selector(selector)
    value = element.text
    if simplified:
        value = value.translate(str.maketrans('', '', '$,.'))  # Removing extra characters
        value = value[:len(value) - 2]  # Removing extra decimals
        return value
    else:
        return value



wasSent = False


def TriggerAlerts(coin_tracker, is_higher=False):
    global wasSent

    if not wasSent:
        ui.email = 'pwiltus@gmail.com'
        if is_higher:
            price_to_track = "$" + coin_tracker.high_value
            message = "Price of " + str(coin_tracker.id) + " is currently ABOVE " + price_to_track
            if ui.phone_number_validated:
                Send_SMS_Alert("ALERT", message, ui.phone_number)
            if ui.email_validated:
                Send_Email_Alert("ALERT", message, ui.email)
            if ui.windows_alert_enabled:
                ui.TriggerWindowsAlert("ALERT", message, None, 1800)  # Duration 30min

        else:
            price_to_track = "$" + coin_tracker.low_value
            message = "Price of " + str(coin_tracker.id) + " is currently BELOW " + price_to_track
            if ui.phone_number_validated:
                Send_SMS_Alert("ALERT", message, ui.phone_number)
            if ui.email_validated:
                Send_Email_Alert("ALERT", message, ui.email)
            if ui.windows_alert_enabled:
                ui.TriggerWindowsAlert("ALERT", message, None, 1800)  # Duration 30min

        wasSent = True


# Initialize UI
ui.Initialize()

while True:
    ui.Update()

    # cryptoAlert_is_running refers to the backed functionality (this bool is linked to the start stop button)
    if ui.cryptoAlert_is_running:
        Update()
