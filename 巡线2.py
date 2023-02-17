import sensor, image, time
from pyb import UART
from pyb import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
clock = time.clock()
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

red_lab=(30,60,20,80,10,60)#红色线条
red_lab2=(0, 75, 30, 80, 10, 60)#红色交叉路口
white_lab=(90,100,-5,5,-5,5)#白色数字
black_lab=(0,40,-20,10,-10,20)#黑色终点/数字



#返回最大色块（也就是返回最近的垃圾）
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


data_car=0
LED(2).on()
while(True):
    clock.tick()
    img = sensor.snapshot()
    car_data=uart.read(3)
    print(data_car)
    print(car_data)
    if car_data==b'999':
        data_car=1

    red_cross = img.find_blobs([red_lab2],roi = (0,60,320,120), pixels_threshold=200, area_threshold=200,merge=True)

    black_over = img.find_blobs([black_lab],roi = (2,110,315,128), pixels_threshold=200, area_threshold=200,merge=True)

    red_cross_l = img.find_blobs([red_lab2],roi = (40,120,40,120), pixels_threshold=200, area_threshold=200,merge=True)
    red_cross_r = img.find_blobs([red_lab2],roi = (265,120,40,120), pixels_threshold=200, area_threshold=200,merge=True)
    red_cross_z = img.find_blobs([red_lab2],roi = (120,120,100,120), pixels_threshold=200, area_threshold=200,merge=True)

    if data_car==0:
        #直线微调--------
        if red_cross:
            i = find_max(red_cross)
            img.draw_rectangle(i.rect(),color=(0,0,255),thickness=2)
            uart.write("%d"%(i.cx()+100))#传输中点的坐标，小车自行计算
            print('微调坐标',i.cx())

        #T字判断----------
        #5个限制区域
        img.draw_rectangle((0,70,20,70),color=(0,0,225),thickness=2)#识别红色右边的限制框
        img.draw_rectangle((80,70,20,70),color=(0,0,225),thickness=2)#识别红色右边的限制框
        img.draw_rectangle((150,70,20,70),color=(0,0,225),thickness=2)#识别红色右边的限制框
        img.draw_rectangle((240,70,20,70),color=(0,0,225),thickness=2)#识别红色右边的限制框
        img.draw_rectangle((300,70,20,70),color=(0,0,225),thickness=2)#识别红色右边的限制框
        hei_1 = img.find_blobs([black_lab],roi = (0,70,20,70), pixels_threshold=20, area_threshold=20)
        hei_2 = img.find_blobs([black_lab],roi = (80,70,20,70), pixels_threshold=20, area_threshold=20)
        hei_3 = img.find_blobs([black_lab],roi = (150,70,20,70), pixels_threshold=20, area_threshold=20)
        hei_4 = img.find_blobs([black_lab],roi = (240,70,20,70), pixels_threshold=20, area_threshold=20)
        hei_5 = img.find_blobs([black_lab],roi = (300,70,20,70), pixels_threshold=20, area_threshold=20)
        if hei_1 and hei_2 and hei_3 and hei_4 and hei_5:
            uart.write("%d"%(800))#传输中点的坐标，小车自行计算
            print("T字")

    if data_car==1:
        #直线微调--------
        if (red_cross_l and red_cross_z) or (red_cross_r and red_cross_z):
            for x in range(20):
                uart.write("%d"%(900))#识别为十字
                print('十字')

        else:
            if red_cross:
                i = find_max(red_cross)
                img.draw_rectangle(i.rect(),color=(0,0,255),thickness=2)
                uart.write("%d"%(i.cx()+100))#传输中点的坐标，小车自行计算
                print('微调坐标',i.cx())
        #十字判断-----------
        #三个限制区域
        img.draw_rectangle((40,120,40,120),color=(0,225,0),thickness=2)#识别红色右边的限制框
        img.draw_rectangle((265,120,40,120),color=(0,225,0),thickness=2)#识别红色右边的限制框
        img.draw_rectangle((120,120,100,120),color=(0,225,0),thickness=2)#识别红色右边的限制框


        #终点判断-----------
        i = 0
        if black_over:#黑色终点
            for blob2 in black_over:
                if(blob2.pixels() > 200):
                    i = i + 1
                    #print("像素数量:",blob2.pixels())#返回像素数量
                img.draw_rectangle(blob2.rect(),color=(0,0,0),thickness=2)
            if(i >=6):
                print("停止")
                uart.write("%d"%(502))#小车停止
                print(502)
            #print(i)#黑点的个数
