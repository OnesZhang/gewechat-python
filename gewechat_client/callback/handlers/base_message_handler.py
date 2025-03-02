from typing import Dict, Any, Optional
import xml.etree.ElementTree as ET

class BaseMessageHandler:
    def get_base_info(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """获取消息的基础信息，包括群聊判断和实际发送者"""
        msg_data = message.get('Data', {})
        from_user = msg_data.get('FromUserName', {}).get('string')
        to_user = msg_data.get('ToUserName', {}).get('string')
        content = msg_data.get('Content', {}).get('string', '')

        # 判断是否为群消息
        is_group = self.is_group_message(from_user)
        
        # 解析群消息发送者
        actual_sender = None
        if is_group and content:
            actual_sender, _ = self.parse_group_message(content)
        else:
            actual_sender = from_user  # 非群聊时，实际发送人就是from_user

        return {
            "FromUser": from_user,     # 发送者ID（群消息时为群ID）
            "ToUser": to_user,         # 接收者ID
            "IsGroup": is_group,       # 是否群消息
            "ActualSender": actual_sender,  # 群消息的实际发送者
        }

    @staticmethod
    def is_group_message(from_user: str) -> bool:
        """判断是否为群消息"""
        return from_user and from_user.endswith('@chatroom')

    @staticmethod
    def parse_group_message(content: str) -> tuple[Optional[str], str]:
        """解析群消息，返回发送者ID和实际内容"""
        if not content or ':' not in content:
            return None, content
        try:
            sender, content = content.split(':', 1)
            return sender.strip(), content.strip()
        except Exception:
            return None, content

    @staticmethod
    def parse_msg_source(msg_source: str) -> Optional[Dict[str, Any]]:
        """解析消息源数据"""
        try:
            root = ET.fromstring(msg_source)
            source_info = {}
            
            # 解析成员数量（群消息特有）
            membercount = root.find('.//membercount')
            if membercount is not None and membercount.text:
                source_info['MemberCount'] = int(membercount.text)
            
            # 解析其他可能的信息
            silence = root.find('.//silence')
            if silence is not None and silence.text:
                source_info['Silence'] = int(silence.text)
                
            return source_info if source_info else None
        except Exception:
            return None

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理消息的基础方法，子类可以重写此方法"""
        return {
            'success': True,
            'message': '消息已处理',
            'data': message
        } 