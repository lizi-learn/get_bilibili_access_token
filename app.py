from flask import Flask, render_template, jsonify, request
import qrcode
import base64
import io
import os
import time
import requests
import json
import urllib
import hashlib
from threading import Thread

app = Flask(__name__)

def tvsign(params, appkey='4409e2ce8ffd12b8', appsec='59b43e04ad6965f34319062b478f83dd'):
    '为请求参数进行 api 签名'
    params.update({'appkey': appkey})
    params = dict(sorted(params.items())) # 重排序参数 key
    query = urllib.parse.urlencode(params) # 序列化参数
    sign = hashlib.md5((query+appsec).encode()).hexdigest() # 计算 api 签名
    params.update({'sign':sign})
    return params

def generate_qr_code(url):
    '生成二维码并转换为base64'
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_qr_code')
def get_qr_code():
    try:
        # 获取二维码
        loginInfo = requests.post('https://passport.bilibili.com/x/passport-tv-login/qrcode/auth_code',
            params=tvsign({
                'local_id':'0',
                'ts':int(time.time())
            }),
            headers={
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            }
        ).json()
        
        if loginInfo['code'] == 0:
            qr_code = generate_qr_code(loginInfo['data']['url'])
            return jsonify({
                'success': True,
                'qr_code': qr_code,
                'auth_code': loginInfo['data']['auth_code']
            })
        else:
            return jsonify({
                'success': False,
                'error': f'获取二维码失败: {loginInfo.get("message", "未知错误")}'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'生成二维码时出错: {str(e)}'
        })

@app.route('/check_login')
def check_login():
    auth_code = request.args.get('auth_code')
    if not auth_code:
        return jsonify({'success': False, 'error': '缺少auth_code参数'})
    
    try:
        pollInfo = requests.post('https://passport.bilibili.com/x/passport-tv-login/qrcode/poll',
            params=tvsign({
                'auth_code': auth_code,
                'local_id':'0',
                'ts':int(time.time())
            }),
            headers={
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            }
        ).json()
        
        if pollInfo['code'] == 0:
            loginData = pollInfo['data']
            

            
            return jsonify({
                'success': True,
                'message': f"登录成功, 有效期至{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + int(loginData['expires_in'])))}",
                'expires_in': loginData['expires_in'],
                'access_token': loginData['token_info']['access_token'],
                'mid': loginData['token_info']['mid']
            })
            
        elif pollInfo['code'] == -3:
            return jsonify({'success': False, 'error': 'API校验密匙错误'})
        elif pollInfo['code'] == -400:
            return jsonify({'success': False, 'error': '请求错误'})
        elif pollInfo['code'] == 86038:
            return jsonify({'success': False, 'error': '二维码已失效'})
        elif pollInfo['code'] == 86039:
            return jsonify({'success': False, 'error': '等待扫码中...'})
        else:
            return jsonify({'success': False, 'error': f'未知错误: {pollInfo.get("message", "未知错误")}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'检查登录状态时出错: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
