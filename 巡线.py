import sensor, image, time, os,math,machine,pyb
from pyb import UART
import json
from pyb import LED
import lcd
from machine import I2C
import time


sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)    # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)      # Set frame size to QVGA (320x240)
sensor.set_windowing((320, 240))       # Set 240x240 window.
sensor.skip_frames(time=2000)          # Let the camera adjust.
clock = time.clock()

red_lab=(30,60,20,80,10,60)#红色线条
red_lab2=(0, 75, 30, 80, 10, 40)#红色交叉路口
white_lab=(90,100,-5,5,-5,5)#白色数字
black_lab=(0,40,-20,10,-10,20)#黑色终点/数字

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



x=0
data_car=b'888'
while(True):
    clock.tick()
    img = sensor.snapshot()
    pyb.delay(100)
    car_data=uart.read(3)
    if car_data==b'1' or car_data==b'2':
        data_car=car_data

    red_cross = img.find_blobs([red_lab2],roi = (0,60,320,120), pixels_threshold=200, area_threshold=200,merge=True)
    red_cross_l = img.find_blobs([red_lab2],roi = (40,110,40,100), pixels_threshold=200, area_threshold=200,merge=True)
    red_cross_r = img.find_blobs([red_lab2],roi = (265,110,40,100), pixels_threshold=200, area_threshold=200,merge=True)
    red_cross_z = img.find_blobs([red_lab2],roi = (100,60,120,120), pixels_threshold=200, area_threshold=200,merge=True)
    black_over = img.find_blobs([black_lab],roi = (2,110,315,128), pixels_threshold=200, area_threshold=200,merge=True)
    img.draw_rectangle((0,60,320,120),color=(225,0,0),thickness=2)#识别红色中间线的限制框
    img.draw_rectangle((40,110,40,100),color=(0,225,0),thickness=2)#识别红色左边的限制框
    img.draw_rectangle((265,110,40,100),color=(0,225,0),thickness=2)#识别红色右边的限制框
    img.draw_rectangle((100,60,120,120),color=(0,225,0),thickness=2)#识别红色右边的限制框

    #用于后退判断----
    red_arae1=[0,0,320,240];red_arae2=[0,0,320,240]
    if red_cross:
        red_xian=find_max(red_cross)
        red_arae1[0]=red_xian.x();red_arae1[1]=red_xian.y();red_arae1[2]=int(red_xian.w()/2);red_arae1[3]=int(red_xian.w()/2);
        red_arae2[0]=red_xian.x()+int(red_xian.w()/2);red_arae2[1]=red_xian.y();red_arae2[2]=int(red_xian.w()/2);red_arae2[3]=int(red_xian.w()/2);

    img.draw_rectangle(red_arae1,color=(255,0,0),thickness=2)#识别红色右边的限制框
    img.draw_rectangle(red_arae2,color=(255,0,0),thickness=2)#识别红色右边的限制框

    red_pix1=0;red_pix2=0
    red_1=img.find_blobs([red_lab2],roi = red_arae1, pixels_threshold=20, area_threshold=20,merge=True)
    red_2=img.find_blobs([red_lab2],roi = red_arae2, pixels_threshold=20, area_threshold=20,merge=True)

    if red_1:
        red_1m=find_max(red_1);
        red_pix1=red_1m.pixels();
        #print(1,red_pix1)
    if red_2:
        red_2m=find_max(red_2);
        red_pix2=red_2m.pixels();
        #print(2,red_pix2)

    red_cha=red_pix1-red_pix2#差值

    if red_cross:
        for blob1 in red_cross:
            img.draw_rectangle(blob1.rect(),color=(0,0,225),thickness=2)#识别红色右边的限制框
            if((red_cross_l and red_cross_z )or (red_cross_r and red_cross_z)):#判断是否拐弯
                if x <= 1:#转弯
                    uart.write("%d"%(blob1.cx()+100))#传输中点的坐标，小车自行计算
                    print(blob1.cx()+100)
                    #uart.write('1')
                    x=x+1
                    #pyb.delay(500)
                    print("------------------停")
                    time.sleep_ms(2000)
                else:#转完
                    img.draw_rectangle(blob1.rect(),color=(0,0,0),thickness=2)
                    print("十字路口")#返回像素数量
                    uart.write("%d"%(500))#色块右移--小车右转
                    print(500)
            else:#微调
                if data_car==b'888':
                    img.draw_rectangle(blob1.rect(),color=(0,0,255),thickness=2)
                    #print("像素数量:",blob1.pixels())#返回像素数量
                    #print(blob1.cx())
                    uart.write("%d"%(blob1.cx()+100))#传输中点的坐标，小车自行计算
                    print('微调坐标',blob1.cx()+100)
                else:
                    uart.write("%d"%(red_cha+500))
                    print('差值',red_cha)

    i = 0
    if black_over:#黑色终点
        for blob2 in black_over:
            if(blob2.pixels() > 200):
                i = i + 1
                #print("像素数量:",blob2.pixels())#返回像素数量
            img.draw_rectangle(blob2.rect(),color=(0,0,0),thickness=2)
        if(i > 7):
            print("停止")
            uart.write("%d"%(502))#小车停止
            print(501)
        #print(i)#黑点的个数
