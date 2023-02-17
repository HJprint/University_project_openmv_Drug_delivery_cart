import sensor, image, time, os, tf, math,machine
from pyb import UART
import json
from pyb import LED
import lcd
from machine import I2C
from vl53l1x import VL53L1X
import time


sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)    # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)      # Set frame size to QVGA (320x240)
sensor.set_windowing((320, 240))       # Set 240x240 window.
sensor.set_auto_whitebal(False, rgb_gain_db=(65.2256,60.2071,61.9736))
sensor.set_auto_exposure(False, 60000)#修改曝光度
sensor.set_auto_gain(False, 22)
#sensor.set_auto_whitebal(False)
#sensor.set_auto_exposure(False)
#sensor.set_auto_gain(False)
sensor.skip_frames(time=2000)          # Let the camera adjust.
clock = time.clock()

red_lab=(0,100,40,70,20,60)#红色线条
white_lab=(90,100,-5,5,-5,5)#白色数字
black_lab=(15,60,-20,10,-10,20)#黑色终点/数字

#串口通信
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

#返回最大色块（也就是返回最近的垃圾）
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob
#数字识别
def judge(pix):
    if pix>100 and pix<700:return 'battery'#5000-14000
    if pix>=700 and pix<=3000:return 'none'#400-1310
    if pix>=3000 and pix<=17000:return 'cup'#400-1310

#参数


while(True):
    clock.tick()
    img = sensor.snapshot()
    LED(2).on()
    #数字识别
    number_areas = img.find_blobs([white_lab], pixels_threshold=20, area_threshold=20)
    red_lines = img.find_blobs([red_lab], pixels_threshold=200, area_threshold=200)
    black_numbers = img.find_blobs([black_lab], pixels_threshold=200, area_threshold=200,merge=True)
    if black_numbers:#如果有黑色色块
        for i in black_numbers:#框出所有的黑色色块
            img.draw_rectangle(i.rect(),color=(0,0,0),thickness=2)
    #红线识别
    if red_lines:
        red_line = find_max(red_lines)
        img.draw_rectangle(red_line.rect(),color=(225,0,0),thickness=2)

    #if black_numbers:
        #number = find_max(black_numbers)
        #img.draw_rectangle(number.rect(),color=(225,0,0),thickness=2)




















