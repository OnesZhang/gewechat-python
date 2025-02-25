from gewechat_client import GewechatClient
from flask import Flask, request
import os
import threading
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

def init_wechat():
    # 配置参数
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:2531/v2/api")
    token = os.environ.get("GEWECHAT_TOKEN", "xxx")
    app_id = os.environ.get("APP_ID", "xxx")
    
    # 创建 GewechatClient 实例
    client = GewechatClient(base_url, token)

    # 登录, 自动创建二维码，扫码后自动登录
    app_id, error_msg = client.login(app_id=app_id)
    if error_msg:
        logger.error("微信登录失败")
        return None, None
    
    logger.info("微信登录成功")
    return client, app_id

@app.route('/getWechatCallBack', methods=['POST'])
def wechat_callback():
    try:
        data = request.get_json()
        # 打印完整的回调消息
        logger.debug("收到回调消息:")
        logger.debug(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 获取消息类型
        msg_type = data.get('TypeName')
        logger.debug(f"消息类型: {msg_type}")
        
        return {'ret': 200, 'msg': 'success'}
    except Exception as e:
        logger.error(f"处理回调消息异常: {str(e)}")
        return {'ret': 500, 'msg': str(e)}

def run_flask():
    app.run(host='0.0.0.0', port=3000)

def demo_send_message(client, app_id):
    """演示发送消息功能"""
    send_msg_nickname = "张伟"  # 要发送消息的好友昵称
    try:
        # 获取好友列表
        fetch_contacts_list_result = client.fetch_contacts_list(app_id)
        if fetch_contacts_list_result.get('ret') != 200 or not fetch_contacts_list_result.get('data'):
            logger.error("获取通讯录列表失败:", fetch_contacts_list_result)
            return
        friends = fetch_contacts_list_result['data'].get('friends', [])
        if not friends:
            logger.error("获取到的好友列表为空")
            return
        logger.info("获取到的好友列表: %s", friends)

        # 获取好友的简要信息
        friends_info = client.get_brief_info(app_id, friends)
        if friends_info.get('ret') != 200 or not friends_info.get('data'):
            logger.error("获取好友简要信息失败: %s", friends_info)
            return
        # {
        #     "ret": 200,
        #     "msg": "获取联系人信息成功",
        #     "data": [
        #         {
        #             "userName": "weixin",
        #             "nickName": "微信团队",
        #             "pyInitial": "WXTD",
        #             "quanPin": "weixintuandui",
        #             "sex": 0,
        #             "remark": "",
        #             "remarkPyInitial": "",
        #             "remarkQuanPin": "",
        #             "signature": null,
        #             "alias": "",
        #             "snsBgImg": null,
        #             "country": "",
        #             "bigHeadImgUrl": "https: //wx.qlogo.cn/mmhead/Q3auHgzwzM6H8bJKHKyGY2mk0ljLfodkWnrRbXLn3P11f68cg0ePxA/0",
        #             "smallHeadImgUrl": "https://wx.qlogo.cn/mmhead/Q3auHgzwzM6H8bJKHKyGY2mk0ljLfodkWnrRbXLn3P11f68cg0ePxA/132",
        #             "description": null,
        #             "cardImgUrl": null,
        #             "labelList": null,
        #             "province": "",
        #             "city": "",
        #             "phoneNumList": null
        #         }
        #     ]
        # }
        
        # 找对目标好友的wxid
        friends_info_list = friends_info['data']
        if not friends_info_list:
            logger.error("获取到的好友简要信息列表为空")
            return
        wxid = None
        for friend_info in friends_info_list:
            if friend_info.get('nickName') == send_msg_nickname:
                logger.info("找到好友: %s", friend_info)
                wxid = friend_info.get('userName')
                break
        if not wxid:
            logger.error(f"没有找到好友: {send_msg_nickname} 的wxid")
            return
        logger.info("找到好友: %s", wxid)

        # 发送消息
        send_msg_result = client.post_text(app_id, wxid, "你好啊")
        if send_msg_result.get('ret') != 200:
            logger.error("发送消息失败: %s", send_msg_result)
            return
        logger.info("发送消息成功: %s", send_msg_result)
    except Exception as e:
        logger.error("执行消息发送示例失败: %s", str(e))

def main():
    # 启动Flask服务
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # 初始化微信客户端
    client, app_id = init_wechat()
    if not client:
        return
        
    logger.info("系统启动完成,等待接收消息...")
    
    # 执行消息发送示例
    demo_send_message(client, app_id)
    
    # 保持主线程运行
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        logger.info("程序退出...")

if __name__ == "__main__":
    main()
