"""
回调消息常量定义
"""

# TypeName 常量
TYPE_ADD_MSG = 'AddMsg'  # 新消息
TYPE_MOD_CONTACTS = 'ModContacts'  # 联系人/群信息变更
TYPE_DEL_CONTACTS = 'DelContacts'  # 联系人删除/退出群聊
TYPE_OFFLINE = 'Offline'  # 掉线通知

# MsgType 常量
MSG_TYPE_TEXT = 1  # 文本消息
MSG_TYPE_IMAGE = 3  # 图片消息
MSG_TYPE_VOICE = 34  # 语音消息
MSG_TYPE_VERIFY = 37  # 好友验证消息
MSG_TYPE_CARD = 42  # 名片消息
MSG_TYPE_VIDEO = 43  # 视频消息
MSG_TYPE_MICROVIDEO = 62  # 微视频消息
MSG_TYPE_EMOJI = 47  # 表情消息
MSG_TYPE_LOCATION = 48  # 位置消息
MSG_TYPE_APP = 49  # 应用消息类型
MSG_TYPE_SYSTEM = 10000  # 系统消息
MSG_TYPE_SYSTEM_NOTIFY = 10002  # 系统通知
MSG_TYPE_SYSTEM_TEMPLATE = 10002  # 系统模板消息
MSG_TYPE_TODO = 10002  # 群待办消息类型
MSG_TYPE_EXIT_GROUP = 10004  # 退出群聊消息类型
MSG_TYPE_OFFLINE = 10005  # 掉线通知消息类型

# APP消息子类型 (msg.appmsg.type)
APP_MSG_TYPE_TEXT = 1  # 文本消息
APP_MSG_TYPE_IMG = 2  # 图片消息
APP_MSG_TYPE_AUDIO = 3  # 音频消息
APP_MSG_TYPE_VIDEO = 4  # 视频消息
APP_MSG_TYPE_URL = 5  # URL链接（同 APP_MSG_TYPE_LINK）
APP_MSG_TYPE_FILE = 6  # 文件发送完成
APP_MSG_TYPE_EMOJI = 8  # 表情消息
APP_MSG_TYPE_MINI_PROGRAM = 33  # 小程序消息类型1
APP_MSG_TYPE_FRIEND_VERIFY = 36  # 好友通过验证消息（同 APP_MSG_TYPE_MINI_PROGRAM_2）
APP_MSG_TYPE_QUOTE = 57  # 引用消息
APP_MSG_TYPE_FILE_NOTIFY = 74  # 文件发送通知
APP_MSG_TYPE_TRANSFER = 2000  # 转账消息
APP_MSG_TYPE_RED_PACKET = 2001  # 红包消息
APP_MSG_TYPE_CHANNELS = 51  # 视频号消息
APP_MSG_TYPE_GROUP_INVITE = 5  # 群聊邀请消息子类型

# 系统消息子类型 (sysmsg.type)
SYSMSG_TYPE_REVOKE = 'revokemsg'  # 撤回消息
SYSMSG_TYPE_PAT = 'pat'  # 拍一拍消息
SYSMSG_TYPE_TEMPLATE = 'sysmsgtemplate'  # 系统消息模板
SYSMSG_TYPE_ANNOUNCEMENT = 'mmchatroombarannouncememt'  # 群公告
SYSMSG_TYPE_ROOM_TOOLS = 'roomtoolstips'  # 群待办

# 特殊文本标识
TEXT_GROUP_INVITE = '邀请你加入群聊'  # 群聊邀请
TEXT_REMOVED_FROM_GROUP = '你被'  # 被移出群聊
TEXT_KICK_FROM_GROUP = '移出了群聊'  # 踢出群聊
TEXT_GROUP_DISMISSED = '解散'  # 解散群聊
TEXT_GROUP_NAME = '群名'  # 修改群名称
TEXT_GROUP_OWNER = '群主'  # 更换群主
TEXT_KICK_FROM_GROUP_TEMPLATE = '你将"$kickoutname$"移出了群聊'  # 踢出群聊模板
TEXT_GROUP_NAME_CHANGE = '你修改群名为'  # 修改群名称的文本标识
TEXT_GROUP_OWNER_CHANGE = '你已成为新群主'  # 更换群主的文本标识

# 系统消息模板类型
TEMPLATE_TYPE_PROFILE = 'tmpl_type_profile'  # 个人资料模板
TEMPLATE_TYPE_SUCCEED_CONTACT = 'new_tmpl_type_succeed_contact'  # 联系人成功模板

# 系统消息文本
TEXT_GROUP_DISMISS_TEMPLATE = '群主"$identity$"已解散该群聊'  # 解散群聊模板

# XML消息类型
XML_TYPE_CHATROOM_ANNOUNCEMENT = 'mmchatroombarannouncememt'  # 群公告 