# Some packages are imported in full or twice due to problems with py-to-exe in getting the modules
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import win10toast
from win10toast import ToastNotifier
import PySide2
from PySide2 import QtWidgets, QtGui
import re
# import six
# import appdirs
# import packaging.requirements


# Tray Icon Stuff
class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)
        # Create menu options
        open_app = menu.addAction("Open Crypto Alert")
        quit_app = menu.addAction("Quit")
        # Bind menu options
        open_app.triggered.connect(self.ShowWindow)
        quit_app.triggered.connect(self.QuitApp)

        menu.addSeparator()
        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            self.ShowWindow()

    def ShowWindow(self):
        root.deiconify()

    def QuitApp(self):
        root.destroy()


# Window settings
root = Tk()
root.title('Crypto Alert')
root.geometry('300x650')


def Minimize(x):
    tray_icon.show()
    # TODO Add icon image and better title, make it appear only once, use this as guide: https://doc.qt.io/qtforpython/PySide6/QtWidgets/QSystemTrayIcon.html
    tray_icon.showMessage("", "App is running on the background", icon=QtWidgets.QSystemTrayIcon.Warning, msecs=10000)


root.bind('<Unmap>', Minimize)  # Binding event when window is minimized

# Title
title = Label(root, text="Crypto Alert")
title.pack()

# SMS Notification stuff

phone_number = ''
phone_number_validated = False
carrier = ''
email = ''
email_validated = False

windows_alert_enabled = False

def email_is_valid(email_address):
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if (re.search(regex, email_address)):
        return True
    else:
        return False


def SaveInformation():
    global phone_number
    global phone_number_validated
    global carrier
    global email
    global email_validated

    SaveCoinTrackers()

    # TODO: Add SMS and E-mail verification

    # Verify if e-mail address input is valid
    if len(email_input.get()) != 0:
        if email_is_valid(email_input.get()):
            email = email_input.get()
            email_validated = True
            messagebox.showinfo(title="Success", message="Information saved")
        else:
            email_validated = False
            messagebox.showerror(title="Error", message="E-mail is invalid, try again")

    carrier = carrier_dropdown_var.get()

    # Verify if phone number input is valid
    if len(number_input.get()) == 10 and number_input.get().isdecimal():
        phone_number = str(number_input.get())
        phone_number_validated = True
        messagebox.showinfo(title="Success", message="Information saved")
    elif len(number_input.get()) == 0:
        phone_number_validated = False
        pass
    else:
        phone_number_validated = False
        messagebox.showerror(title='Error', message="Error, make sure the phone number consists of only 10 numbers")



def SaveCoinTrackers():
    # Make sure only numbers are saved
    for entry in entry_list:
        if len(entry.get()) != 0 and entry.get().isdecimal() is False:
            messagebox.showerror(title='Error', message="Error, please input only numbers on the value tracker")
            return


    # Update values on the class object
    entry_index = 0
    for x in range(len(coin_tracker_list)):

        if (len(entry_list[entry_index].get()) != 0):
            coin_tracker_list[x].high_value = entry_list[entry_index].get()
        if (len(entry_list[entry_index + 1].get()) != 0):
            coin_tracker_list[x].low_value = entry_list[entry_index + 1].get()

        entry_index += 2


# Creates and positions SMS related stuff on the window
def Initialize_SMS():
    global number_input
    global sms_var
    global done_button
    global carrier_dropdown_var
    global carrier_dropdown

    sms_var = IntVar()
    sms_checkbox = Checkbutton(root, text="Enable SMS alert", variable=sms_var, command=Enable_Disable_SMS)
    sms_checkbox.pack(side=TOP, anchor=W)

    # Create phone number input box
    phone_title = Label(root, text='Phone Number: (numbers only) ')
    phone_title.pack(side=TOP, anchor=W)
    number_input = Entry(root)
    number_input.pack(side=TOP, anchor=W)

    # Create dropdown for carrier selection
    label = Label(root, text="Select Carrier")
    label.pack(side=TOP, anchor=NW)
    carriers = ["Koodo", "Virgin", "Bell", "Rogers"]
    carrier_dropdown_var = StringVar()
    carrier_dropdown_var.set(carriers[0])  # Default
    carrier_dropdown = OptionMenu(root, carrier_dropdown_var, *carriers)
    carrier_dropdown.pack(side=TOP, anchor=NW)

    # Initialize everything as disabled
    number_input.config(state='disabled')
    carrier_dropdown.config(state='disabled')

def InitializeEmail():
    global email_input
    global email_var

    # Create Checkbox
    email_var = IntVar()
    email_checkbox = Checkbutton(root, text="Enable e-mail alert", variable=email_var, command=Enable_Disable_Email)
    email_checkbox.pack(side=TOP, anchor=W)

    # Create e-mail input box
    email_title = Label(root, text='Email:')
    email_title.pack(side=TOP, anchor=W)
    email_input = Entry(root)
    email_input.pack(side=TOP, anchor=W)
    email_input.config(state= 'disabled')

# Enable or disables SMS related values and functionality
def Enable_Disable_SMS():
    # Enabling and disabling input based on checkbox
    if sms_var.get():
        number_input.config(state='normal')
        carrier_dropdown.config(state='normal')
    elif not sms_var.get():
        number_input.config(state='disabled')
        carrier_dropdown.config(state='disabled')

# Updates SMS related values and functionality
def Enable_Disable_Email():
    if email_var.get():
        email_input.config(state='normal')
    elif not email_var.get():
        email_input.config(state='disabled')


# Windows notification stuff (only tested on Windows 10)
def InitializeWindowsAlert():
    global win_alert_var
    global win_alert_checkbox
    global toaster

    win_alert_var = IntVar()
    win_alert_checkbox = Checkbutton(root, text="Enable Windows alert", variable=win_alert_var,
                                     command=UpdateWindowsNotification)
    win_alert_checkbox.pack(side=TOP, anchor=W)
    toaster = ToastNotifier()


def UpdateWindowsNotification():
    global windows_alert_enabled

    if win_alert_var.get():
        windows_alert_enabled = True
        TriggerWindowsAlert("Crypto Alert", "Windows alert has been enabled", '', 5)
    else:
        windows_alert_enabled = False
        TriggerWindowsAlert("Crypto Alert", "Windows alert has been disabled",'', 5)


def TriggerWindowsAlert(msg_title, message, icon_path, duration):
    toaster.show_toast(msg_title, message, icon_path=icon_path, duration=duration, threaded=True)


# Coin selection stuff
def ChangeDropdownIcon(dropdown, image):
    dropdown.config(compound='right', image=image, width=100)
    dropdown.image = image


coin_choices = ['Bitcoin', 'Ethereum', 'Litecoin']
previous_dropdown_values = {}  # Backup of the previous dropdown valueus (i.e the value before we clicked to change the dropdown)


def CreateCoinDropdown(dropdown_title, coin_name, image):
    label = Label(root, text=dropdown_title)
    label.pack(side=TOP, anchor=W)
    dropdown_var = StringVar()
    dropdown_var.set(coin_name)  # Command provides a string argument (the var variable)
    dropdown = OptionMenu(root, dropdown_var, *coin_choices,
                          command=lambda x: UpdateCoinsDropdown(x, dropdown_var, dropdown))
    dropdown.pack(side=TOP, anchor=W)
    ChangeDropdownIcon(dropdown, image)

    # Return a key value pair
    entry = {dropdown: dropdown_var}
    backup_val = {dropdown: dropdown_var.get()}
    previous_dropdown_values.update(backup_val)

    return entry


# Start stop button and main loop bool
start_stop_button = None


def InitializeCoinsDropdown():
    # Dropdown Icons
    global btc_img
    global eth_img
    global ltc_img
    # Dropdowns dictionary (key = dropdown, value = var)
    global dropdowns

    global start_stop_button

    # Declare dropdown images
    btc_img = PhotoImage(file="BC_logo.gif") #.img\\BC_logo.gif
    eth_img = PhotoImage(file="ETH_logo.gif") #.img\\ETH_logo.gif
    ltc_img = PhotoImage(file="LTC_logo.gif") #.img\\LTC_logo.gif

    space = Label(root, text="")
    space.pack()

    # Create currency selection before dropdowns
    CreateCurrencySelector()

    # Create dropdowns
    dropdowns = {}
    dropdowns.update(CreateCoinDropdown("Coin 1", "Bitcoin", btc_img))
    CreateValueTracker('Bitcoin')
    dropdowns.update(CreateCoinDropdown("Coin 2", "Ethereum", eth_img))
    CreateValueTracker('Ethereum')

    # Create general Save Button
    save_button = Button(root, text='Save', command=SaveInformation)
    save_button.pack(side=TOP, anchor=W)

    space_2 = Label(root, text="")
    space_2.pack()

    start_stop_button_txt = StringVar()
    start_stop_button_txt.set('Start')
    stop_start_button = Button(root, textvariable=start_stop_button_txt,
                               command=lambda: StartProgram(start_stop_button_txt))
    stop_start_button.pack()


# 'text' parameter is for changing the button text every time we press it
def StartProgram(text):
    global cryptoAlert_is_running

    txt = text.get()
    if txt == 'Start':
        cryptoAlert_is_running = True
        messagebox.showinfo(title='Success', message='Crypto Alert has started...')
        text.set('Stop (running...)')
    elif txt == 'Stop (running...)':
        cryptoAlert_is_running = False
        messagebox.showwarning(title='Warning', message='Crypto Alert has been stopped...')
        text.set('Start')

    # Disable all other widgets while program is running
    if cryptoAlert_is_running:
        for w in root.winfo_children():
            if type(w) == tk.Button and w['text'] == 'Stop (running...)':
                pass
            else:
                w.config(state='disabled')
    else:
        for w in root.winfo_children():
           w.config(state='normal')


# var = var (passed as argument when OptionMenu was created), dropdown = object itself
# coin = like var.get(basically the string value from var (i.e var.get())) could not get rid of it
def UpdateCoinsDropdown(coin, var, dropdown):
    # Verify availability (avoid 2 dropdowns with the same coin)
    current_selected_coin = var.get()
    # Append the previous values to a list
    previous_coins = []
    for x in previous_dropdown_values:
        previous_coins.append(previous_dropdown_values.get(x))

    # If coin already selected somewhere, display error and set it back to what it was before
    if current_selected_coin in previous_coins:
        messagebox.showerror(title='Error', message="Error, coin already selected")
        var.set(previous_dropdown_values.get(dropdown))
        coin = var.get()

    # Update Image
    if coin == 'Bitcoin':
        ChangeDropdownIcon(dropdown, btc_img)
    elif coin == 'Ethereum':
        ChangeDropdownIcon(dropdown, eth_img)
    elif coin == 'Litecoin':
        ChangeDropdownIcon(dropdown, ltc_img)

    # Update current coin class ID (that corresponds to this dropdown)
    new_id = coin
    for x in coin_tracker_list:
        if x.id == previous_dropdown_values.get(dropdown):
            x.id = new_id

    # Update previous dropdown value dictionary with the new old value
    new_old_value = {dropdown: var.get()}
    previous_dropdown_values.update(new_old_value)


coin_tracker_list = []
entry_list = []  # Hold all entries

currencies = ['CAD', 'USD', 'BRL', 'EUR', 'GBP']
# For selecting the currency of preference
def CreateCurrencySelector():
    label = Label(root, text='Currency')
    label.pack(side=TOP, anchor=NW)

    dropdown_var = StringVar()
    dropdown_var.set(currencies[0])
    currency_dropdown = OptionMenu(root, dropdown_var, *currencies)
    currency_dropdown.pack(side=TOP, anchor=NW)

    space = Label(root, text='')
    space.pack(side=TOP, anchor=NW)



# Initialize one of these for every coin dropdown, ID is the dropdown name (coin name)
def CreateValueTracker(ID):
    # A value tracker consists of 2: checkbox, the label, and the input box
    # One for the higher than value, and the other for the lower than value
    global entry_list

    # Create entries (disabled by default)
    input_higher = Entry(root)
    input_higher.config(state='disabled')
    input_lower = Entry(root)
    input_lower.config(state='disabled')

    # Create checkboxes
    coin_tracker_higher_var = IntVar()
    coin_tracker_checkbox_higher = Checkbutton(root, text="Higher Than", variable=coin_tracker_higher_var,
                                               command=lambda: EnableDisableValueInputBox(input_higher,
                                                                                          coin_tracker_higher_var))
    coin_tracker_lower_var = IntVar()
    coin_tracker_checkbox_lower = Checkbutton(root, text="Lower Than", variable=coin_tracker_lower_var,
                                              command=lambda: EnableDisableValueInputBox(input_lower,
                                                                                         coin_tracker_lower_var))

    # Pack everything
    coin_tracker_checkbox_higher.pack(side=TOP, anchor=W)
    input_higher.pack(side=TOP, anchor=W)
    coin_tracker_checkbox_lower.pack(side=TOP, anchor=W)
    input_lower.pack(side=TOP, anchor=W)
    # Create coin_tracker class instance
    coin_tracker = CoinTracker(coin_tracker_higher_var, coin_tracker_lower_var, ID)
    coin_tracker_list.append(coin_tracker)

    # Add entries to list
    entry_list.append(input_higher)
    entry_list.append(input_lower)

    # Bound to the checkboxes up here


def EnableDisableValueInputBox(input_box, var):
    if var.get() == 1:
        input_box.config(state='normal')
    elif var.get() == 0:
        input_box.config(state='disabled')


# Coin tracker class contains the coin dropdown as well as the min and max values and its checkboxes
class CoinTracker:
    high_value = '0'
    low_value = '0'

    def __init__(self, high_value_check, low_value_check, id):  # ID is the dropdown name (coin name)
        self.low_value_check = low_value_check
        self.high_value_check = high_value_check
        self.id = id


# Wraps all the individual initialize methods (responsible for creating and positioning objs on the window)
def Initialize():
    InitializeWindowsAlert()
    InitializeEmail()
    Initialize_SMS()
    InitializeCoinsDropdown()


def Update():
    root.update()
    root.update_idletasks()


cryptoAlert_is_running = False

if __name__ == '__main__':
    # Main Program
    Initialize()
    # TODO change tray icon

    # Initialize tray icon stuff
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("BC_logo.gif"), w)

    # Main Loop
    while True:
        Update()
