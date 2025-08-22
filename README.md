# Bilibili 登录工具

一个简单的Bilibili登录工具，通过网页界面获取access_token。

## 功能特性

- 🌐 网页界面操作，无需命令行
- 📱 扫码登录，支持手机Bilibili App
- 🔑 自动获取access_token和用户信息
- 🔑 获取access_token和用户信息

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
``` 

2. 运行应用：
```bash
python app.py
```

3. 打开浏览器访问：`http://localhost:5000`

4. 使用手机Bilibili App扫描二维码完成登录

5. 登录成功后，可直接从网页界面复制access_token等信息

## 文件说明

- `app.py` - 主程序文件，Flask Web应用
- `templates/index.html` - 网页界面模板
- `requirements.txt` - Python依赖包列表
- `start.bat` - Windows快速启动脚本

## 注意事项

- 请妥善保管登录信息，不要泄露给他人

## 技术实现

- 使用Flask框架构建Web应用
- 调用Bilibili TV端登录API
- 支持API签名验证
- 自动处理登录状态轮询

