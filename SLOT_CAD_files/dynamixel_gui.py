import sys
import time
import tkinter as tk
from tkinter import messagebox
from dynamixel_sdk import *  # Dynamixel SDK library

# Control table addresses for XL-430
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132

# Protocol version
PROTOCOL_VERSION = 2.0

# Default setting
DXL_IDS = {"FL": 5, "FR": 4, "BL": 2, "BR": 3}  # Servo IDs
BAUDRATE = 2000000
DEVICENAME = '/dev/ttyUSB0'  # Change this to match your setup

TORQUE_ENABLE = 1  # Enable torque
TORQUE_DISABLE = 0  # Disable torque

# Position limits (0 to 360 degrees mapped to 0 to 4095)
DXL_MIN_POSITION_VALUE = 0  # 0 degrees
DXL_MAX_POSITION_VALUE = 4095  # 360 degrees
ul = 250
ulr = 260+20 #upper limit for left turn
# Upper limit
ulc = 220
relc = 160
defc = 100
rel = 140
defo = 180# Relaxed position


def angle_to_position(angle):
    angle = max(10, min(350, angle))  # Restrict input to 10° - 350°
    return int((angle / 360.0) * 4095)

# Initialize PortHandler and PacketHandler
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if not portHandler.openPort():
    messagebox.showerror("Error", "Failed to open the port!")
    sys.exit()

if not portHandler.setBaudRate(BAUDRATE):
    messagebox.showerror("Error", "Failed to set the baudrate!")
    sys.exit()

# Enable torque for each Dynamixel
for dxl_id in DXL_IDS.values():
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

def move_servo(angle, dxl_id):
    goal_position = angle_to_position(angle)
    packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, goal_position)

def move_servos():
    angle = int(angle_slider.get())
    for dxl_id in DXL_IDS.values():
        move_servo(angle, dxl_id)
    root.after(2000, update_positions)

def forward_gait():
    """Implements the forward walking motion by controlling the servos."""

    # Step 1
    move_servo(rel+15, DXL_IDS["FL"])
    move_servo(ul, DXL_IDS["FR"])
    move_servo(ul, DXL_IDS["BL"])
    move_servo(ul, DXL_IDS["BR"])
    root.after(420)  # Delay 1 sec

    # Step 2
    move_servo(ul+15, DXL_IDS["FL"])
    move_servo(rel, DXL_IDS["FR"])
    move_servo(ul, DXL_IDS["BL"])
    move_servo(ul, DXL_IDS["BR"])
    root.after(420)  # Delay 1 sec

def update_positions():
    for leg, dxl_id in DXL_IDS.items():
        dxl_present_position, _, _ = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)
        dxl_present_position &= 0xFFFFFFFF  # Handle negative values
        position_labels[leg].config(text=f"{leg} Position: {dxl_present_position}")

def backward_gait():
    move_servo(ul, DXL_IDS["FL"])
    move_servo(ul, DXL_IDS["FR"])
    move_servo(rel, DXL_IDS["BL"])
    move_servo(ul, DXL_IDS["BR"])
    root.after(1000)
    move_servo(ul, DXL_IDS["FL"])
    move_servo(ul, DXL_IDS["FR"])
    move_servo(ul, DXL_IDS["BL"])
    move_servo(rel, DXL_IDS["BR"])
    root.after(1000)

def right_turn():
    move_servo(ul, DXL_IDS["FL"])
    move_servo(ul, DXL_IDS["FR"])
    move_servo(rel, DXL_IDS["BR"])
    move_servo(defo, DXL_IDS["BL"])
    root.after(200)
    move_servo(ul, DXL_IDS["FL"])
    move_servo(defo, DXL_IDS["FR"])
    move_servo(ul - 20, DXL_IDS["BR"])
    move_servo(rel, DXL_IDS["BL"])
    root.after(200)
    move_servo(ul, DXL_IDS["FL"])
    move_servo(rel, DXL_IDS["FR"])
    move_servo(defo, DXL_IDS["BR"])
    move_servo(ul, DXL_IDS["BL"])
    root.after(200)

def left_turn():
    move_servo(ulr, DXL_IDS["FR"])
    move_servo(ulr, DXL_IDS["FL"])
    move_servo(defo-rel, DXL_IDS["BL"])
    move_servo(defo, DXL_IDS["BR"])
    root.after(600)

    move_servo(defo, DXL_IDS["FR"])
    move_servo(ulr, DXL_IDS["FL"])
    move_servo(ulr, DXL_IDS["BL"])
    move_servo(defo-rel, DXL_IDS["BR"])
    root.after(600)

    move_servo(defo-rel, DXL_IDS["FR"])
    move_servo(ulr, DXL_IDS["FL"])
    move_servo(defo, DXL_IDS["BL"])
    move_servo(ulr, DXL_IDS["BR"])
    root.after(600)

def crawl_forward():
    move_servo(defc, DXL_IDS["FR"])
    move_servo(defc, DXL_IDS["BL"])
    move_servo(ulc, DXL_IDS["FL"])
    move_servo(defc - relc, DXL_IDS["BR"])
    root.after(1000)

    move_servo(ulc, DXL_IDS["BR"])
    move_servo(defc - relc, DXL_IDS["FL"])
    move_servo(defc, DXL_IDS["BL"])
    move_servo(defc, DXL_IDS["FR"])
    root.after(1000)

    move_servo(defc, DXL_IDS["BR"])
    move_servo(defc, DXL_IDS["FL"])
    move_servo(defc - relc, DXL_IDS["BL"])
    move_servo(ulc, DXL_IDS["FR"])
    root.after(1000)

    move_servo(defc - relc, DXL_IDS["FR"])
    move_servo(ulc, DXL_IDS["BL"])
    move_servo(defc, DXL_IDS["FL"])
    move_servo(defc, DXL_IDS["BR"])
    root.after(1000)

def close_app():


    for dxl_id in DXL_IDS.values():
        packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    portHandler.closePort()
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Dynamixel Servo Controller")
root.geometry("500x500")

angle_slider = tk.Scale(root, from_=0, to=360, orient=tk.HORIZONTAL, label="Angle (10-351)")
angle_slider.pack(pady=10)

move_button = tk.Button(root, text="Move Servos", command=move_servos)
move_button.pack(pady=5)

position_labels = {}
for leg in DXL_IDS.keys():
    lbl = tk.Label(root, text=f"{leg} Position: -")
    lbl.pack()
    position_labels[leg] = lbl

forward_button = tk.Button(root, text="Forward", command=forward_gait)
forward_button.pack(pady=5)

backward_button = tk.Button(root, text="Backward", command=backward_gait)
backward_button.pack(pady=5)

left_button = tk.Button(root, text="Left Turn", command=left_turn)
left_button.pack(pady=5)

right_button = tk.Button(root, text="Right Turn", command=right_turn)
right_button.pack(pady=5)

c_button = tk.Button(root, text="crawl", command=crawl_forward)
right_button.pack(pady=5)

exit_button = tk.Button(root, text="Exit", command=close_app)
exit_button.pack(pady=10)

root.mainloop()