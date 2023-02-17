import sensor, image, time
from pyb import UART
import time
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((320, 240))
#sensor.set_auto_whitebal(False, rgb_gain_db=(65.2256,60.2071,61.9736))
#sensor.set_auto_exposure(False)
#sensor.set_auto_gain(False, 22)
sensor.skip_frames(time=2000)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

clock = time.clock()
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

#红的
#red_lab=(30, 65, 25, 61, -14, 41)
#black_lab=(15, 53, -15, 8, -8, 15)

#黑色Openmv
red_lab=(32, 70, 11, 86, 12, 68)
#黑色Openmv
black_lab=(3, 30, -21, 41, -20, 25)
while(True):
    clock.tick()
    img = sensor.snapshot()
    red_LineM = img.find_blobs([red_lab],roi = (30,120,260,60), pixels_threshold=200, area_threshold=200,merge=True)
    red_LineL = img.find_blobs([red_lab],roi = (0,120,30,60), pixels_threshold=200, area_threshold=200,merge=True)
    red_LineR = img.find_blobs([red_lab],roi = (290,120,30,60), pixels_threshold=200, area_threshold=200,merge=True)
    img.draw_rectangle(0,120,320,60, color = (0,255,255), thickness = 2, fill = False)
    black_over = img.find_blobs([black_lab],roi = (0,110,320,128), pixels_threshold=200, area_threshold=200,merge=True)
    #img.draw_rectangle(0,110,320,128, color = (255,255,0), thickness = 2, fill = False)
    if red_LineM:
        for blob1 in red_LineM:
            print("中间像素数量:",blob1.pixels())
            if(blob1.pixels() > 200  and blob1.pixels() < 1500 and blob1.w() < 50):
                img.draw_rectangle(blob1.rect(),color=(0,155,155),thickness=2)
                print("中间像素坐标:",blob1.cx())
                if(blob1.cx() >= 175 and blob1.cx() < 187):
                    print("小右转")
                    uart.write('1')
                if(blob1.cx() <= 145 and blob1.cx() > 133):
                    print("小左转")
                    uart.write('2')
                if(blob1.cx() > 187 and blob1.cx() < 220):
                    print("中右转")
                    uart.write('3')
                if(blob1.cx() < 133 and blob1.cx() > 100):
                    print("中左转")
                    uart.write('4')
                #if(blob1.cx() > 220 and blob1.cx() < 270):
                    #print("大右转")
                    #uart.write('5')
                #if(blob1.cx() < 100 and blob1.cx() > 30):
                    #print("大左转")
                    #uart.write('6')
                if(blob1.cx() > 145 and blob1.cx() < 175):
                    print("正常行驶")
                    uart.write('0')
    if (red_LineL):
        if(red_LineR):
            blob2=find_max(red_LineL)
            print("左侧像素数量:",blob2.pixels())
            blob3=find_max(red_LineR)
            print("右侧像素数量:",blob3.pixels())
            img.draw_rectangle(blob2.rect(),color=(0,0,0),thickness=2)
            img.draw_rectangle(blob3.rect(),color=(0,0,0),thickness=2)
            if(blob1.pixels() > 2200 and blob1.pixels() < 5600 and blob2.pixels() > 100 and blob2.pixels() < 500 and blob2.pixels() > 100 and blob2.pixels() < 500 and blob2.w()> 20 and blob3.w()> 20):
                img.draw_rectangle(blob1.rect(),color=(0,255,0),thickness=2)
                print("十字路口")
                uart.write('9')
        else:
            blob2=find_max(red_LineL)
            print("左侧像素数量:",blob2.pixels())
            img.draw_rectangle(blob2.rect(),color=(0,0,255),thickness=2)
            print("左三岔路")
            uart.write('7')
    if (red_LineR):
        if(red_LineL):
            blob2=find_max(red_LineL)
            print("左侧像素数量:",blob2.pixels())
            blob3=find_max(red_LineR)
            print("右侧像素数量:",blob3.pixels())
            img.draw_rectangle(blob2.rect(),color=(0,0,0),thickness=2)
            img.draw_rectangle(blob3.rect(),color=(0,0,0),thickness=2)
            if(blob1.pixels() > 2200 and blob1.pixels() < 5600 and blob2.pixels() > 100 and blob2.pixels() < 500 and blob2.pixels() > 100 and blob2.pixels() < 500 and blob2.w()> 20 and blob3.w()> 20):
                img.draw_rectangle(blob1.rect(),color=(0,255,0),thickness=2)
                print("十字路口")
                uart.write('9')
        else:
            blob3=find_max(red_LineR)
            print("右侧像素数量:",blob3.pixels())
            img.draw_rectangle(blob3.rect(),color=(0,0,255),thickness=2)
            print("右三岔路")
            uart.write('8')
    i = 0
    if black_over:
        for blob2 in black_over:
            if(blob2.pixels() > 200  and blob2.pixels() < 900):
                i = i + 1
            img.draw_rectangle(blob2.rect(),color=(255,0,0),thickness=2)
        if(i > 5 and i < 12):
            print("停止")
            uart.write('A')
        print(i)
