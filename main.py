# LINE 聊天機器人的基本資料



from inspect import iscoroutinefunction
import os
from tkinter import Image
from flask import Flask, request, abort,render_template,url_for,redirect,session,Response
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
import numpy as np
import string,qrcode,random,requests,cv2,time
import RPi.GPIO as GPIO
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306



app = Flask(__name__,
            static_folder="static", #靜態檔案資料夾名稱
            static_url_path="/static" #靜態檔案對應網址路徑
)

# LINE 聊天機器人的基本資料
# config = configparser.ConfigParser()
# config.read('config.ini')
line_bot_api = LineBotApi('n1ixZcsYtHe4NbGIqATUOYBJoNyuGY++xSBxPU6TzAd12xK4JTrOHQuvizKocWIv3wm3hJRW1tA7nulYjGyyjlg0+wpq97oS/kbKF990epLz9ye+23eXaF7Y4uA3eNHKnFWMJ+PAl+1nfRQTk4UIKgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7cf77a8be12339f8169eb7cf466f2df0')

heroku_url='https://benwang2000.herokuapp.com/'
ngrok_url='https://0c99-49-158-68-104.jp.ngrok.io'
header_from={'Content-Type':'multipart/form-data'}
header_json={'Content-Type':'application/json'}

app.secret_key="orlak"

def gen_frames():
    cap=cv2.VideoCapture(0)
    while True:
        success,frame=cap.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode("as.jpg",frame)
            frame=buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
                    
def open_door():
    sg90_freq=50
    GPIO.setmode(GPIO.BCM)   #gpio模式
    GPIO.setup(12,GPIO.OUT)  #輸出腳位
    SG90=GPIO.PWM(12,sg90_freq)     # 建立實體物件 腳位,頻率
    SG90.start(0)           #開始
    def duty_cycle_angle(angle=0):
        duty_cycle=(0.05*sg90_freq)+(0.19*sg90_freq*angle/180)
        return duty_cycle
    def move(degree):
        worksa=duty_cycle_angle(degree)
        print(degree,"度＝",worksa,"週期")
        SG90.ChangeDutyCycle(worksa)
    # duty_cycle_angle(0)
    list=[50,180,50]
    for i in range(3):
        for degree in list:
            move(degree)
            time.sleep(0.35)
    SG90.stop()


def det_programe():   #偵測qrcode程式
    i2c = busio.I2C(SCL, SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    
    # ---------------------------------
    star=time.time()
    cap=cv2.VideoCapture(0)
    qrcode = cv2.QRCodeDetector()
    
    timeend=0
    pushqrcode=session["pushqrcode"]
    print('傳送到偵測程式中的pushqrcode',pushqrcode)
    while int(timeend)-int(star)<180:
        ret,frame=cap.read()
        data, bbox, rectified = qrcode.detectAndDecode(frame)  # 偵測圖片中的 QRCode 
        print("ret--",ret,"data--",data,int(timeend)-int(star),"秒")
        timeend=time.time()
        sec=str(180-(int(timeend)-int(star)))
        print('剩餘時間',sec)
        
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
        font = ImageFont.truetype('TaipeiSansTCBeta-Bold.ttf', 12)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)    
        session["getqrcode"]=data #----------------------

        if data == pushqrcode:
            print(data,"==",pushqrcode)
            # session["getqrcode"]=data #----------------------
            draw.text((x+5, top + 5), "開門剩餘 "+sec+" 秒", font=font, fill=255)
            draw.text((x+5, top + 20), "密碼正確,許可開門" , font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(1)
            open_door()
            break
        elif data == '' and int(sec)>0:
            print("沒有收到",data)
            draw.text((x+5, top + 5),"開門剩餘 "+sec+" 秒", font=font, fill=255)
            draw.text((x+20, top + 20), "等待驗證......" , font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(1)
            continue

            
        elif data != pushqrcode:
            print("密碼不相符",data)
            draw.text((x, top + 2), "開門剩餘 " +sec+" 秒", font=font, fill=255)
            draw.text((x+5, top + 17), "密碼失效,重新申請" , font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(0.1)
            break  
        else:
            draw.text((x+5, top + 10), "密碼失效,重新申請" , font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(10)
            disp.fill(0)
    cap.release()
    cv2.destroyAllWindows() 
    
    

    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
     
@app.route('/close')
def close():
    i2c = busio.I2C(SCL, SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    disp.fill(0)
    disp.show()
    return "Oled close"

    
# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 產生qrcode
@app.route('/qrc')
def qrc():
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    print("產生qrcode隨機碼",ran_str)
    img=qrcode.make(ran_str)
    img.save('./static/la.png')
    session["pushqrcode"]=ran_str  #------------------------
    session["getqrcode"]=None
    user_id ='Uc6ca3a2dbabeb7576ec4bfe80fbaa9aa'
    url=ngrok_url+'/static/la.png'
    line_bot_api.push_message(user_id,ImageSendMessage(original_content_url=url, preview_image_url=url))
    line_bot_api.push_message(user_id,TextSendMessage(text="你有3分鐘時間開門"))
    return redirect('/pi')

@app.route('/pi')
def pi():
    det_programe()  #呼叫qrcode偵測程式
    getqrcode1=session["getqrcode"]
    pushqrcode1=session["pushqrcode"]
    print('backfeed',pushqrcode1,getqrcode1)
    user_id = 'Uc6ca3a2dbabeb7576ec4bfe80fbaa9aa'
    if getqrcode1 == pushqrcode1:
        line_bot_api.push_message(user_id,TextSendMessage(text="密碼驗證成功,門已經開啟"))
        return "密碼驗證成功,門已經開啟"
    elif getqrcode1 == '':
        line_bot_api.push_message(user_id,TextSendMessage(text="沒有監測到密碼,超過時間請再申請一次"))
        return "沒有監測到密碼,超過時間請再申請一次"
    elif getqrcode1 != pushqrcode1:
        line_bot_api.push_message(user_id,TextSendMessage(text="您密碼錯誤,請再申請一次"))
        return "您密碼錯誤,請再申請一次"
    else:
        return 'something wrong!!'
    

#學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


if __name__ == "__main__":
    app.run(debug=True)
