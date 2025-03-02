# 好友请求通知处理模块


# 好友添加请求通知示例
"""
{
    "TypeName": "AddMsg",   消息类型
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
    "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
    "Data":
    {
        "MsgId": 1040356166,    消息ID
        "FromUserName":
        {
            "string": "fmessage"    消息发送人的wxid
        },
        "ToUserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
        },
        "MsgType": 37,  消息类型，37是好友添加请求通知
        "Content":
        {
            "string": "<msg fromusername=\"wxid_phyyedw9xap22\" encryptusername=\"v3_020b3826fd03010000000000feba078fc1e760000000501ea9a3dba12f95f6b60a0536a1adb6f6352c38d0916c9c74045d85aa602efa2d81b84adde05d285124e8a54b9fcd039f725d6ac0d3bd651c7c74503a@stranger\" fromnickname=\"朝夕。\" content=\"我是朝夕。\" fullpy=\"chaoxi\" shortpy=\"CX\" imagestatus=\"3\" scene=\"6\" country=\"\" province=\"\" city=\"\" sign=\"\" percard=\"0\" sex=\"1\" alias=\"\" weibo=\"\" albumflag=\"3\" albumstyle=\"0\" albumbgimgid=\"\" snsflag=\"273\" snsbgimgid=\"http://shmmsns.qpic.cn/mmsns/FzeKA69P5uIdqPfQxp59LvOohoE2iaiaj86IBH1jl0F76aGvg8AlU7giaMtBhQ3bPibunbhVLb3aEq4/0\" snsbgobjectid=\"14216284872728580667\" mhash=\"d36f4cc1c8bba1df41b93d2215133cdb\" mfullhash=\"d36f4cc1c8bba1df41b93d2215133cdb\" bigheadimgurl=\"http://wx.qlogo.cn/mmhead/ver_1/G3G6r1OBfCIO40FTribZ3WvrLQbnMibfT5PyRaxeyjXgLqA8M94lKic3ibOztlrawo2xpVQaH7V6yhYATia3GKbVH8MhRbnKQGfNZ4EY8Zc85uy49P5WSZZrntbECUpQfrjRu/0\" smallheadimgurl=\"http://wx.qlogo.cn/mmhead/ver_1/G3G6r1OBfCIO40FTribZ3WvrLQbnMibfT5PyRaxeyjXgLqA8M94lKic3ibOztlrawo2xpVQaH7V6yhYATia3GKbVH8MhRbnKQGfNZ4EY8Zc85uy49P5WSZZrntbECUpQfrjRu/132\" ticket=\"v4_000b708f0b040000010000000000c502ff3b59b31c08394fdaefa0651000000050ded0b020927e3c97896a09d47e6e9eec84bb6bebe542fb120b366298a0157c280337855083f4a87fc4b15cfba311a11720041ce2d9f8a575cf7b432a2c0bebc5ed9c9a70bf7784c54ebbfb816e54e0fda2befcf2f873d162f5ed54108c76ce53310321077ced22420c5fbd199cff57d8e0a583f155e7e558@stranger\" opcode=\"2\" googlecontact=\"\" qrticket=\"\" chatroomusername=\"\" sourceusername=\"\" sourcenickname=\"\" sharecardusername=\"\" sharecardnickname=\"\" cardversion=\"\" extflag=\"0\"><brandlist count=\"0\" ver=\"640356091\"></brandlist></msg>"  请求添加好友微信号的基本信息，可用于添加好友
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "CreateTime": 1705045979,  消息发送时间
        "MsgSource": "<msgsource>\n\t<signature>v1_GOrHWRNL</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 1109510141823131559,   消息ID
        "MsgSeq": 640356166
    }
}
"""


class FriendRequestNotificationHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        from_user = msg_data.get('FromUserName', {}).get('string')
        to_user = msg_data.get('ToUserName', {}).get('string')
        content = msg_data.get('Content', {}).get('string')
        msg_type = msg_data.get('MsgType')
        create_time = msg_data.get('CreateTime', 0)

        # 创建好友请求通知对象
        # 创建包含好友请求信息的字典
        message = {
            "TypeName": type_name,  # 消息类型
            "Appid": appid,        # 设备ID
            "Wxid": wxid,          # 所属微信的wxid
            "MsgId": msg_id,       # 消息ID
            "FromUser": from_user, # 发送人wxid
            "ToUser": to_user,     # 接收人wxid
            "Content": content,     # 消息内容
            "MsgType": msg_type,   # 消息类型
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取好友请求信息
        if content:
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(content)
                message['friend_request'] = {
                    'from_username': root.get('fromusername'),
                    'encrypt_username': root.get('encryptusername'),
                    'from_nickname': root.get('fromnickname'),
                    'verify_content': root.get('content'),
                    'ticket': root.get('ticket'),
                    'scene': root.get('scene'),
                    'country': root.get('country'),
                    'province': root.get('province'),
                    'city': root.get('city'),
                    'sex': root.get('sex'),
                    'avatar_url': root.get('bigheadimgurl')
                }
            except Exception:
                pass
        
        return message

    def handle(self, message):
        # 处理好友请求通知的业务逻辑
        return {
            'success': True,
            'message': '好友请求通知已处理',
            'data': message
        }