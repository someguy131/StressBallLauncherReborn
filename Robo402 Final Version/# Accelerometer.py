# GY-521 / MPU6050 accelerometer 

import time
import smbus

# ---------------- I2C / MPU6050 Registers ----------------
MPU_ADDR = 0x68

PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

# For default ±2g accelerometer range
ACCEL_SCALE_MODIFIER = 16384.0

# Globals
bus = None
accel_x = 0.0
accel_y = 0.0
accel_z = 0.0


# ---------------- Setup ----------------
def accelerometerSetup(bus_num=1):
    global bus
    bus = smbus.SMBus(bus_num)

    # Wake up MPU6050 (it starts in sleep mode)
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

    time.sleep(0.1)
    print("Accelerometer initialized")


# ---------------- Helpers ----------------
def read_raw_data(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)

    value = (high << 8) | low

    if value > 32767:
        value -= 65536

    return value


# ---------------- Main Update ----------------
def updateAccelerometer():
    global accel_x, accel_y, accel_z

    try:
        raw_x = read_raw_data(ACCEL_XOUT_H)
        raw_y = read_raw_data(ACCEL_YOUT_H)
        raw_z = read_raw_data(ACCEL_ZOUT_H)

        # Convert raw values to g
        accel_x = raw_x / ACCEL_SCALE_MODIFIER
        accel_y = raw_y / ACCEL_SCALE_MODIFIER
        accel_z = raw_z / ACCEL_SCALE_MODIFIER

    except Exception as e:
        print("Failed to read accelerometer:", e)
        accel_x = 0.0
        accel_y = 0.0
        accel_z = 0.0


# ---------------- Individual Axis Getters ----------------
def getAccelX():
    return accel_x

def getAccelY():
    return accel_y

def getAccelZ():
    return accel_z


# ---------------- Optional Print Function ----------------
def printAccelerometer():
    print("X:", accel_x)
    print("Y:", accel_y)
    print("Z:", accel_z)
    print("-------------------")


# ---------------- Cleanup ----------------
def destroy():
    pass