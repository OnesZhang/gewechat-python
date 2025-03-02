# 好友通过验证及好友资料变更通知处理模块


# 好友通过验证及好友资料变更的通知消息示例
"""
{
    "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",
    "TypeName": "ModContacts",
    "Data":
    {
        "UserName":
        {
            "string": "wxid_0xsqb3o0tsvz22"
        },
        "NickName":
        {
            "string": "chaoxi。"
        },
        "PyInitial":
        {
            "string": "CX"
        },
        "QuanPin":
        {
            "string": "chaoxi"
        },
        "Sex": 1,
        "ImgBuf":
        {
            "iLen": 0
        },
        "BitMask": 4294967295,
        "BitVal": 3,
        "ImgFlag": 1,
        "Remark":
        {},
        "RemarkPyinitial":
        {},
        "RemarkQuanPin":
        {},
        "ContactType": 0,
        "RoomInfoCount": 0,
        "DomainList": [
        {}],
        "ChatRoomNotify": 0,
        "AddContactScene": 0,
        "Province": "Jiangsu",
        "City": "Nanjing",
        "Signature": "......",
        "PersonalCard": 0,
        "HasWeiXinHdHeadImg": 1,
        "VerifyFlag": 0,
        "Level": 6,
        "Source": 14,
        "WeiboFlag": 0,
        "AlbumStyle": 0,
        "AlbumFlag": 3,
        "SnsUserInfo":
        {
            "SnsFlag": 1,
            "SnsBgimgId": "http://shmmsns.qpic.cn/mmsns/FzeKA69P5uIdqPfQxp59LvOohoE2iaiaj86IBH1jl0F76aGvg8AlU7giaMtBhQ3bPibunbhVLb3aEq4/0",
            "SnsBgobjectId": 14216284872728580667,
            "SnsFlagEx": 7297
        },
        "Country": "CN",
        "BigHeadImgUrl": "https://wx.qlogo.cn/mmhead/ver_1/qqncCu2avRYruPcQbav3PrwaGSS31QgN6dqW8q1XuDKjgiaAuwoFPw3kN8Cj3zIBL36M93R2Xwib0IddUK3gqbFeezEiaA8K2mMdibT5VUDDrbn7F7M1Mxicmows9cdYNOicjI/0",
        "SmallHeadImgUrl": "https://wx.qlogo.cn/mmhead/ver_1/qqncCu2avRYruPcQbav3PrwaGSS31QgN6dqW8q1XuDKjgiaAuwoFPw3kN8Cj3zIBL36M93R2Xwib0IddUK3gqbFeezEiaA8K2mMdibT5VUDDrbn7F7M1Mxicmows9cdYNOicjI/132",
        "CustomizedInfo":
        {
            "BrandFlag": 0
        },
        "EncryptUserName": "v3_020b3826fd03010000000000feba078fc1e760000000501ea9a3dba12f95f6b60a0536a1adb6f6352c38d0916c9c74045d85aa602efa2d81b84adde05d285124e8a54b9fcd039f725d6ac0d3bd651c7c74503a@stranger",
        "AdditionalContactList":
        {
            "LinkedinContactItem":
            {}
        },
        "ChatroomMaxCount": 0,
        "DeleteFlag": 0,
        "Description": "\b\u0000\u0018\u0000\"\u0000(\u00008\u0000",
        "ChatroomStatus": 0,
        "Extflag": 0,
        "ChatRoomBusinessType": 0
    }
}
"""

from datetime import datetime

class FriendVerificationAndProfileChangeHandler:
    def parse(self, message):
        # 从回调数据中提取基本信息
        type_name = message.get('TypeName')
        appid = message.get('Appid')
        wxid = message.get('Wxid')
        
        # 提取Data中的信息
        msg_data = message.get('Data', {})
        user_name = msg_data.get('UserName', {}).get('string')
        nick_name = msg_data.get('NickName', {}).get('string')
        sex = msg_data.get('Sex')
        province = msg_data.get('Province')
        city = msg_data.get('City')
        country = msg_data.get('Country')
        signature = msg_data.get('Signature')
        big_head_img_url = msg_data.get('BigHeadImgUrl')
        small_head_img_url = msg_data.get('SmallHeadImgUrl')
        contact_type = msg_data.get('ContactType')
        verify_flag = msg_data.get('VerifyFlag')
        
        # 创建好友资料变更通知对象
        # 创建好友资料变更通知对象
        message = {
            "TypeName": type_name,      # 类型名称
            "Appid": appid,            # 应用ID
            "Wxid": wxid,              # 微信ID
            "UserName": user_name,      # 用户名
            "NickName": nick_name,      # 昵称
            "Sex": sex,                # 性别
            "Province": province,       # 省份
            "City": city,              # 城市
            "Country": country,         # 国家
            "Signature": signature,     # 签名
            "BigHeadImgUrl": big_head_img_url,  # 大头像URL
            "SmallHeadImgUrl": small_head_img_url,  # 小头像URL
            "ContactType": contact_type,  # 联系人类型
            "VerifyFlag": verify_flag    # 验证标志
        }
        
        return message
    def handle(self, message):
        # 处理好友通过验证及好友资料变更的通知逻辑
        return {
            'success': True,
            'message': '好友资料变更通知已处理',
            'data': message
        }