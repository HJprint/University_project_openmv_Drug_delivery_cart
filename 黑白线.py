import sensor, image, time, math
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)#320*240个像素
sensor.skip_frames(time = 2000)
sensor.set_auto_exposure(False, 220000)
sensor.set_auto_gain(False) # must be turned off for color tracking 白平衡
sensor.set_auto_whitebal(False) # must be turned off for color tracking 自动增益

thresholds = [(75, 90, -19, 0, -17, 4),(15, 60, -15, 0, -20, 5)]#1 白色块 2  黑色块
clock = time.clock()
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

while(True):
    clock.tick()
    img = sensor.snapshot()
#------------识别弯道---------------
    blobs = img.find_blobs([thresholds[1]],x_stride=10,y_stride=10,invert=False, pixels_threshold=200, area_threshold=200)
    if blobs:
        max_blob=find_max(blobs)
        img.draw_rectangle(max_blob.rect(),color = (255, 0, 0))
        #print(max_blob.cx(),max_blob.area())
        if max_blob.area()<10000:
            if max_blob.cx()>120 and max_blob.cx() < 180:#前
                uart.write('0');print('前')
            if max_blob.cx()>90 and max_blob.cx() < 120:#左调
                uart.write('1');print('左')
            if max_blob.cx()>180 and max_blob.cx() < 200:#右调
                uart.write('2');print('右')

            if max_blob.cx()<90 :#左大调
                uart.write('3');print('大左')
            if max_blob.cx()>200 :#右大调
                uart.write('4');print('大右')
        else:
            uart.write('5')#停止
            print('停下')

