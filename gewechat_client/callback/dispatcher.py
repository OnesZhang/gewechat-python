import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

from .handlers.callback_test_message import CallbackTestMessageHandler
from .handlers.msg_text_message import TextMessageHandler
from .handlers.msg_image_message import ImageMessageHandler
from .handlers.msg_voice_message import VoiceMessageHandler
from .handlers.msg_video_message import VideoMessageHandler
from .handlers.msg_emoji_message import EmojiMessageHandler
from .handlers.msg_file_send_complete_message import FileSendCompleteMessageHandler
from .handlers.msg_file_send_notification_message import FileSendNotificationMessageHandler
from .handlers.msg_mini_program_message import MiniProgramMessageHandler
from .handlers.msg_revoke_message import RevokeMessageHandler
from .handlers.msg_pat_message import PatMessageHandler
from .handlers.msg_official_account_link_message import OfficialAccountLinkMessageHandler
from .handlers.msg_contact_card_message import ContactCardMessageHandler
from .handlers.msg_location_message import LocationMessageHandler
from .handlers.msg_quoted_message import QuotedMessageHandler
from .handlers.msg_transfer_message import TransferMessageHandler
from .handlers.msg_red_packet_message import RedPacketMessageHandler
from .handlers.msg_video_channel_message import VideoChannelMessageHandler
from .handlers.notify_friend_request_notification import FriendRequestNotificationHandler
from .handlers.notify_friend_verification_and_profile_change import FriendVerificationAndProfileChangeHandler
from .handlers.notify_friend_deleted_notification import FriendDeletedNotificationHandler
from .handlers.group_invitation_message import GroupInvitationMessageHandler
from .handlers.group_removed_from_group_notification import RemovedFromGroupNotificationHandler
from .handlers.group_kicked_from_group_notification import KickedFromGroupNotificationHandler
from .handlers.group_disband_notification import GroupDisbandNotificationHandler
from .handlers.group_name_change_notification import GroupNameChangeNotificationHandler
from .handlers.group_owner_change_notification import GroupOwnerChangeNotificationHandler
from .handlers.group_info_change_notification import GroupInfoChangeNotificationHandler
from .handlers.group_announcement_notification import GroupAnnouncementNotificationHandler
from .handlers.group_todo_notification import GroupTodoNotificationHandler
from .handlers.group_exit_notification import GroupExitNotificationHandler
from .handlers.sys_offline_notification import OfflineNotificationHandler
from ..util.logger import logger

class Dispatcher:
    def __init__(self):
        # 初始化各类消息处理器
        self.handlers = {
            # 常规消息
            'msg_text': TextMessageHandler(),
            'msg_image': ImageMessageHandler(),
            'msg_voice': VoiceMessageHandler(),
            'msg_video': VideoMessageHandler(),
            'msg_emoji': EmojiMessageHandler(),
            'msg_file_send_notification': FileSendNotificationMessageHandler(),
            'msg_file_send_complete': FileSendCompleteMessageHandler(),
            'msg_mini_program': MiniProgramMessageHandler(),
            'msg_official_account_link': OfficialAccountLinkMessageHandler(),
            'msg_contact_card': ContactCardMessageHandler(),
            'msg_location': LocationMessageHandler(),
            'msg_quoted': QuotedMessageHandler(),
            'msg_transfer': TransferMessageHandler(),
            'msg_red_packet': RedPacketMessageHandler(),
            'msg_video_channel': VideoChannelMessageHandler(),
            
            # 互动通知
            'notify_friend_request': FriendRequestNotificationHandler(),
            'notify_friend_verification': FriendVerificationAndProfileChangeHandler(),
            'notify_friend_deleted': FriendDeletedNotificationHandler(),
            'msg_revoke': RevokeMessageHandler(),
            'msg_pat': PatMessageHandler(),
            
            # 群相关通知
            'group_invitation': GroupInvitationMessageHandler(),
            'group_removed': RemovedFromGroupNotificationHandler(),
            'group_kicked': KickedFromGroupNotificationHandler(),
            'group_disband': GroupDisbandNotificationHandler(),
            'group_name_change': GroupNameChangeNotificationHandler(),
            'group_owner_change': GroupOwnerChangeNotificationHandler(),
            'group_info_change': GroupInfoChangeNotificationHandler(),
            'group_announcement': GroupAnnouncementNotificationHandler(),
            'group_todo': GroupTodoNotificationHandler(),
            'group_exit': GroupExitNotificationHandler(),
            
            # 系统消息
            'sys_offline': OfflineNotificationHandler(),
            
            # 回调测试消息
            'callback_test': CallbackTestMessageHandler()
        }

    def dispatch(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 记录接收到的消息基本信息
            type_name = message.get('TypeName')
            appid = message.get('Appid')
            wxid = message.get('Wxid')
            logger.info(f"收到新消息 - 类型: {type_name}, AppID: {appid}, WXID: {wxid}")
            
            # 判断是否为自己发送的消息
            data = message.get('Data', {})
            from_user = data.get('FromUserName', {}).get('string', '')
            if from_user == wxid:
                logger.info(f"忽略自己发送的消息")
                return {
                    'type_name': type_name,
                    'appid': appid,
                    'wxid': wxid,
                    'message': '忽略自己发送的消息'
                }
            
            # 解析消息类型
            msg_type = self.determine_message_type(message)
            handler = self.handlers.get(msg_type)
            
            if handler:
                # 使用对应的处理器处理消息
                handler_name = handler.__class__.__name__
                logger.info(f"使用 [{handler_name}] 解析 [{msg_type}] 类型消息")
                parsed_message = handler.parse(message)
                logger.info(f"消息解析完成: {parsed_message}")
                return handler.handle(parsed_message)
            else:
                # 未找到对应的处理器
                logger.warning(f"未找到消息类型处理器 - 类型: [{msg_type}]")
                return {
                    'type_name': type_name,
                    'appid': appid,
                    'wxid': message.get('Wxid'),
                    'message': '未知消息类型'
                }
        except Exception as e:
            # 记录错误信息
            logger.error(f"消息处理异常: {str(e)}", exc_info=True)
            return {
                'type_name': message.get('TypeName'),
                'appid': message.get('Appid'),
                'wxid': message.get('Wxid'),
                'message': f'消息处理出错: {str(e)}'
            }

    def determine_message_type(self, message):
        type_name = message.get('TypeName')
        data = message.get('Data', {})
        msg_type = data.get('MsgType')
        content = data.get('Content', {}).get('string', '')
        
        # 根据TypeName、MsgType和Content内容判断消息类型
        if type_name == 'AddMsg':
            if msg_type == 1:
                return 'msg_text'
            elif msg_type == 3:
                return 'msg_image'
            elif msg_type == 34:
                return 'msg_voice'
            elif msg_type == 43:
                return 'msg_video'
            elif msg_type == 47:
                return 'msg_emoji'
            elif msg_type == 42:
                return 'msg_contact_card'
            elif msg_type == 48:
                return 'msg_location'
            elif msg_type == 49:
                # 解析复杂消息类型
                if '<appmsg' in content:
                    try:
                        root = ET.fromstring(content)
                        appmsg = root.find('appmsg')
                        if appmsg is not None:
                            appmsg_type = appmsg.find('type')
                            if appmsg_type is not None:
                                appmsg_type = appmsg_type.text
                                if appmsg_type == '5':
                                    return 'msg_official_account_link'
                                elif appmsg_type == '74':
                                    return 'msg_file_send_notification'
                                elif appmsg_type == '6':
                                    return 'msg_file_send_complete'
                                elif appmsg_type in ['33', '36']:
                                    return 'msg_mini_program'
                                elif appmsg_type == '57':
                                    return 'msg_quoted'
                                elif appmsg_type == '2000':
                                    return 'msg_transfer'
                                elif appmsg_type == '2001':
                                    return 'msg_red_packet'
                                elif appmsg_type == '51':
                                    return 'msg_video_channel'
                    except Exception:
                        pass
                    
                    # 检查是否为群聊邀请
                    if '邀请你加入群聊' in content:
                        return 'group_invitation'
            elif msg_type == 37:
                if '验证请求' in content:
                    return 'notify_friend_request'
                else:
                    return 'notify_friend_verification'
            elif msg_type == 10000:
                if '你被' in content and '移出群聊' in content:
                    return 'group_removed'
                elif '群名' in content:
                    return 'group_name_change'
                elif '群主' in content:
                    return 'group_owner_change'
            elif msg_type == 10002:
                if '<sysmsg type="revokemsg">' in content:
                    return 'msg_revoke'
                elif '<sysmsg type="pat">' in content:
                    return 'msg_pat'
                elif '<sysmsg type="sysmsgtemplate">' in content:
                    if '移出了群聊' in content:
                        return 'group_kicked'
                    elif '解散' in content:
                        return 'group_disband'
                elif '<sysmsg type="mmchatroombarannouncememt">' in content:
                    return 'group_announcement'
                elif '<sysmsg type="roomtoolstips">' in content:
                    return 'group_todo'
        elif type_name == 'ModContacts':
            return 'group_info_change'
        elif type_name == 'DelContacts':
            # 判断是删除好友还是退出群聊
            # 这里需要根据实际情况进一步判断
            if 'ChatRoom' in content:
                return 'group_exit'
            else:
                return 'notify_friend_deleted'
        elif type_name == 'Offline':
            return 'sys_offline'
        elif 'testMsg' in message and 'token' in message:
            return 'callback_test'
            
        return 'unknown'