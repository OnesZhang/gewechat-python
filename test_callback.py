from flask import Flask, request, jsonify
from gewechat_client.callback.handlers import MessageHandler
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)

# 创建 Flask 应用
app = Flask(__name__)
handler = MessageHandler()

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json  # 获取 JSON 数据
    logging.debug(f'Received data: {data}')  # 打印调试信息
    result = handler.receive_message(data)  # 处理消息
    logging.info(f'Result: {result}')  # 打印信息日志
    return jsonify(result)  # 返回处理结果

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 启动服务器 