# LINE 聊天機器人的基本資料



import os
from tkinter import Image
from flask import Flask, request, abort,render_template,url_for,redirect,session
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
import numpy as np
import string,qrcode,random,requests,cv2,time

app = Flask(__name__,
            static_folder="static", #靜態檔案資料夾名稱
            static_url_path="/static" #靜態檔案對應網址路徑
)

# LINE 聊天機器人的基本資料
# config = configparser.ConfigParser()
# config.read('config.ini')
line_bot_api = LineBotApi('n1ixZcsYtHe4NbGIqATUOYBJoNyuGY++xSBxPU6TzAd12xK4JTrOHQuvizKocWIv3wm3hJRW1tA7nulYjGyyjlg0+wpq97oS/kbKF990epLz9ye+23eXaF7Y4uA3eNHKnFWMJ+PAl+1nfRQTk4UIKgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7cf77a8be12339f8169eb7cf466f2df0')

heroku_url='https://finishben1977.herokuapp.com'
ngrok_url='https://f576-2404-0-8022-6f81-160f-6b29-9f05-2bdf.jp.ngrok.io'
header_from={'Content-Type':'multipart/form-data'}
header_json={'Content-Type':'application/json'}

app.secret_key="orlak"

def open_door():
    print("門已打開") 

def det_programe():   #偵測qrcode程式
    star=time.time()
    cap=cv2.VideoCapture(0)
    qrcode = cv2.QRCodeDetector()
    timeend=0
    pushqrcode=session["pushqrcode"]
    print('傳送到偵測程式中的pushqrcode',pushqrcode)
    while int(timeend)-int(star)<120:
        ret,frame=cap.read()
        data, bbox, rectified = qrcode.detectAndDecode(frame)  # 偵測圖片中的 QRCode 
        
        print("ret--",ret,"data--",data,int(timeend)-int(star))
        timeend=time.time()
        if data ==pushqrcode:
            print(data,"==",pushqrcode)
            session["getqrcode"]=data #----------------------
            open_door()
            break
        elif data=="":
            print("沒有收到",data)
            continue  
        elif data!=pushqrcode:
            print("密碼不相符",data)
            break  

    cap.release()
    cv2.destroyAllWindows() 
    
  
     
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
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    print("產生qrcode隨機碼",ran_str)
    img=qrcode.make(ran_str)
    img.save('./static/la.png')
    session["pushqrcode"]=ran_str  #------------------------
    session["getqrcode"]=None
    user_id = 'Uc6ca3a2dbabeb7576ec4bfe80fbaa9aa'
    url=heroku_url+'/static/la.png'
    line_bot_api.push_message(user_id,ImageSendMessage(original_content_url=url, preview_image_url=url))
    line_bot_api.push_message(user_id,TextSendMessage(text="你有5分鐘時間開門"))
    return redirect('/pi')

@app.route('/pi')
def pi():
    det_programe()  #呼叫qrcode偵測程式
    getqrcode=session["getqrcode"]
    pushqrcode=session["pushqrcode"]
    print('backfeed',pushqrcode,getqrcode)
    user_id = 'Uc6ca3a2dbabeb7576ec4bfe80fbaa9aa'
    if getqrcode==pushqrcode:
        line_bot_api.push_message(user_id,TextSendMessage(text='驗證密碼正確,門開了'))
        return f"<p>門開了,驗證密碼是{getqrcode}</p>"
    elif getqrcode==None:
        line_bot_api.push_message(user_id,TextSendMessage(text="沒有驗證密碼,且超過五分鐘請在申請一次,驗證密碼為{getqrcode}"))
        return f"<p>沒有驗證密碼,且超過五分鐘請在申請一次,驗證密碼為{getqrcode}</p>"
    elif getqrcode!=pushqrcode:
        line_bot_api.push_message(user_id,TextSendMessage(text="您密碼錯誤請在申請一次,驗證密碼是{getqrcode}"))
        return f"<p>您密碼錯誤請在申請一次,驗證密碼是{getqrcode}</p>"
    else:
        return 'nook'
    

#學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


if __name__ == "__main__":
    app.run(debug=True)
