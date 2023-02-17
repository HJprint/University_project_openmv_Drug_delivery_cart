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
sensor.set_auto_exposure(False, 40000)#修改曝光度
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

#参数
area=[0,0,320,240];area_1=[0,0,320,240];area_2=[0,0,320,240]
area_3=[0,0,320,240];area_3_1=[0,0,320,240];area_4=[0,0,320,240]

#数字识别
def num(wh,di_pix,ding_pix,zhong_3,zhong_3_xia,zhong_6):
    if wh<0.6:return'1'#1
    else:#非1
        if di_pix>200:return'2'
        else:#非1，2
            if di_pix<80:#4和7
                if ding_pix<80:return'4'#4
                else:return'7'
            else:#非1，4，7(3,5,6,8)
                if zhong_3==0:return'3'
                else:#非1，4，7，3（5，6，8）
                    if zhong_3_xia==0:return'5'
                    else:#非1，4，7，3，5（6，8）
                        if zhong_6==0:return'6'
                        else:return'8'



#主循环
while(1):
    clock.tick()
    #sensor.set_windowing((0,0,320,240))
    img = sensor.snapshot()
    LED(2).on()
    #数字识别
    number_areas = img.find_blobs([white_lab], pixels_threshold=20, area_threshold=20)
    red_lines = img.find_blobs([red_lab], pixels_threshold=20, area_threshold=20)
    black_numbers = img.find_blobs([black_lab], pixels_threshold=200, area_threshold=200,merge=True)

    if black_numbers:#如果有黑色色块
        for i in black_numbers:#框出所有的黑色色块
            #参数重置
            wh=0;di_pix=0;ding_pix=0;zhong_3=0;zhong_3_xia=0;zhong_6=0
            #1的识别
            wh=i.w()/i.h()
            area[0]=i.x();area[1]=i.y()+int(i.h()/2);area[2]=i.w();area[3]=int(i.h()/2);
            #底边参数
            area_2[0]=i.x();area_2[1]=i.y()+i.h()-5;area_2[2]=i.w();area_2[3]=5;
            blob_2s = img.find_blobs([black_lab],roi=area_2, pixels_threshold=20, area_threshold=20,merge=True)
            if blob_2s:
                blob_2=find_max(blob_2s);
                img.draw_rectangle(blob_2.rect(),color=(225,0,0),thickness=2)
                di_pix=blob_2.area()
            #顶边参数
            area_1[0]=i.x();area_1[1]=i.y();area_1[2]=i.w();area_1[3]=5;
            blob_1s = img.find_blobs([black_lab],roi=area_1, pixels_threshold=20, area_threshold=20,merge=True)
            if blob_1s:
                blob_1=find_max(blob_1s);
                img.draw_rectangle(blob_1.rect(),color=(225,0,0),thickness=2)
                ding_pix=blob_1.area()
            #3的左中间
            area_3[0]=i.x();area_3[1]=i.y()+int(i.h()/3);area_3[2]=int(i.w()/3);area_3[3]=int(i.h()/3);
            blob_3s = img.find_blobs([black_lab],roi=area_3, pixels_threshold=20, area_threshold=20,merge=True)
            if blob_3s:
                blob_3=find_max(blob_3s);
                img.draw_rectangle(blob_3.rect(),color=(0,225,0),thickness=2)
                zhong_3=blob_3.area()
                #3中间的下面
                area_3_1[0]=blob_3.x();area_3_1[1]=blob_3.y()+blob_3.h();area_3_1[2]=blob_3.w();area_3_1[3]=5;
                blob_3_1s = img.find_blobs([black_lab],roi=area_3_1, pixels_threshold=20, area_threshold=20,merge=True)
                if blob_3_1s:
                    blob_3_1=find_max(blob_3_1s);
                    img.draw_rectangle(blob_3_1.rect(),color=(0,0,225),thickness=2)
                    zhong_3_xia=blob_3_1.area()
            #6的中间
            area_4[0]=i.x()+int(i.w()/3);area_4[1]=i.y()+int(i.h()*2/9);area_4[2]=int(i.w()*5/7);area_4[3]=5;
            blob_4s = img.find_blobs([black_lab],roi=area_4, pixels_threshold=20, area_threshold=20,merge=True)
            if blob_4s:
                blob_4=find_max(blob_4s);
                img.draw_rectangle(blob_4.rect(),color=(255,0,0),thickness=2)
                zhong_6=blob_4.area()

            #打印识别结果
            print(num(wh,di_pix,ding_pix,zhong_3,zhong_3_xia,zhong_6))
            #框出每一个数字
            img.draw_rectangle(i.rect(),color=(0,0,0),thickness=2)
            #print('8--------------------------')
            print('长宽比',wh)
            #识别参数打印
            print(wh,di_pix,ding_pix,zhong_3,zhong_3_xia,zhong_6)



