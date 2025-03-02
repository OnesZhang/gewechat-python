# 掉线通知示例
"""
{
    "TypeName": "Offline",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22"  掉线号的wxid
}
"""

class OfflineNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        # 创建离线通知对象
        # 创建包含离线通知信息的字典
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid           # 掉线号的wxid
        }
        return message

    def handle(self, message):
        # 处理离线通知的业务逻辑
        return {
            'success': True,
            'message': '离线通知已处理',
            'data': message
        }