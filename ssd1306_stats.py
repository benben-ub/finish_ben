# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

from dis import dis
import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
beforetime=time.time()
while True:
    disp.fill(0)
    disp.show()
    width = disp.width
    height = disp.height
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    padding = -2
    top = padding
    x = 0
    font = ImageFont.truetype('TaipeiSansTCBeta-Bold.ttf', 14)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    nowtime=time.time()
    print('beforetime',beforetime,'nowtime',nowtime)
    
    if int(nowtime)-int(beforetime)<150:
        la=str(300-int(nowtime-beforetime))
        print(300-int(nowtime-beforetime),'秒')
        
        draw.text((x+20, top + 2), la +'秒', font=font, fill=255)
        disp.image(image)
        disp.show()
       
        time.sleep(1)
    else:
            break

        # draw.text((x, top + 2), "哈囉你好"+time , font=font, fill=255)
    # draw.text((x+5, top + 17), "密碼正確,許可開門" , font=font, fill=255)
    # draw.text((x+5, top + 17), "密碼錯誤,重新申請" , font=font, fill=255)
        # draw.text((x+5, top + 17), "等待驗證....." , font=font, fill=255)
 
    # draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    # draw.text((x, top + 8), "CPU load:" + CPU, font=font, fill=255)
    # draw.text((x, top + 16), MemUsage, font=font, fill=255)
    # draw.text((x, top + 25), Disk, font=font, fill=255)

    # Display image.
        # disp.image(image)
        # disp.show()
        # time.sleep(1)
