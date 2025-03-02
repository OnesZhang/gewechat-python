# 视频号消息处理模块
from typing import Dict, Any
from .base_message_handler import BaseMessageHandler
import xml.etree.ElementTree as ET


# 视频号消息
"""
 {
     "TypeName": "AddMsg",   消息类型
     "Appid": "wx_wR_U4zPj2M_OTS3BCyoE4",  设备ID
     "Wxid": "wxid_phyyedw9xap22",  所属微信的wxid
     "Data":
     {
         "MsgId": 1040356115,    消息ID
         "FromUserName":
         {
             "string": "wxid_phyyedw9xap22"    消息发送人的wxid
         },
         "ToUserName":
         {
             "string": "wxid_0xsqb3o0tsvz22"  消息接收人的wxid
         },
         "MsgType": 49,
         "Content":
         {
             "string": "<?xml version=\"1.0\"?>\n<msg>\n\t<appmsg appid=\"\" sdkver=\"0\">\n\t\t<title>当前微信版本不支持展示该内容，请升级至最新版本。</title>\n\t\t<des />\n\t\t<action />\n\t\t<type>51</type>\n\t\t<showtype>0</showtype>\n\t\t<soundtype>0</soundtype>\n\t\t<mediatagname />\n\t\t<messageext />\n\t\t<messageaction />\n\t\t<content />\n\t\t<contentattr>0</contentattr>\n\t\t<url>https://support.weixin.qq.com/update/</url>\n\t\t<lowurl />\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<appattach>\n\t\t\t<totallen>0</totallen>\n\t\t\t<attachid />\n\t\t\t<emoticonmd5 />\n\t\t\t<fileext />\n\t\t\t<aeskey />\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<sourceusername />\n\t\t<sourcedisplayname />\n\t\t<thumburl />\n\t\t<md5 />\n\t\t<statextstr />\n\t\t<finderFeed>\n\t\t\t<objectId>14264358459626428566</objectId>\n\t\t\t<feedType>4</feedType>\n\t\t\t<nickname>国风锦鲤</nickname>\n\t\t\t<avatar>https://wx.qlogo.cn/finderhead/ver_1/x2LxetmLmgoo9jp69R3wcrtZ0LBLdjVv9vrK9HmPNGEdD1iawdrPffPvMmFUez8pWqRIfs7DtgPiaV5C7DZpibH8b3y0jG178aIict6uPf0Vht4/0</avatar>\n\t\t\t<desc>还招人么？我不要工资#逆水寒cos</desc>\n\t\t\t<mediaCount>1</mediaCount>\n\t\t\t<objectNonceId>8046877030770906689_0_0_0_0_0</objectNonceId>\n\t\t\t<liveId>0</liveId>\n\t\t\t<username>v2_060000231003b20faec8cae08b19c7d2c702e834b077fb74f482543ff67f0cc66363057a5443@finder</username>\n\t\t\t<webUrl />\n\t\t\t<authIconType>0</authIconType>\n\t\t\t<authIconUrl />\n\t\t\t<bizNickname />\n\t\t\t<bizAvatar />\n\t\t\t<bizUsernameV2 />\n\t\t\t<mediaList>\n\t\t\t\t<media>\n\t\t\t\t\t<mediaType>4</mediaType>\n\t\t\t\t\t<url>http://wxapp.tc.qq.com/251/20302/stodownload?encfilekey=Cvvj5Ix3eez3Y79SxtvVL0L7CkPM6dFibFeI6caGYwFFDAZJzcvicKz3jic4UfNeiaWTwH9gTlYiafAxVkMZRXicBUBk2Ms7lauAj6SArUu0P9ddKiaa8IWZzYaaKLf1WddH4G8T0KicxQV3hQPH3pQgEMTscw&amp;a=1&amp;bizid=1023&amp;dotrans=0&amp;hy=SH&amp;idx=1&amp;m=4c4c7f3ed03a14a6b99d0d19176c12ac&amp;upid=290110</url>\n\t\t\t\t\t<thumbUrl>http://wxapp.tc.qq.com/251/20304/stodownload?encfilekey=oibeqyX228riaCwo9STVsGLPj9UYCicgttvO59vjtcQ7Jviaia0q4bnpVP2ia7ibqzacPo0z4nIRtWom80ZXwL64icZO2q6ibVBQLZQftMwU3SHj5uplsIFroHeF0QNcCkXX3RtibaWCHJQjfqZUk&amp;bizid=1023&amp;dotrans=0&amp;hy=SH&amp;idx=1&amp;m=7522250b4d15e5df866bf23da9f117d6&amp;token=oA9SZ4icv8IssuhLtacX13nAzXiaf8y52juKW4ibUDN7a2vn71bbrCR0LZiabddvTsLLMvnELnuAwNxViclRT7wT9IyibzFw1pq9wdichRYaEmb6Js&amp;ctsc=2-20</thumbUrl>\n\t\t\t\t\t<width>1080</width>\n\t\t\t\t\t<height>1920</height>\n\t\t\t\t\t<coverUrl>http://wxapp.tc.qq.com/251/20304/stodownload?encfilekey=oibeqyX228riaCwo9STVsGLPj9UYCicgttvO59vjtcQ7Jviaia0q4bnpVP2ia7ibqzacPo0z4nIRtWom80ZXwL64icZO2q6ibVBQLZQftMwU3SHj5uplsIFroHeF0QNcCkXX3RtibaWCHJQjfqZUk&amp;bizid=1023&amp;dotrans=0&amp;hy=SH&amp;idx=1&amp;m=7522250b4d15e5df866bf23da9f117d6&amp;token=oA9SZ4icv8IssuhLtacX13nAzXiaf8y52juKW4ibUDN7a2vn71bbrCR0LZiabddvTsLLMvnELnuAwNxViclRT7wT9IyibzFw1pq9wdichRYaEmb6Js&amp;ctsc=2-20</coverUrl>\n\t\t\t\t\t<fullCoverUrl>http://wxapp.tc.qq.com/251/20350/stodownload?encfilekey=oibeqyX228riaCwo9STVsGLPj9UYCicgttv1FCQXwResqN75zI4n65zY5tkAficEPWbbClq2VcicqMYaSLK7nrAVMasrIhvsCXJib5cOLib98JgWPr4SP92W6YEkVN5Uv0TKAdyRryQ3Qxk7jU&amp;bizid=1023&amp;dotrans=0&amp;hy=SH&amp;idx=1&amp;m=731b89683dd3cb866cdf96dab70ac183&amp;token=KkOFht0mCXlnmicFbJnvymIJOEfZgzia8PY0ZzOdaIYTJXwfblvK4U1ibntribm1beupHwictGWs9hpMiclyhfSb6766Lnb3ib0j14bENm6u1tHpeo&amp;ctsc=3-20</fullCoverUrl>\n\t\t\t\t\t<videoPlayDuration>10&gt;&gt;</videoPlayDuration>\n\t\t\t\t</media>\n\t\t\t</mediaList>\n\t\t</finderFeed>\n\t</appmsg>\n\t<fromusername>wxid_phyyedw9xap22</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>1</version>\n\t\t<appname></appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>\n"
         },
         "Status": 3,
         "ImgStatus": 1,
         "ImgBuf":
         {
             "iLen": 0
         },
         "CreateTime": 1705045057,  消息发送时间
         "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n\t<alnode>\n\t\t<fr>4</fr>\n\t</alnode>\n\t<sec_msg_node>\n\t\t<uuid>bb2cbd9d3290e7a3d35f183eaade2213_</uuid>\n\t</sec_msg_node>\n\t<signature>v1_+Tfo41HS</signature>\n</msgsource>\n",
         "PushContent": "你收到了一条消息",   消息通知内容
         "NewMsgId": 5576224237104747184,   消息ID
         "MsgSeq": 640356115
     }
 }
"""
class VideoChannelMessageHandler(BaseMessageHandler):
    def parse(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 获取基础信息（群聊相关）
        base_info = self.get_base_info(message)
        
        # 从回调数据中提取消息特定信息
        msg_data = message.get('Data', {})
        msg_id = msg_data.get('MsgId')
        content = msg_data.get('Content', {}).get('string')
        create_time = msg_data.get('CreateTime', 0)

        # 创建视频号消息对象
        message = {
            **base_info,  # 包含 FromUser、ToUser、IsGroup、ActualSender
            "MsgId": msg_id,       # 消息ID
            "Content": content,     # 消息内容
            "CreateTime": create_time  # 消息发送时间
        }
        
        # 解析XML内容获取视频号信息
        if content and '<finderFeed>' in content:
            try:
                root = ET.fromstring(content)
                finder_feed = root.find('.//finderFeed')
                if finder_feed is not None:
                    # 提取视频号信息
                    message['finder_info'] = {
                        'object_id': finder_feed.find('objectId').text if finder_feed.find('objectId') is not None else None,
                        'feed_type': finder_feed.find('feedType').text if finder_feed.find('feedType') is not None else None,
                        'nickname': finder_feed.find('nickname').text if finder_feed.find('nickname') is not None else None,
                        'avatar': finder_feed.find('avatar').text if finder_feed.find('avatar') is not None else None,
                        'desc': finder_feed.find('desc').text if finder_feed.find('desc') is not None else None,
                        'username': finder_feed.find('username').text if finder_feed.find('username') is not None else None
                    }
                    
                    # 提取媒体信息
                    media_list = finder_feed.find('mediaList')
                    if media_list is not None and media_list.find('media') is not None:
                        media = media_list.find('media')
                        message['video_url'] = media.find('url').text if media.find('url') is not None else None
                        message['video_thumb_url'] = media.find('thumbUrl').text if media.find('thumbUrl') is not None else None
            except Exception as e:
                print(f"解析视频号消息XML出错: {e}")
        
        return message

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # 处理视频号消息的业务逻辑
        return {
            'success': True,
            'message': '视频号消息已处理',
            'data': message
        }