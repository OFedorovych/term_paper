from tkinter import *
import tkinter as tk
import serial
import threading
import datetime
import time
from crcmod import *
import mysql.connector
from pandas import DataFrame
import pandas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

connection = mysql.connector.connect(
    host = "127.0.0.1",
    user = "alex",
    password = "123456",
    database = "term_paper"
)
print("Connection: ", connection)
cursor = connection.cursor()

select_movies_query = "select Address, CmdID, sensors.id AS SensorID from devices inner join sensors on devices.id=sensors.devid"

cursor.execute(select_movies_query)
result = cursor.fetchall()
sens_config = {}
for row in result:
    key = str(row[0]) + "*" + str(row[1])
    sens_config[key] = row[2]
#----------------------------------------------------------------------------------------

ser = serial.Serial("COM2", 9600, timeout = 1)
name = None
bd_date = None
data = None
Timer = None
buffer = bytearray(32)
cmdID = 2
slave = 233
CMD_LENGTH = 255
crc16_func = crcmod.predefined.mkCrcFun('crc-aug-ccitt')

def print_chart(sensor_id):
    if sensor_id == 1:
        sensor_name = "Distance"
        place_x = 185
        place_y = 10
    elif sensor_id == 2:
        sensor_name = "Dust"
        place_x = 830
        place_y = 10
    elif sensor_id == 3:
        sensor_name = "Humidity"
        place_x = 185
        place_y = 405
    elif sensor_id == 4:
        sensor_name = "Temperature"
        place_x = 830
        place_y = 405

    select_value_query = "select value, time from tvalues where sensorid = " + str(sensor_id)
    cursor.execute(select_value_query)
    result_values_times = cursor.fetchall()
    Times = []
    Values = []
    for i in result_values_times:
        Values.append(i[0])
        Times.append(i[1])
    data2 = {'Time': Times,
            'Value': Values }
    df2 = DataFrame(data2,columns=['Time','Value'])
    figure2 = plt.Figure(figsize=(6.3, 3.8), dpi=100)
    ax2 = figure2.add_subplot()
    line2 = FigureCanvasTkAgg(figure2, root)
    line2.get_tk_widget().place(x = place_x, y = place_y)
    df2 = df2[['Time','Value']].groupby('Time').sum()
    df2.plot(kind='line', legend=True,  ax=ax2 , color='r',marker='o', fontsize=10)
    ax2.set_title('Time Vs. ' + sensor_name)


def get_data():
    while True:
        ser.readinto(buffer)
        if (buffer[0] == 233 or buffer[0] == 234):
            address = buffer[0]
            print("")
            print("Got message from slave #", address)
            ser.readinto(buffer)
            func = buffer[0]
            print("     Function:", func)
            ser.readinto(buffer)
            response_len = buffer[0]
            print("     Data length:", response_len)
            data = ""
            print("     Data:", end = ' ')
            for i in range(response_len):
                ser.readinto(buffer)
                data += chr(buffer[0])
                print(chr(buffer[0]), end = '')
            print()
            calc_crc = crc16_func(data.encode())
            ser.readinto(buffer)
            got_crc = buffer[0] * 256
            ser.readinto(buffer)
            got_crc += buffer[0]
            print("     Got crc:", hex(got_crc))
            print("     Calc crc:", hex(calc_crc))
            print()
            if calc_crc == got_crc:
                key = str(address) + "*" + str(func)
                sensor_id = sens_config[key] 
                
                insert_value_query = "INSERT INTO TValues (SensorID, Value) VALUES (" + str(sensor_id) + ", " + data + ")"
                cursor.execute(insert_value_query)
                connection.commit()
                #-------------------------------------------------
                #перемальовування графіка
                print_chart(sensor_id)
                #-------------------------------------------------
                #вивід в поле
                if (address == 233 and func == 1):
                    T_distance.delete("1.0", "end")
                    T_distance.insert(tk.END, data)
                elif (address == 233 and func == 2):
                    T_dust.delete("1.0", "end")
                    T_dust.insert(tk. END, data)
                elif (address == 234 and func == 3):
                    T_humidity.delete("1.0", "end")
                    T_humidity.insert(tk. END, data)
                elif (address == 234 and func == 4):
                    T_temperature.delete("1.0", "end")
                    T_temperature.insert(tk. END, data)
            else:
                if (address == 233 and func == 1):
                    T_distance.delete("1.0", "end")
                    T_distance.insert(tk.END, "crc error")
                elif (address == 234 and func == 1):
                    T_dust.delete("1.0", "end")
                    T_dust.insert(tk.END, "crc error")
            buffer[0] = 0


def send_command():
    global cmdID
    global slave
    cmdID += 1
    if cmdID > 2:
        slave = 234
    if cmdID > 4:
        cmdID = 1
        slave = 233
    values = bytearray(5)
    values[0] = slave
    values[1] = cmdID
    values[2] = CMD_LENGTH
    go_crc = crc16_func(values[:3])
    values[3] = int(go_crc / 256)
    values[4] = int(go_crc % 256)
    
    print("Send message to slave#", values[0])
    print("     Command:", values[1])
    print("     CRC:", hex(values[3]), hex(values[4]))
    ser.write(values)
    Timer = threading.Timer(25, send_command)
    Timer.start()

send_command()

#----------------------------------------------------------------------------------------

root = tk.Tk()
root.geometry("185x190")
root.title("Курсова робота")

T_distance = Text(root, height = 2, width = 20)
T_distance.place(x = 10, y = 10)

T_dust = Text(root, height = 2, width = 20)
T_dust.place(x = 10, y = 55)

T_humidity = Text(root, height = 2, width = 20)
T_humidity.place(x = 10, y = 100)

T_temperature = Text(root, height = 2, width = 20)
T_temperature.place(x = 10, y = 145)

t = threading.Thread(target=get_data, daemon=True)
t.start()

print_chart(1)
print_chart(2)
print_chart(3)
print_chart(4)

root.mainloop()