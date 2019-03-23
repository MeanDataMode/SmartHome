import sqlite3
from shutil import copyfile
import datetime
from private_smarthome import (File)

wd = File('home', 'private').wd()
db_name = File('home', 'private').db_name()


def backup_db():
    # Move File from Download Folder and Save
    master_file = "{}{}".format(wd, db_name)
    file = db_name.split(".")[0]
    date = datetime.datetime.now().strftime("%Y-%m-%d %H%M")
    backup_file = "{wd}backup/{file}{date}.db".format(wd=wd,
                                                      file=file,
                                                      date=date)
    # Copy File from
    copyfile(master_file, backup_file)


def init_devices_db(cur):
    # Purpose:
    #   Builds the Database table called 'devices'
    #   will store the posting information in this table
    cur.execute('''CREATE TABLE IF NOT EXISTS devices(
    Current_Time TIMESTAMP, 
    Device_Name TEXT, 
    Device_Label TEXT, 
    Device_ID TEXT, 
    Device_Type TEXT, 
    Device_Version TEXT, 
    Device_DeviceNetworkID TEXT, 
    Device_Status TEXT, 
    Device_Location TEXT, 
    Device_Hub TEXT, 
    Device_Group TEXT, 
    Device_ZigbeeID TEXT, 
    Device_LastActivityAt TIMESTAMP, 
    Device_DateCreated TIMESTAMP, 
    Device_LastUpdated TIMESTAMP, 
    Device_RawDescription TEXT, 
    Device_Firmware TEXT, 
    Device_Preferences, 
    Device_ExecutionLocation TEXT, 
    Device_InUseBy TEXT, 
    Event_Date TIMESTAMP, 
    Event_Source TEXT, 
    Event_Type TEXT, 
    Event_Name TEXT, 
    Event_Value TEXT, 
    Event_User TEXT, 
    Event_Displayed_Text TEXT, 
    Event_Changed TEXT)''')


def populate_devices_db(db, line):
    # Purpose:
    #   populates 'devices' database table with line
    # Variables:
    #   db = the database
    #   line = what to write to the database.
    cur = db.cursor()
    cur.execute('''
    INSERT INTO devices (    
    Current_Time, Device_Name, Device_Label, Device_ID, 
    Device_Type, Device_Version, Device_DeviceNetworkID, Device_Status, 
    Device_Location, Device_Hub, Device_Group, Device_ZigbeeID, 
    Device_LastActivityAt, Device_DateCreated, Device_LastUpdated, Device_RawDescription, 
    Device_Firmware, Device_Preferences, Device_ExecutionLocation, Device_InUseBy, 
    Event_Date, Event_Source, Event_Type, Event_Name, 
    Event_Value, Event_User, Event_Displayed_Text, Event_Changed
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?)''', line)
    db.commit()


def build_devices_db(devices_dict, device_info_dict, device_data_dict, last_event):
    # db = sqlite3.connect(':memory:')
    db = sqlite3.connect("{}{}".format(wd, db_name))
    cur = db.cursor()
    t_now = datetime.datetime.now()

    # Is the function that starts the DB, and creates the "devices" table.
    init_devices_db(cur)
    for k1, data_dict in device_data_dict.items():
        if data_dict['Date'] > last_event:
            line = (t_now,
                    device_info_dict['Name'],
                    device_info_dict['Label'],
                    devices_dict['ID'],
                    device_info_dict['Type'],
                    device_info_dict['Version'],
                    device_info_dict['DeviceNetworkID'],
                    device_info_dict['Status'],
                    devices_dict['Location'],
                    devices_dict['Hub'],
                    device_info_dict['Group'],
                    devices_dict['ZigbeeID'],
                    devices_dict['LastActivity'],
                    device_info_dict['DateCreated'],
                    device_info_dict['LastUpdated'],
                    device_info_dict['RawDescription'],
                    device_info_dict['Firmware'],
                    device_info_dict['Preferences'],
                    device_info_dict['ExecutionLocation'],
                    device_info_dict['InUseBy'],
                    data_dict['Date'],
                    data_dict['Source'],
                    data_dict['Type'],
                    data_dict['Name'],
                    data_dict['Value'],
                    data_dict['User'],
                    data_dict['Displayed_Text'],
                    data_dict['Changed'])
            # print(line)
            populate_devices_db(db, line)
    db.close()
    # print("\t\t\t*** Data Sent to 'devices' DB ***")


def get_device_event_dates(device_id, the_wd=wd, the_db_name=db_name):
    db = sqlite3.connect("{}{}".format(the_wd, the_db_name))
    cur = db.cursor()
    cur.fetchall()
    output = cur.execute("""SELECT MAX(Event_Date) AS Event_Date 
    FROM devices
    WHERE Device_ID is "{device_id}"
    """.format(device_id=device_id))
    for idx, line in enumerate(output):
        if line[0] is None:
            last_recorded_event_time = datetime.datetime(2018, 3, 20, 21, 46, 58, 14034)
        else:
            last_recorded_event_time = datetime.datetime.strptime(line[0], ("%Y-%m-%d %H:%M:%S.%f"))
    db.close()
    return last_recorded_event_time
