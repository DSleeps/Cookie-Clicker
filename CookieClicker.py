from selenium import webdriver
import time
import json
from selenium.common.exceptions import StaleElementReferenceException
import pyautogui
import math as m
import re

#Number of different products in the store
product_num = 16

#How much you zoom out
zoom_amount = 6

#Amount of time we pause between clicks
pause_time = 0.05

#The desired upgrade information
desired_upgrade_id = 75
desired_upgrade_cost = 50000
upgrade_bought = False

interest = 0

#The variable for graphing
global_cps = 0

#The queue for the items to buy
queue = []

#The start time
start_time = time.time()

#Goes to a url in the main window
browser = webdriver.Chrome('Driver/chromedriver')
browser.get("http://orteil.dashnet.org/cookieclicker/")

time.sleep(5)

#Convert the cookie clicker numbers into actual numbers
def convert_string(text):
    t_arr = text.split(' ')
    if (len(t_arr) == 1):
        return float(text.replace(",", ""))
    else:
        if (t_arr[1] == 'million'):
            return float(t_arr[0]) * 1000000
        elif(t_arr[1] == 'billion'):
            return float(t_arr[0]) * 1000000000
        elif (t_arr[1] == 'trillion'):
            return float(t_arr[0]) * 1000000000000
        elif (t_arr[1] == 'quadrillion'):
            return float(t_arr[0]) * 1000000000000000

#Zooms out on the page
def zoom_out():
    #Start by zooming out so we can see all of the upgrades
    pyautogui.keyDown('command')
    for i in range(zoom_amount):
        time.sleep(0.25)
        pyautogui.press('-')

#Checks and returns all of the products we can currently afford
def check_products_available():
    #This gets all of the products
    products_price = []
    for i in range(product_num):
        product = browser.find_element_by_id('product' + str(i))

    #These are the products that are available
    affordable = []
    for p in product_elements:
        cl = p.get_attribute('class')
        if (cl == 'product unlocked enabled'):
            affordable.append(p)

    return affordable

#Get the prices of all of the currently unlockable elements
def get_prices():
    #This gets all of the products
    product_elements = []
    for i in range(product_num):
        product = browser.find_element_by_id('product' + str(i))

        price_elem = browser.find_element_by_id('productPrice' + str(i))
        #If the price is blank the item can't be bought yet
        if (price_elem.text != ''):
            price = convert_string(price_elem.text)
            product_elements.append( (product, price) )

    return product_elements

#Get the price of a single element
def get_price(item):
    id = extract_number(item.get_attribute('id'))
    price_elem = browser.find_element_by_id('productPrice' + str(id))
    return convert_string(price_elem.text)

#Gets how many cookies we currently have and how many cookies we are generating per second
def get_current_cookie_data():
    cookie_count_elem = browser.find_element_by_id('cookies')
    cookie_str = cookie_count_elem.text
    cookie_arr = re.split(" |\n", cookie_str)

    print(cookie_arr)
    #The first element is the amount of cookies and the last is the cookie per second

    cookie_count = 0
    cps = 0
    num_texts = ['million', 'billion', 'trillion', 'quadrillion']
    if (cookie_arr[1] in num_texts): cookie_count = convert_string(" ".join(cookie_arr[0:2]))
    else: cookie_count = convert_string(cookie_arr[0])

    if (cookie_arr[-1] in num_texts): cps = convert_string(" ".join(cookie_arr[-2:]))
    else: cps = convert_string(cookie_arr[-1])

    print(cookie_count)
    print(cps)
    return (cookie_count, cps)

#Gets the big cookie element
def get_cookie():
    return browser.find_element_by_id("bigCookie")

#Moves the mouse to the center of the specified element
def move_mouse_to_element(elem):
    #Get the width and everything of the browser
    a = browser.execute_script("return outerWidth")
    b = browser.execute_script("return outerHeight")
    c = browser.execute_script("return outerHeight - innerHeight")

    x = elem.location_once_scrolled_into_view['x'] + int(elem.rect['width']/2.0)
    y = elem.location_once_scrolled_into_view['y'] + int(elem.rect['height']/2.0)

    pyautogui.moveTo(x*1440/a, (y + c)*900/b, 0.1)

#Buys whatever product is passed into here a certain number of times
def buy_product(product_elem, times=1):

    #If the product elem is just a number it means that it's an upgrade id
    if (type(product_elem) == type(1)):
        buy_upgrade(product_elem)
        return None

    #This just moves the mouse to the right part of the screen to scroll properly
    x = product_elem.location['x'] + int(product_elem.rect['width']/2.0)
    y = 300

    #Get the width and everything of the browser
    a = browser.execute_script("return outerWidth")
    b = browser.execute_script("return outerHeight")
    c = browser.execute_script("return outerHeight - innerHeight")

    pyautogui.moveTo(x*1440/a, (y + c)*900/b, 0.1)

    price = get_price(item)
    c, cps = get_current_cookie_data()
    if (price <= c):
        move_mouse_to_element(product_elem)
        for i in range(times):
            pyautogui.click()

        queue.pop(0)
    else:
        print('Cannot afford :(')
        print('Actual Price: ' + str(price))
        print('Current Cookies: ' + str(c))

def extract_number(text):
    nums = '0123456789'
    new_str = ''
    for l in text:
        if (l in nums): new_str += l
    return new_str

def buy_upgrade(upgrade_id):
    global interest
    global upgrade_bought

    #This means you don't have enough money yet
    if (get_current_cookie_data()[0] < desired_upgrade_cost):
        return None

    print('Buying upgrade')
    for i in range(400):
        upgrade = None
        try:
            upgrade = browser.find_element_by_id("upgrade" + str(i))
        except:
            #This means this many upgrades are not available yet
            print('Could not find ' + str(i))
            break

        #If it got here it means the upgrades are available
        on_click = upgrade.get_attribute("onclick")
        id = extract_number(on_click)

        #If the ids match this is the right upgrade
        if (float(id) == float(upgrade_id) and get_current_cookie_data()[0] >= desired_upgrade_cost):
            #Move the mouse to the first upgrade so all of them pop up then move it to the right one
            move_mouse_to_element(browser.find_element_by_id("upgrade0"))
            time.sleep(0.5)
            move_mouse_to_element(upgrade)
            pyautogui.click()

            #Make sure you update the upgrade bought variable
            upgrade_bought = True
            interest = interest + 0.01
            break


#This returns the next item to buy and the number of clicks needed to buy the item
current_item = 0
def get_item_and_click_count(method):
    global global_cps

    lps = 1/pause_time  #Clicks per second
    c, cps = get_current_cookie_data()  #Total cookies and cookies per second
    l = 1 + cps*interest      #Cookies per click
    tps = cps + l*lps   #Total cookies per second

    global_cps = cps

    current_items = get_prices()        #Gets the prices of all of the current items
    pps = [0.1, 1, 8, 47, 260, 1400,        #The amount of cookies each generates per second
            7800, 44000, 260000, 1600000,
            10000000, 65000000, 430000000,
            2900000000, 21000000000, 150000000000]

    #Method 1: Buy which one is most effient by ratio of cps over price
    if (method == 1):
        #Calculate how "efficient" each item is
        eff = []
        for i in range(len(current_items)):
            eff.append((pps[i]/current_items[i][1], i))
    elif (method == 2):
        #Method 2: Optimize how quickly your cps will increase
        eff = []
        #If there are no items queued up run the efficiency thing
        if (len(queue) == 0):
            for j in range(len(current_items)):
                p_j = current_items[j][1]
                for i in range(j,len(current_items)):
                    p_i = current_items[i][1]
                    tps_new = (cps + pps[j]) + (1 + interest*(cps + pps[j]))*lps
                    eff.append( [( (pps[i] + pps[j]) / ((p_j/tps) + (p_i/(tps_new+pps[j]))) ), j, i] )
        else:
            eff.append([ current_items[queue[0]][1], queue[0] ])
    elif (method == 3):
        #Method 3: Optimize how quickly the amount of cookies you have increases over some time interval

        #This is some function that determines the time interval to evaluate this over
        a = 1
        T = lambda x: x*a
        dt = (time.time() - start_time)

        eff = []
        for i in range(len(current_items)):
            #Price of the current item
            p_i = current_items[i][1]
            eff.append([(T(dt) - (p_i - c)/(tps))*pps[i] - p_i, i])

    def first(a):
        return a[0]

    #Sort to find the most efficient one
    eff.sort(key=first)

    #Add the new things to the queue
    if (len(queue) == 0): queue.extend(eff[-1][1:])
    m_i = eff[-1][1]
    most_efficient = current_items[m_i]

    #The price of the item you will buy
    price = current_items[m_i][1]

    #If the price is greater than the cost of the desired upgrade just buy the upgrade
    item = None
    c_price = 0
    if (price > desired_upgrade_cost and upgrade_bought == False):
        c_price = desired_upgrade_cost
        item = desired_upgrade_id
    else:
        #Otherwise just return the clicks to buy the element
        c_price = price
        item = most_efficient[0]

    #Calculate the number of clicks
    number_of_clicks = ((c_price - c)*lps) / (cps + l*lps)

    print(queue)

    print_numbers(int(number_of_clicks), queue[0])

    return (item, number_of_clicks)

def print_numbers(a, b):
    elem1 = browser.find_element_by_id('prefsButton')
    elem2 = browser.find_element_by_id('logButton')
    elem3 = browser.find_element_by_id('statsButton')

    browser.execute_script('arguments[0].innerHTML = "' + str(a) + '";', elem1)
    browser.execute_script('arguments[0].innerHTML = "' + str(b) + '";', elem2)
    browser.execute_script('arguments[0].innerHTML = "' + str(get_current_cookie_data()[0]) + '";', elem3)

#This gets the big cookie
c = get_cookie()
move_mouse_to_element(c)

#This sets the time between clicks
pyautogui.PAUSE = pause_time

past_time = time.time()
start_time = time.time()
data = []

method = 3

one_hour = 60 * 60
while time.time() < start_time + one_hour:
    #Get the best item to buy and buy it
    result = get_item_and_click_count(3)

    #The first element is the item to buy and the second is the number of clicks
    item = result[0]
    click_num = result[1]

    move_mouse_to_element(c)
    for i in range(int(click_num)+1):
        pyautogui.click()
        if (past_time + 10 < time.time()):
            data.append(global_cps)
            past_time = past_time + 10
        #time.sleep(pause_time)

    time.sleep(0.5)
    buy_product(item)

#Save the results
with open('Methodo' + str(method) + '.json', 'w') as outfile:
    json.dump(data, outfile)

browser.quit()
