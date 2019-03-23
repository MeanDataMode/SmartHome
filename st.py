import math
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
from DB_common_smarthome import build_devices_db, get_device_event_dates
from private import Password, Username, URL


def time_me(*arg):
    if len(arg) != 0:
        elapsed_time = time.time() - arg[0]
        hours = math.floor(elapsed_time / (60*60))
        elapsed_time = elapsed_time - hours * 60*60
        minutes = math.floor(elapsed_time / 60)
        elapsed_time = elapsed_time - minutes * 60
        seconds = math.floor(elapsed_time)
        if hours != 0:
            return "%d hours %d minutes %d seconds" % (hours, minutes, seconds)
        elif minutes != 0:
            return "%d hours %d minutes %d seconds" % (hours, minutes, seconds)
        else:
            return "%d hours %d minutes %d seconds" % (hours, minutes, seconds)
    else:
        return time.time()


def wait():
    secs = random.randrange(4, 7)
    ms = random.random()
    wait_time = secs + ms
    time.sleep(wait_time)


def date_string(last_activity):
    if last_activity is "":
        return ''
    else:
        activity = last_activity.split(" ")
        if activity[1] == 'hours':
            h = int(activity[0])
            ago = (datetime.datetime.now() - datetime.timedelta(hours=h))
        elif activity[1] == 'hour':
            ago = (datetime.datetime.now() - datetime.timedelta(hours=1))
        elif activity[1] == 'minutes':
            m = int(activity[0])
            ago = (datetime.datetime.now() - datetime.timedelta(minutes=m))
        elif activity[1] == 'minute':
            ago = (datetime.datetime.now() - datetime.timedelta(minutes=1))
        elif activity[1] == 'seconds':
            s = int(activity[0])
            ago = (datetime.datetime.now() - datetime.timedelta(minutes=s))
        elif activity[1] == 'second':
            ago = (datetime.datetime.now() - datetime.timedelta(seconds=1))
        else:
            ago = ''
        return ago


def st_login(run_silent=False):
    st_username = Username().st()
    st_pass = Password().st()

    if run_silent is False:
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir=selenium")
        driver = webdriver.Chrome(executable_path=r"chromedriver_win32\chromedriver.exe",
                                  options=chrome_options)
    else:
        print("*** Running Silent Browser ***")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-data-dir=selenium")
        driver = webdriver.Chrome(executable_path=r"chromedriver_win32\chromedriver.exe",
                                  options=chrome_options)

    driver.get(URL().st_login())
    wait()
    landing_url = driver.current_url
    if landing_url != URL().st_landing():
        # All ready Logged In, Need to Log out
        driver.find_element_by_class_name('st-arrow-dropdown').click()
        wait()
        driver.find_element_by_link_text('Logout').click()
        wait()
        time.sleep(10)
        driver.get(URL().st_login())
        wait()
        # Click the 'Sign in
        sam_account = '//button[contains(@class, "sa-login-btn button pure-input-1")]'
        driver.find_element_by_xpath(sam_account).click()
        # time.sleep(3)
        wait()
    else:
        # Click the 'Sign
        sam_account = '//button[contains(@class, "sa-login-btn button pure-input-1")]'
        driver.find_element_by_xpath(sam_account).click()
        # time.sleep(3)
        wait()

        # Find input fields
        username = driver.find_element_by_id("iptLgnPlnID")
        password = driver.find_element_by_id("iptLgnPlnPD")
        wait()

        # Enter text into username
        username.clear()
        wait()
        username.send_keys(st_username)
        wait()

        # Enter Password
        password.clear()
        wait()
        password.send_keys(st_pass)
        wait()

        # Click Sign In
        driver.find_element_by_id("signInButton").click()
        time.sleep(10)
        wait()
    return driver


def get_devices(driver):
    html = driver.page_source
    page_soup = BeautifulSoup(html, "html.parser")
    rows = page_soup.findAll("tr", {"class": ("device-row odd", "device-row even")})
    device_dict = dict()
    for row in rows:
        columns = row.findAll("td")

        # Get Display Name and Link
        key = columns[0].text
        device_dict[key] = dict()
        line = str(columns[0].find("a"))
        device_url_ext = line.split('"')[1]
        device_id = device_url_ext.split('/')[3]
        root_url = URL().st_root()
        url = "{}{}".format(root_url, device_url_ext)
        device_dict[key]['Name'] = key
        device_dict[key]['ID'] = device_id
        device_dict[key]['URL'] = url

        # Get Other Columns
        device_dict[key]['Type'] = columns[1].text
        device_dict[key]['Location'] = columns[2].text
        device_dict[key]['Hub'] = columns[3].text
        device_dict[key]['ZigbeeID'] = columns[4].text
        device_dict[key]['DeviceNetworkID'] = columns[5].text
        device_dict[key]['Status'] = columns[6].text
        device_dict[key]['ExecutionLocation'] = columns[7].text
        device_dict[key]['LastActivity'] = date_string(columns[8].text)
    return driver, device_dict


def get_device_specific_info(driver):
    hold_dict = dict()
    hold_dict['Name'] = ""
    hold_dict['Label'] = ""
    hold_dict['Type'] = ""
    hold_dict['Version'] = ""
    hold_dict['DeviceNetworkID'] = ""
    hold_dict['Status'] = ""
    hold_dict['Hub'] = ""
    hold_dict['Group'] = ""
    hold_dict['ZigbeeID'] = ""
    hold_dict['LastActivityAt'] = ""
    hold_dict['DateCreated'] = ""
    hold_dict['LastUpdated'] = ""
    hold_dict['Data'] = ""
    hold_dict['RawDescription'] = ""
    hold_dict['Firmware'] = ""
    hold_dict['CurrentStates'] = ""
    hold_dict['Preferences'] = ""
    hold_dict['ExecutionLocation'] = ""
    hold_dict['Events'] = ""
    hold_dict['InUseBy'] = ""

    time.sleep(3)
    html = driver.page_source
    page_soup = BeautifulSoup(html, "html.parser")
    rows = page_soup.findAll("tr", {"class": "fieldcontain"})

    count = 0
    while count <= 30:
        for idx, row in enumerate(rows):
            if " ".join(row.text.split()[0:1]) == 'Name':
                hold_dict['Name'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Label':
                hold_dict['Label'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Type':
                hold_dict['Type'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Version':
                hold_dict['Version'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:2]) == 'Device Network':
                hold_dict['DeviceNetworkID'] = " ".join(row.text.split()[3:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Status':
                hold_dict['Status'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Hub':
                hold_dict['Hub'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Group':
                hold_dict['Group'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:2]) == 'Zigbee ID':
                hold_dict['ZigbeeID'] = " ".join(row.text.split()[2:])
                count += 1

            elif " ".join(row.text.split()[0:3]) == 'Last Activity At':
                last_activity = datetime.datetime.strptime(" ".join(
                    row.text.split()[3:6]), "%Y-%m-%d %I:%M %p")
                hold_dict['LastActivityAt'] = last_activity
                count += 1

            elif " ".join(row.text.split()[0:2]) == 'Date Created':
                create = datetime.datetime.strptime(" ".join(
                    row.text.split()[2:5]), "%Y-%m-%d %I:%M %p")
                hold_dict['DateCreated'] = create
                count += 1

            elif " ".join(row.text.split()[0:2]) == 'Last Updated':
                lst_update = datetime.datetime.strptime(" ".join(
                    row.text.split()[2:5]), "%Y-%m-%d %I:%M %p")
                hold_dict['LastUpdated'] = lst_update
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Data':
                data_1 = " ".join(row.text.split()[1:])
                data_1 = data_1.strip().split()
                di = 0
                do = 1
                hold_dict['Data'] = dict()
                for i in range(0, (int(len(data_1) / 2))):
                    hold_dict['Data'][data_1[di]] = data_1[do]
                    di += 2
                    do += 2
                count += 1

            elif " ".join(row.text.split()[0:2]) == 'Raw Description':
                hold_dict['RawDescription'] = " ".join(row.text.split()[2:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Firmware':
                hold_dict['Firmware'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:2]) == 'Current States':
                status = " ".join(row.text.split()[2:])
                status = status.strip().split()
                di = 0
                do = 1
                hold_dict['CurrentStates'] = dict()
                for i in range(0, (int(len(status) / 2))):
                    hold_dict['CurrentStates'][status[di]] = status[do]
                    di += 2
                    do += 2
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Preferences':
                hold_dict['Preferences'] = " ".join(row.text.split()[2:])

            elif " ".join(row.text.split()[0:2]) == 'Execution Location':
                hold_dict['ExecutionLocation'] = " ".join(row.text.split()[2:])
                count += 1

            elif " ".join(row.text.split()[0:1]) == 'Events':
                hold_dict['Events'] = " ".join(row.text.split()[1:])
                count += 1

            elif " ".join(row.text.split()[0:3]) == 'In Use By':
                hold_dict['InUseBy'] = " ".join(row.text.split())
                count += 1
    return driver, hold_dict


def get_all_events_from_page(driver):
    # Click the Display 'all'
    driver.find_element_by_id('allLink').click()
    wait()

    # Click on #200 (display at once)
    driver.find_element_by_xpath('//option[@value="200"]').click()
    wait()

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Scroll to bottom
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(3)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    try:
        driver.find_element_by_class_name('events-table').click()
        wait()

        html = driver.page_source
        page_soup = BeautifulSoup(html, "html.parser")
        wait()
        table = page_soup.find("tbody", {"class": "events-table"})
        rows = table.findAll("tr")
        event_dict = dict()
        line = 0
        for row in rows:
            event_dict[line] = dict()
            column = row.findAll("td")

            # Date
            e_date = column[0].text.strip().split("\n")[0]
            e_date = " ".join(e_date.split(" ")[0:3])
            e_date = datetime.datetime.strptime(e_date, "%Y-%m-%d %I:%M:%S.%f %p")
            event_dict[line]['Date'] = e_date

            # Source
            event_dict[line]['Source'] = " ".join(column[1].text.strip().split("\n"))

            # Type
            event_dict[line]['Type'] = " ".join(column[2].text.strip().split("\n"))

            # Name
            event_dict[line]['Name'] = " ".join(column[3].text.strip().split("\n"))

            # Value
            event_dict[line]['Value'] = " ".join(column[4].text.strip().split("\n"))

            # User
            event_dict[line]['User'] = " ".join(column[5].text.strip().split("\n"))

            # Displayed Text
            event_dict[line]['Displayed_Text'] = " ".join(column[6].text.strip().split("\n"))

            # Changed
            event_dict[line]['Changed'] = " ".join(column[7].text.strip().split("\n"))

            line += 1
    except Exception:
        event_dict = dict()
    return driver, event_dict


def get_all_st_data():
    start = time_me()
    main_data_dict = dict()
    driver = st_login()
    wait()
    device_return = get_devices(driver)
    driver = device_return[0]
    devices = device_return[1]

    count = 0
    for key, value in devices.items():
        if count <= 1000:
            t_device = time_me()
            count += 1
            device_url = devices[key]['URL']
            wait()

            # Go to Device:
            driver.get(device_url)
            wait()

            device_return = get_device_specific_info(driver)
            wait()
            driver = device_return[0]
            device_info = device_return[1]
            wait()

            # Go To Data
            events_url = (URL().st_events() +
                          "device/{IDS}/events".format(IDS=devices[key]['ID']))
            driver.get(events_url)
            wait()

            data_return = get_all_events_from_page(driver)
            driver = data_return[0]
            device_data = data_return[1]

            if len(device_data) is 0:
                print("{} \t\t*** Nothing to Send to 'devices' DB ***\t- {}".format(time_me(t_device),
                                                                                    devices[key]['Name']))
                pass
            else:
                # Send device_info to device_info_DB
                try:
                    last_event_time = get_device_event_dates(device_id=devices[key]['ID'])
                except:
                    last_event_time = datetime.datetime(2018, 3, 20, 21, 46, 58, 14034)
                build_devices_db(devices_dict=devices[key],
                                 device_info_dict=device_info,
                                 device_data_dict=device_data,
                                 last_event=last_event_time)
                main_data_dict[devices[key]['Name']] = device_data
                print("{} \t\t*** Sent New Content to 'devices' DB ***\t- {}".format(time_me(t_device),
                                                                                     devices[key]['Name']))
    print("Completed in {}".format(time_me(start)))

    # Logout
    driver.find_element_by_class_name('st-arrow-dropdown').click()
    wait()
    time.sleep(5)
    driver.find_element_by_link_text('Logout').click()
    time.sleep(10)
    wait()
    driver.close()
    return main_data_dict


get_all_st_data()
