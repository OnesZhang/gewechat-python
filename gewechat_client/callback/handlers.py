"""
消息处理器

负责解析和处理回调消息
"""

import xml.etree.ElementTree as ET
import re
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from .constants import *
from .models import Message, TextContent, ImageContent, VideoContent
from .models import VoiceContent, LocationContent, LinkContent, ContactCardContent
from .models import FileNotifyContent, FileContent, ContactInfo, FriendPassVerifyContent, MiniProgramContent, QuoteContent, RedPacketContent, RevokeContent, PatContent, TodoContent, OfflineContent

class MessageHandler:
    """消息处理器"""
    
    def parse_message(self, data: Dict[str, Any]) -> Optional[Message]:
        """解析消息数据
        
        Args:
            data: 原始消息数据
            
        Returns:
            解析后的消息对象
        """
        try:
            msg_data = data.get('Data', {})
            
            # 基础消息信息
            base_msg = {
                'type_name': data.get('TypeName'),
                'appid': data.get('Appid'),
                'wxid': data.get('Wxid'),
                'raw_data': data,
                'msg_id': msg_data.get('MsgId'),
                'from_user': msg_data.get('FromUserName', {}).get('string'),
                'to_user': msg_data.get('ToUserName', {}).get('string'),
                'msg_type': msg_data.get('MsgType'),
                'create_time': datetime.fromtimestamp(msg_data.get('CreateTime', 0)),
                'content': self._parse_content(msg_data)
            }
            
            return Message(**base_msg)
            
        except Exception as e:
            print(f"解析消息失败: {e}")
            return None
    
    def _parse_xml_content(self, xml_content: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """解析XML内容
        
        Args:
            xml_content: XML字符串
            
        Returns:
            (appmsg_dict, sysmsg_dict): 应用消息字典和系统消息字典
        """
        try:
            root = ET.fromstring(xml_content)
            
            # 解析appmsg
            appmsg = root.find('.//appmsg')
            appmsg_dict = None
            if appmsg is not None:
                appmsg_dict = {
                    'type': int(appmsg.find('type').text) if appmsg.find('type') is not None else None,
                    'title': appmsg.find('title').text if appmsg.find('title') is not None else None,
                    'url': appmsg.find('url').text if appmsg.find('url') is not None else None,
                    'thumburl': appmsg.find('thumburl').text if appmsg.find('thumburl') is not None else None,
                    'des': appmsg.find('des').text if appmsg.find('des') is not None else None
                }
            
            # 解析sysmsg
            sysmsg = root.find('.//sysmsg')
            sysmsg_dict = None
            if sysmsg is not None:
                sysmsg_dict = {
                    'type': sysmsg.get('type'),
                    'content': sysmsg.text if sysmsg.text else None
                }
            
            return appmsg_dict, sysmsg_dict
            
        except Exception as e:
            print(f"解析XML内容失败: {e}")
            return None, None
    
    def _parse_content(self, msg_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析消息内容
        
        Args:
            msg_data: 消息数据
            
        Returns:
            解析后的内容
        """
        msg_type = msg_data.get('MsgType')
        content = msg_data.get('Content', {}).get('string', '')
        
        # 解析系统通知消息
        if msg_type == MSG_TYPE_SYSTEM_NOTIFY and content.startswith('<sysmsg'):
            try:
                root = ET.fromstring(content)
                sysmsg = root.find('.//sysmsg')
                if sysmsg is not None:
                    sysmsg_type = sysmsg.get('type')
                    if sysmsg_type == SYSMSG_TYPE_REVOKE:
                        revoke = root.find('.//revokemsg')
                        if revoke is not None:
                            return {
                                'revoke': RevokeContent(
                                    session=revoke.find('session').text if revoke.find('session') is not None else '',
                                    msgid=revoke.find('msgid').text if revoke.find('msgid') is not None else '',
                                    newmsgid=revoke.find('newmsgid').text if revoke.find('newmsgid') is not None else '',
                                    replacemsg=revoke.find('replacemsg').text if revoke.find('replacemsg') is not None else ''
                                )
                            }
                    elif sysmsg_type == SYSMSG_TYPE_PAT:
                        pat = root.find('.//pat')
                        if pat is not None:
                            return {
                                'pat': PatContent(
                                    from_username=pat.find('fromusername').text if pat.find('fromusername') is not None else '',
                                    chat_username=pat.find('chatusername').text if pat.find('chatusername') is not None else '',
                                    patted_username=pat.find('pattedusername').text if pat.find('pattedusername') is not None else '',
                                    pat_suffix=pat.find('patsuffix').text if pat.find('patsuffix') is not None else '',
                                    pat_suffix_version=int(pat.find('patsuffixversion').text) if pat.find('patsuffixversion') is not None else 0,
                                    template=pat.find('template').text if pat.find('template') is not None else ''
                                )
                            }
            except Exception as e:
                print(f"解析系统通知消息失败: {e}")
                return None
        
        try:
            # 解析其他XML内容
            appmsg_dict = None
            xml_data = None
            if content.startswith('<?xml'):
                try:
                    root = ET.fromstring(content)
                    xml_data = {'msg': {}}
                    
                    # 解析图片信息
                    img = root.find('.//img')
                    if img is not None:
                        xml_data['msg']['img'] = {
                            'aeskey': img.get('aeskey'),
                            'encryver': img.get('encryver'),
                            'cdnthumbaeskey': img.get('cdnthumbaeskey'),
                            'cdnthumburl': img.get('cdnthumburl'),
                            'cdnthumblength': img.get('cdnthumblength'),
                            'cdnthumbheight': img.get('cdnthumbheight'),
                            'cdnthumbwidth': img.get('cdnthumbwidth'),
                            'cdnmidheight': img.get('cdnmidheight'),
                            'cdnmidwidth': img.get('cdnmidwidth'),
                            'cdnhdheight': img.get('cdnhdheight'),
                            'cdnhdwidth': img.get('cdnhdwidth'),
                            'cdnmidimgurl': img.get('cdnmidimgurl'),
                            'length': img.get('length'),
                            'md5': img.get('md5')
                        }
                    
                    # 解析appmsg
                    appmsg = root.find('.//appmsg')
                    if appmsg is not None:
                        appmsg_dict = {
                            'type': int(appmsg.find('type').text) if appmsg.find('type') is not None else None,
                            'title': appmsg.find('title').text if appmsg.find('title') is not None else None,
                            'url': appmsg.find('url').text if appmsg.find('url') is not None else None,
                            'thumburl': appmsg.find('thumburl').text if appmsg.find('thumburl') is not None else None,
                            'des': appmsg.find('des').text if appmsg.find('des') is not None else None
                        }
                except Exception as e:
                    print(f"解析XML内容失败: {e}")
            
            # 根据消息类型处理
            if msg_type == MSG_TYPE_TEXT:
                return {
                    'text': TextContent(
                        content=content,
                        push_content=msg_data.get('PushContent'),
                        msg_source=msg_data.get('MsgSource'),
                        msg_seq=msg_data.get('MsgSeq'),
                        status=msg_data.get('Status')
                    )
                }
                
            elif msg_type == MSG_TYPE_IMAGE:
                # 获取图片信息和缩略图
                img_data = xml_data['msg']['img'] if xml_data and 'msg' in xml_data and 'img' in xml_data['msg'] else {}
                thumb_data = msg_data.get('ImgBuf', {})
                
                # 构建图片内容
                result = {
                    'image': ImageContent(
                        image_url=img_data.get('cdnmidimgurl', ''),  # CDN URL
                        thumb_url=img_data.get('cdnthumburl', ''),  # 缩略图URL
                        aes_key=img_data.get('aeskey', ''),  # 解密密钥
                        thumb_aes_key=img_data.get('cdnthumbaeskey', ''),  # 缩略图解密密钥
                        file_length=int(img_data.get('length', 0)),  # 文件大小
                        thumb_length=int(img_data.get('cdnthumblength', 0)),  # 缩略图大小
                        thumb_width=int(img_data.get('cdnthumbwidth', 0)),  # 缩略图宽度
                        thumb_height=int(img_data.get('cdnthumbheight', 0)),  # 缩略图高度
                        md5=img_data.get('md5', ''),  # 文件MD5
                        thumb_buffer=thumb_data.get('buffer'),  # 缩略图base64数据
                        encryver=int(img_data.get('encryver', 0)),  # 加密版本
                        mid_width=int(img_data.get('cdnmidwidth', 0)),  # 中等尺寸图片宽度
                        mid_height=int(img_data.get('cdnmidheight', 0)),  # 中等尺寸图片高度
                        hd_width=int(img_data.get('cdnhdwidth', 0)),  # 高清图片宽度
                        hd_height=int(img_data.get('cdnhdheight', 0)),  # 高清图片高度
                        mid_image_url=img_data.get('cdnmidimgurl', '')  # 中等尺寸图片URL
                    ),
                    'xml_data': xml_data  # 原始XML数据，包含所有图片属性
                }
                return result
                
            elif msg_type == MSG_TYPE_VIDEO:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    video = root.find('.//videomsg')
                    if video is not None:
                        # 构建视频内容
                        result = {
                            'video': VideoContent(
                                video_url=video.get('cdnvideourl', ''),  # CDN URL
                                thumb_url=video.get('cdnthumburl', ''),  # 缩略图URL
                                aes_key=video.get('aeskey', ''),  # 解密密钥
                                thumb_aes_key=video.get('cdnthumbaeskey', ''),  # 缩略图解密密钥
                                file_length=int(video.get('length', 0)),  # 文件大小
                                play_length=int(video.get('playlength', 0)),  # 播放时长
                                thumb_length=int(video.get('cdnthumblength', 0)),  # 缩略图大小
                                thumb_width=int(video.get('cdnthumbwidth', 0)),  # 缩略图宽度
                                thumb_height=int(video.get('cdnthumbheight', 0)),  # 缩略图高度
                                md5=video.get('md5', ''),  # 文件MD5
                                new_md5=video.get('newmd5', ''),  # 新MD5
                                from_user=video.get('fromusername', ''),  # 发送者
                                is_placeholder=video.get('isplaceholder', '0') == '1',  # 是否占位
                                raw_md5=video.get('rawmd5', None),  # 原始MD5
                                raw_length=int(video.get('rawlength', 0)) or None,  # 原始大小
                                raw_video_url=video.get('cdnrawvideourl', None),  # 原始URL
                                raw_video_aes_key=video.get('cdnrawvideoaeskey', None),  # 原始解密密钥
                                origin_source_md5=video.get('originsourcemd5', None),  # 源MD5
                                is_ad=video.get('isad', '0') == '1'  # 是否广告
                            ),
                            'xml_data': {'msg': {'video': {k: v for k, v in video.attrib.items()}}},  # 原始XML数据
                        }
                        return result
                except Exception as e:
                    print(f"解析视频消息失败: {e}")
                    
                return {'video': VideoContent(
                    video_url='',
                    thumb_url='',
                    aes_key='',
                    thumb_aes_key='',
                    file_length=0,
                    play_length=0,
                    thumb_length=0,
                    thumb_width=0,
                    thumb_height=0,
                    md5='',
                    new_md5='',
                    from_user=''
                )}
                
            elif msg_type == MSG_TYPE_EMOJI:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    emoji = root.find('.//emoji')
                    if emoji is not None:
                        # 构建表情内容
                        result = {
                            'emoji': EmojiContent(
                                md5=emoji.get('md5', ''),  # 文件MD5
                                cdn_url=emoji.get('cdnurl', ''),  # CDN URL
                                aes_key=emoji.get('aeskey', ''),  # 解密密钥
                                file_length=int(emoji.get('len', 0)),  # 文件大小
                                width=int(emoji.get('width', 0)),  # 宽度
                                height=int(emoji.get('height', 0)),  # 高度
                                thumb_url=emoji.get('thumburl', ''),  # 缩略图URL
                                encrypt_url=emoji.get('encrypturl', ''),  # 加密URL
                                extern_url=emoji.get('externurl', ''),  # 外部URL
                                extern_md5=emoji.get('externmd5', ''),  # 外部MD5
                                type=emoji.get('type', '2'),  # 类型
                                product_id=emoji.get('productid', ''),  # 产品ID
                                attached_text=emoji.get('attachedtext', ''),  # 附加文本
                                attached_text_color=emoji.get('attachedtextcolor', ''),  # 附加文本颜色
                                lens_id=emoji.get('lensid', ''),  # 镜头ID
                                emoji_attr=emoji.get('emojiattr', ''),  # 表情属性
                                link_id=emoji.get('linkid', ''),  # 链接ID
                                desc=emoji.get('desc', '')  # 描述
                            ),
                            'xml_data': {'msg': {'emoji': {k: v for k, v in emoji.attrib.items()}}},  # 原始XML数据
                        }
                        return result
                except Exception as e:
                    print(f"解析表情消息失败: {e}")
                    
                return {'emoji': EmojiContent(
                    md5='',
                    cdn_url='',
                    aes_key='',
                    file_length=0,
                    width=0,
                    height=0
                )}
                
            elif msg_type == MSG_TYPE_VOICE:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    voice = root.find('.//voicemsg')
                    if voice is not None:
                        # 构建语音内容
                        result = {
                            'voice': VoiceContent(
                                voice_url=voice.get('voiceurl', ''),  # CDN URL
                                voice_length=int(voice.get('voicelength', 0)),  # 语音时长
                                aes_key=voice.get('aeskey', ''),  # 解密密钥
                                file_length=int(voice.get('length', 0)),  # 文件大小
                                voice_format=int(voice.get('voiceformat', 0)),  # 语音格式
                                md5=voice.get('voicemd5', '')  # 文件MD5
                            ),
                            'xml_data': {'msg': {'voice': {k: v for k, v in voice.attrib.items()}}},  # 原始XML数据
                        }
                        
                        # 添加语音文件的base64数据（如果有）
                        voice_buffer = msg_data.get('ImgBuf', {}).get('buffer')
                        if voice_buffer:
                            result['voice'].buffer = voice_buffer
                            
                        return result
                except Exception as e:
                    print(f"解析语音消息失败: {e}")
                    
                return {'voice': VoiceContent(
                    voice_url='',
                    voice_length=0,
                    aes_key='',
                    file_length=0,
                    voice_format=0
                )}
                
            elif msg_type == MSG_TYPE_LOCATION:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    location = root.find('.//location')
                    if location is not None:
                        return {
                            'location': LocationContent(
                                latitude=float(location.get('x', '0')),
                                longitude=float(location.get('y', '0')),
                                scale=int(location.get('scale', '0')),
                                label=location.get('label', ''),
                                maptype=location.get('maptype', ''),
                                poiname=location.get('poiname', ''),
                                poiid=location.get('poiid', ''),
                                building_id=location.get('buildingId', ''),
                                floor_name=location.get('floorName', ''),
                                poi_category_tips=location.get('poiCategoryTips', ''),
                                poi_business_hour=location.get('poiBusinessHour', ''),
                                poi_phone=location.get('poiPhone', ''),
                                poi_price_tips=location.get('poiPriceTips', ''),
                                is_from_poi_list=location.get('isFromPoiList', 'false').lower() == 'true',
                                adcode=location.get('adcode', ''),
                                cityname=location.get('cityname', '')
                            )
                        }
                except Exception as e:
                    print(f"解析地理位置消息失败: {e}")
                    return None
                
            elif msg_type == MSG_TYPE_APP:
                if not appmsg_dict:
                    try:
                        # 解析XML内容
                        root = ET.fromstring(content)
                        appmsg = root.find('.//appmsg')
                        if appmsg is not None:
                            # 获取基本信息
                            title = appmsg.find('title').text if appmsg.find('title') is not None else ''
                            type_elem = appmsg.find('type')
                            msg_type = int(type_elem.text) if type_elem is not None else 0
                            url = appmsg.find('url').text if appmsg.find('url') is not None else ''
                            
                            # 获取公众号信息
                            source_username = appmsg.find('sourceusername').text if appmsg.find('sourceusername') is not None else ''
                            source_displayname = appmsg.find('sourcedisplayname').text if appmsg.find('sourcedisplayname') is not None else ''
                            
                            # 获取缩略图信息
                            appattach = appmsg.find('appattach')
                            if appattach is not None:
                                thumb_url = appattach.find('cdnthumburl').text if appattach.find('cdnthumburl') is not None else ''
                                thumb_width = int(appattach.find('cdnthumbwidth').text) if appattach.find('cdnthumbwidth') is not None else 0
                                thumb_height = int(appattach.find('cdnthumbheight').text) if appattach.find('cdnthumbheight') is not None else 0
                                thumb_aes_key = appattach.find('cdnthumbaeskey').text if appattach.find('cdnthumbaeskey') is not None else ''
                                thumb_length = int(appattach.find('cdnthumblength').text) if appattach.find('cdnthumblength') is not None else 0
                                thumb_md5 = appattach.find('cdnthumbmd5').text if appattach.find('cdnthumbmd5') is not None else ''
                            else:
                                thumb_url = appmsg.find('thumburl').text if appmsg.find('thumburl') is not None else ''
                                thumb_width = 0
                                thumb_height = 0
                                thumb_aes_key = ''
                                thumb_length = 0
                                thumb_md5 = ''
                            
                            # 获取其他信息
                            des = appmsg.find('des').text if appmsg.find('des') is not None else ''
                            action = appmsg.find('action').text if appmsg.find('action') is not None else ''
                            app_id = appmsg.get('appid', '')
                            sdk_ver = appmsg.get('sdkver', '0')
                            show_type = int(appmsg.find('showtype').text) if appmsg.find('showtype') is not None else 0
                            sound_type = int(appmsg.find('soundtype').text) if appmsg.find('soundtype') is not None else 0
                            content_elem = appmsg.find('content')
                            content = content_elem.text if content_elem is not None and content_elem.text else ''
                            content_attr = int(appmsg.find('contentattr').text) if appmsg.find('contentattr') is not None else 0
                            
                            # 构建消息内容
                            appmsg_dict = {
                                'type': msg_type,
                                'title': title,
                                'url': url,
                                'source_username': source_username,
                                'source_displayname': source_displayname,
                                'thumb_url': thumb_url,
                                'thumb_width': thumb_width,
                                'thumb_height': thumb_height,
                                'thumb_aes_key': thumb_aes_key,
                                'thumb_length': thumb_length,
                                'thumb_md5': thumb_md5,
                                'des': des,
                                'action': action,
                                'app_id': app_id,
                                'sdk_ver': sdk_ver,
                                'show_type': show_type,
                                'sound_type': sound_type,
                                'content': content,
                                'content_attr': content_attr
                            }
                    except Exception as e:
                        print(f"解析应用消息失败: {e}")
                        return {'app': content}
                
                if not appmsg_dict:
                    return {'app': content}
                
                app_type = appmsg_dict.get('type')
                
                # 处理群聊邀请消息
                if app_type == APP_MSG_TYPE_GROUP_INVITE:
                    title = appmsg_dict.get('title', '')
                    if '邀请你加入群聊' in title:  # 根据标题判断是否为群聊邀请
                        description = appmsg_dict.get('des', '')
                        url = appmsg_dict.get('url', '')
                        thumb_url = appmsg_dict.get('thumb_url', '')
                        
                        # 从描述中提取邀请者和群名
                        inviter_username = ''
                        chat_name = ''
                        if description:
                            # 解析描述格式："xxx"邀请你加入群聊"xxx"，进入可查看详情。
                            parts = description.split('"')
                            if len(parts) >= 4:
                                inviter_username = parts[1].rstrip('。')
                                chat_name = parts[3]
                        
                        return {
                            'group_invite': GroupInviteContent(
                                title=title,
                                description=description,
                                url=url,
                                thumb_url=thumb_url or '',
                                inviter_username=inviter_username,
                                chat_name=chat_name
                            )
                        }
                
                # 公众号链接
                if app_type == APP_MSG_TYPE_LINK:
                    title = appmsg_dict.get('title', '')
                    if TEXT_GROUP_INVITE in title:
                        return {'group_invite': appmsg_dict}
                    return {'link': AppMessageContent(**appmsg_dict)}
                
                # 文件消息
                elif app_type in (APP_MSG_TYPE_FILE, APP_MSG_TYPE_FILE_NOTIFY):
                    try:
                        # 解析XML内容
                        root = ET.fromstring(content)
                        appmsg = root.find('.//appmsg')
                        if appmsg is not None:
                            # 获取基本信息
                            title = appmsg.find('title').text if appmsg.find('title') is not None else ''
                            appattach = appmsg.find('appattach')
                            
                            # 获取文件基本信息
                            total_len = int(appattach.find('totallen').text) if appattach.find('totallen') is not None else 0
                            file_ext = appattach.find('fileext').text if appattach.find('fileext') is not None else ''
                            file_upload_token = appattach.find('fileuploadtoken').text if appattach.find('fileuploadtoken') is not None else ''
                            md5 = appmsg.find('md5').text if appmsg.find('md5') is not None else ''
                            
                            # 获取发送者信息
                            from_user = root.find('.//fromusername')
                            from_user = from_user.text if from_user is not None else ''
                            
                            if app_type == APP_MSG_TYPE_FILE_NOTIFY:
                                # 文件发送通知消息
                                status = int(appattach.find('status').text) if appattach.find('status') is not None else 0
                                lan_info = appmsg.find('laninfo').text if appmsg.find('laninfo') is not None else ''
                                
                                file_content = FileNotifyContent(
                                    title=title,
                                    file_ext=file_ext,
                                    total_len=total_len,
                                    md5=md5,
                                    file_upload_token=file_upload_token,
                                    status=status,
                                    from_user=from_user,
                                    lan_info=lan_info
                                )
                            else:
                                # 文件发送完成消息
                                attach_id = appattach.find('attachid').text if appattach.find('attachid') is not None else ''
                                cdn_attach_url = appattach.find('cdnattachurl').text if appattach.find('cdnattachurl') is not None else ''
                                aes_key = appattach.find('aeskey').text if appattach.find('aeskey') is not None else ''
                                encryver = int(appattach.find('encryver').text) if appattach.find('encryver') is not None else 0
                                overwrite_newmsgid = int(appattach.find('overwrite_newmsgid').text) if appattach.find('overwrite_newmsgid') is not None else 0
                                
                                file_content = FileContent(
                                    title=title,
                                    file_ext=file_ext,
                                    total_len=total_len,
                                    attach_id=attach_id,
                                    cdn_attach_url=cdn_attach_url,
                                    aes_key=aes_key,
                                    md5=md5,
                                    encryver=encryver,
                                    overwrite_newmsgid=overwrite_newmsgid,
                                    file_upload_token=file_upload_token,
                                    from_user=from_user
                                )
                            
                            # 构建返回结果
                            result = {
                                'file': file_content,
                                'xml_data': {'msg': {'appmsg': {
                                    'title': title,
                                    'type': str(app_type),
                                    'showtype': appmsg.find('showtype').text if appmsg.find('showtype') is not None else '0',
                                    'appattach': {
                                        'totallen': str(total_len),
                                        'fileext': file_ext,
                                        'status': str(status) if app_type == APP_MSG_TYPE_FILE_NOTIFY else None,
                                    },
                                    'md5': md5,
                                    'laninfo': lan_info if app_type == APP_MSG_TYPE_FILE_NOTIFY else None
                                }}}
                            }
                            return result
                    except Exception as e:
                        print(f"解析文件消息失败: {e}")
                        return {'file': None}
                
                # 小程序消息
                elif app_type == APP_MSG_TYPE_MINIPROGRAM:
                    try:
                        # 获取小程序信息
                        weappinfo = appmsg.find('weappinfo')
                        if weappinfo is not None:
                            # 构建小程序内容
                            result = {
                                'miniprogram': MiniProgramContent(
                                    title=appmsg_dict.get('title', ''),
                                    description=appmsg_dict.get('des', ''),
                                    username=weappinfo.find('username').text if weappinfo.find('username') is not None else '',
                                    appid=weappinfo.find('appid').text if weappinfo.find('appid') is not None else '',
                                    type=int(weappinfo.find('type').text) if weappinfo.find('type') is not None else 0,
                                    version=int(weappinfo.find('version').text) if weappinfo.find('version') is not None else 0,
                                    icon_url=weappinfo.find('weappiconurl').text if weappinfo.find('weappiconurl') is not None else '',
                                    page_path=weappinfo.find('pagepath').text if weappinfo.find('pagepath') is not None else '',
                                    share_id=weappinfo.find('shareId').text if weappinfo.find('shareId') is not None else '',
                                    thumb_url=appmsg_dict.get('thumb_url', ''),
                                    thumb_width=appmsg_dict.get('thumb_width', 0),
                                    thumb_height=appmsg_dict.get('thumb_height', 0),
                                    thumb_aes_key=appmsg_dict.get('thumb_aes_key', ''),
                                    thumb_length=appmsg_dict.get('thumb_length', 0),
                                    thumb_md5=appmsg_dict.get('thumb_md5', ''),
                                    source_username=appmsg_dict.get('source_username', ''),
                                    source_displayname=appmsg_dict.get('source_displayname', ''),
                                    url=appmsg_dict.get('url', ''),
                                    from_user=appmsg_dict.get('from_user', ''),
                                    scene=appmsg_dict.get('scene', 0),
                                    app_service_type=int(weappinfo.find('appservicetype').text) if weappinfo.find('appservicetype') is not None else 0,
                                    is_brand_official=bool(int(weappinfo.find('brandofficialflag').text)) if weappinfo.find('brandofficialflag') is not None else False,
                                    show_relieved_buy_flag=int(weappinfo.find('showRelievedBuyFlag').text) if weappinfo.find('showRelievedBuyFlag') is not None else 0,
                                    has_relieved_buy_plugin=bool(int(weappinfo.find('hasRelievedBuyPlugin').text)) if weappinfo.find('hasRelievedBuyPlugin') is not None else False,
                                    is_flagship=bool(int(weappinfo.find('flagshipflag').text)) if weappinfo.find('flagshipflag') is not None else False,
                                    sub_type=int(weappinfo.find('subType').text) if weappinfo.find('subType') is not None else 0,
                                    is_private_message=bool(int(weappinfo.find('isprivatemessage').text)) if weappinfo.find('isprivatemessage') is not None else False
                                ),
                                'xml_data': {'msg': {'appmsg': appmsg_dict, 'weappinfo': {k: v for k, v in weappinfo.attrib.items()}}}  # 原始XML数据
                            }
                            return result
                    except Exception as e:
                        print(f"解析小程序消息失败: {e}")
                    
                    return {'miniprogram': None}
                
                # 引用消息
                elif app_type == APP_MSG_TYPE_QUOTE:
                    try:
                        # 获取引用消息信息
                        refermsg = appmsg.find('refermsg')
                        if refermsg is not None:
                            # 构建引用消息内容
                            result = {
                                'quote': QuoteContent(
                                    title=appmsg_dict.get('title', ''),
                                    type=app_type,
                                    url=appmsg_dict.get('url', ''),
                                    source_username=appmsg_dict.get('source_username', ''),
                                    source_displayname=appmsg_dict.get('source_displayname', ''),
                                    thumb_url=appmsg_dict.get('thumb_url', ''),
                                    thumb_width=appmsg_dict.get('thumb_width', 0),
                                    thumb_height=appmsg_dict.get('thumb_height', 0),
                                    thumb_aes_key=appmsg_dict.get('thumb_aes_key', ''),
                                    thumb_length=appmsg_dict.get('thumb_length', 0),
                                    thumb_md5=appmsg_dict.get('thumb_md5', ''),
                                    des=appmsg_dict.get('des', ''),
                                    action=appmsg_dict.get('action', ''),
                                    app_id=appmsg_dict.get('app_id', ''),
                                    sdk_ver=appmsg_dict.get('sdk_ver', '0'),
                                    show_type=appmsg_dict.get('show_type', 0),
                                    sound_type=appmsg_dict.get('sound_type', 0),
                                    content=appmsg_dict.get('content', ''),
                                    content_attr=appmsg_dict.get('content_attr', 0),
                                    refer_msg_type=int(refermsg.find('type').text) if refermsg.find('type') is not None else 0,
                                    refer_msg_id=refermsg.find('msgid').text if refermsg.find('msgid') is not None else '',
                                    refer_msg_svrid=refermsg.find('svrid').text if refermsg.find('svrid') is not None else '',
                                    refer_msg_from_user=refermsg.find('fromusr').text if refermsg.find('fromusr') is not None else '',
                                    refer_msg_chat_user=refermsg.find('chatusr').text if refermsg.find('chatusr') is not None else '',
                                    refer_msg_display_name=refermsg.find('displayname').text if refermsg.find('displayname') is not None else '',
                                    refer_msg_content=refermsg.find('content').text if refermsg.find('content') is not None else '',
                                    refer_msg_source=refermsg.find('msgsource').text if refermsg.find('msgsource') is not None else ''
                                ),
                                'xml_data': {'msg': {'appmsg': appmsg_dict, 'refermsg': {k: v for k, v in refermsg.attrib.items()}}}  # 原始XML数据
                            }
                            return result
                    except Exception as e:
                        print(f"解析引用消息失败: {e}")
                    
                    return {'quote': None}
                
                # 转账消息
                elif app_type == APP_MSG_TYPE_TRANSFER:
                    try:
                        # 解析XML内容
                        root = ET.fromstring(content)
                        appmsg = root.find('.//appmsg')
                        if appmsg is not None:
                            # 获取基本信息
                            title = appmsg.find('title').text if appmsg.find('title') is not None else ''
                            des = appmsg.find('des').text if appmsg.find('des') is not None else ''
                            url = appmsg.find('url').text if appmsg.find('url') is not None else ''
                            thumb_url = appmsg.find('thumburl').text if appmsg.find('thumburl') is not None else ''
                            
                            # 获取支付信息
                            wcpayinfo = appmsg.find('wcpayinfo')
                            if wcpayinfo is not None:
                                # 构建转账内容
                                result = {
                                    'transfer': TransferContent(
                                        title=title,
                                        type=app_type,
                                        des=des,
                                        url=url,
                                        thumb_url=thumb_url,
                                        pay_subtype=int(wcpayinfo.find('paysubtype').text) if wcpayinfo.find('paysubtype') is not None else 0,
                                        fee_desc=wcpayinfo.find('feedesc').text if wcpayinfo.find('feedesc') is not None else '',
                                        transcation_id=wcpayinfo.find('transcationid').text if wcpayinfo.find('transcationid') is not None else '',
                                        transfer_id=wcpayinfo.find('transferid').text if wcpayinfo.find('transferid') is not None else '',
                                        invalid_time=int(wcpayinfo.find('invalidtime').text) if wcpayinfo.find('invalidtime') is not None else 0,
                                        begin_transfer_time=int(wcpayinfo.find('begintransfertime').text) if wcpayinfo.find('begintransfertime') is not None else 0,
                                        effective_date=int(wcpayinfo.find('effectivedate').text) if wcpayinfo.find('effectivedate') is not None else 0,
                                        pay_memo=wcpayinfo.find('pay_memo').text if wcpayinfo.find('pay_memo') is not None else '',
                                        receiver_username=wcpayinfo.find('receiver_username').text if wcpayinfo.find('receiver_username') is not None else '',
                                        payer_username=wcpayinfo.find('payer_username').text if wcpayinfo.find('payer_username') is not None else ''
                                    ),
                                    'xml_data': {'msg': {'appmsg': appmsg_dict, 'wcpayinfo': {k: v for k, v in wcpayinfo.attrib.items()}}}  # 原始XML数据
                                }
                                return result
                    except Exception as e:
                        print(f"解析转账消息失败: {e}")
                    
                    return {'transfer': None}
                
                # 红包消息
                elif app_type == APP_MSG_TYPE_RED_PACKET:
                    return {'redpacket': appmsg_dict}
                
                # 视频号消息
                elif app_type == APP_MSG_TYPE_CHANNELS:
                    return {'channels': appmsg_dict}
                
                return {'app': appmsg_dict}
                
            elif msg_type == MSG_TYPE_CARD:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    
                    # 构建名片内容
                    result = {
                        'card': ContactCardContent(
                            wxid=root.get('username', ''),  # 用户唯一标识
                            nickname=root.get('nickname', ''),  # 用户昵称
                            avatar=root.get('bigheadimgurl', ''),  # 头像URL
                            alias=root.get('alias', ''),  # 微信号
                            sex=int(root.get('sex', '0')),  # 性别: 1男2女0未知
                            province=root.get('province', ''),  # 省份
                            city=root.get('city', ''),  # 城市
                            sign=root.get('sign', ''),  # 个性签名
                            scene=int(root.get('scene', '0')),  # 场景值
                            v3=root.get('username', '').startswith('v3_'),  # 是否v3数据
                            v4=root.get('antispamticket', '').startswith('v4_'),  # 是否v4数据
                            antispam_ticket=root.get('antispamticket', '')  # 防垃圾票据
                        ),
                        'xml_data': {'msg': {k: v for k, v in root.attrib.items()}}  # 原始XML数据
                    }
                    return result
                except Exception as e:
                    print(f"解析名片消息失败: {e}")
                    
                return {'card': ContactCardContent(
                    wxid='',
                    nickname='',
                    avatar=''
                )}
                
            elif msg_type == MSG_TYPE_VERIFY:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    
                    # 构建好友请求内容
                    result = {
                        'friend_request': FriendRequestContent(
                            wxid=root.get('fromusername', ''),  # 请求者wxid
                            encrypt_username=root.get('encryptusername', ''),  # 加密的用户名
                            nickname=root.get('fromnickname', ''),  # 请求者昵称
                            content=root.get('content', ''),  # 验证消息内容
                            avatar=root.get('bigheadimgurl', ''),  # 头像URL
                            scene=int(root.get('scene', '0')),  # 添加场景
                            ticket=root.get('ticket', ''),  # 验证票据
                            sex=int(root.get('sex', '0')),  # 性别
                            province=root.get('province', ''),  # 省份
                            city=root.get('city', ''),  # 城市
                            sign=root.get('sign', ''),  # 个性签名
                            weibo=root.get('weibo', ''),  # 微博账号
                            alias=root.get('alias', ''),  # 微信号
                            v3=root.get('encryptusername', '').startswith('v3_'),  # 是否v3数据
                            v4=root.get('ticket', '').startswith('v4_'),  # 是否v4数据
                            opcode=root.get('opcode', '2')  # 操作码
                        ),
                        'xml_data': {'msg': {k: v for k, v in root.attrib.items()}}  # 原始XML数据
                    }
                    return result
                except Exception as e:
                    print(f"解析好友请求消息失败: {e}")
                    
                return {'friend_request': None}
                
            elif msg_type == MSG_TYPE_SYSTEM:
                try:
                    # 解析群名称修改通知
                    if content.startswith(TEXT_GROUP_NAME_CHANGE):
                        # 提取新的群名称 - 格式: "你修改群名为xxx"
                        new_name = content[len(TEXT_GROUP_NAME_CHANGE):].strip('"')
                        return {
                            'group_name_change': GroupNameChangeContent(
                                chat_id=msg_data['FromUserName']['string'],
                                new_name=new_name,
                                operator_username=msg_data['ToUserName']['string']
                            )
                        }
                    # 解析群主更换通知
                    elif content == TEXT_GROUP_OWNER_CHANGE:
                        return {
                            'group_owner_change': GroupOwnerChangeContent(
                                chat_id=msg_data['FromUserName']['string'],
                                new_owner_username=msg_data['ToUserName']['string']
                            )
                        }
                except Exception as e:
                    print(f"解析群主更换通知失败: {e}")
                return {'system': content}
            
            elif msg_type == MSG_TYPE_APP and appmsg_dict and appmsg_dict.get('type') == 2001:
                # 解析红包消息
                try:
                    root = ET.fromstring(content)
                    appmsg = root.find('.//appmsg')
                    wcpayinfo = appmsg.find('.//wcpayinfo') if appmsg is not None else None
                    
                    if wcpayinfo is not None:
                        return {
                            'red_packet': RedPacketContent(
                                title=appmsg.find('title').text if appmsg.find('title') is not None else '',
                                type=int(appmsg.find('type').text) if appmsg.find('type') is not None else 2001,
                                des=appmsg.find('des').text if appmsg.find('des') is not None else '',
                                url=appmsg.find('url').text if appmsg.find('url') is not None else '',
                                thumb_url=appmsg.find('thumburl').text if appmsg.find('thumburl') is not None else '',
                                native_url=wcpayinfo.find('nativeurl').text if wcpayinfo.find('nativeurl') is not None else '',
                                sender_title=wcpayinfo.find('sendertitle').text if wcpayinfo.find('sendertitle') is not None else '',
                                receiver_title=wcpayinfo.find('receivertitle').text if wcpayinfo.find('receivertitle') is not None else '',
                                sender_desc=wcpayinfo.find('senderdes').text if wcpayinfo.find('senderdes') is not None else '',
                                receiver_desc=wcpayinfo.find('receiverdes').text if wcpayinfo.find('receiverdes') is not None else '',
                                scene_text=wcpayinfo.find('scenetext').text if wcpayinfo.find('scenetext') is not None else '',
                                scene_id=wcpayinfo.find('sceneid').text if wcpayinfo.find('sceneid') is not None else '',
                                inner_type=wcpayinfo.find('innertype').text if wcpayinfo.find('innertype') is not None else '',
                                pay_msg_id=wcpayinfo.find('paymsgid').text if wcpayinfo.find('paymsgid') is not None else '',
                                invalid_time=int(wcpayinfo.find('invalidtime').text) if wcpayinfo.find('invalidtime') is not None else 0,
                                template_id=wcpayinfo.find('templateid').text if wcpayinfo.find('templateid') is not None else ''
                            )
                        }
                except Exception as e:
                    print(f"解析红包消息失败: {e}")
                    return None
            
            elif msg_type == MSG_TYPE_APP and appmsg_dict and appmsg_dict.get('type') == 51:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    finder_feed = root.find('.//finderFeed')
                    if finder_feed is not None:
                        # 解析媒体列表
                        media_list = []
                        media_list_elem = finder_feed.find('mediaList')
                        if media_list_elem is not None:
                            for media_elem in media_list_elem.findall('media'):
                                media = {
                                    'media_type': int(media_elem.find('mediaType').text) if media_elem.find('mediaType') is not None else 0,
                                    'url': media_elem.find('url').text if media_elem.find('url') is not None else '',
                                    'thumb_url': media_elem.find('thumbUrl').text if media_elem.find('thumbUrl') is not None else '',
                                    'width': int(media_elem.find('width').text) if media_elem.find('width') is not None else 0,
                                    'height': int(media_elem.find('height').text) if media_elem.find('height') is not None else 0,
                                    'cover_url': media_elem.find('coverUrl').text if media_elem.find('coverUrl') is not None else '',
                                    'full_cover_url': media_elem.find('fullCoverUrl').text if media_elem.find('fullCoverUrl') is not None else '',
                                    'video_play_duration': media_elem.find('videoPlayDuration').text if media_elem.find('videoPlayDuration') is not None else ''
                                }
                                media_list.append(media)
                        
                        # 构建视频号内容
                        result = {
                            'finder_feed': FinderFeedContent(
                                object_id=finder_feed.find('objectId').text if finder_feed.find('objectId') is not None else '',
                                feed_type=int(finder_feed.find('feedType').text) if finder_feed.find('feedType') is not None else 0,
                                nickname=finder_feed.find('nickname').text if finder_feed.find('nickname') is not None else '',
                                avatar=finder_feed.find('avatar').text if finder_feed.find('avatar') is not None else '',
                                desc=finder_feed.find('desc').text if finder_feed.find('desc') is not None else '',
                                media_count=int(finder_feed.find('mediaCount').text) if finder_feed.find('mediaCount') is not None else 0,
                                object_nonce_id=finder_feed.find('objectNonceId').text if finder_feed.find('objectNonceId') is not None else '',
                                live_id=finder_feed.find('liveId').text if finder_feed.find('liveId') is not None else '',
                                username=finder_feed.find('username').text if finder_feed.find('username') is not None else '',
                                web_url=finder_feed.find('webUrl').text if finder_feed.find('webUrl') is not None else '',
                                auth_icon_type=int(finder_feed.find('authIconType').text) if finder_feed.find('authIconType') is not None else 0,
                                auth_icon_url=finder_feed.find('authIconUrl').text if finder_feed.find('authIconUrl') is not None else '',
                                biz_nickname=finder_feed.find('bizNickname').text if finder_feed.find('bizNickname') is not None else '',
                                biz_avatar=finder_feed.find('bizAvatar').text if finder_feed.find('bizAvatar') is not None else '',
                                biz_username_v2=finder_feed.find('bizUsernameV2').text if finder_feed.find('bizUsernameV2') is not None else '',
                                media_list=media_list
                            ),
                            'xml_data': {'msg': {'finder_feed': {k: v for k, v in finder_feed.attrib.items()}}}  # 原始XML数据
                        }
                        return result
                except Exception as e:
                    print(f"解析视频号消息失败: {e}")
                    return None
            
            elif msg_type == MSG_TYPE_SYSTEM_TEMPLATE:
                try:
                    # 解析XML内容
                    root = ET.fromstring(content)
                    if root.tag == 'sysmsg' and root.get('type') == SYSMSG_TYPE_TEMPLATE:
                        sysmsg_template = root.find('sysmsgtemplate')
                        if sysmsg_template is not None:
                            content_template = sysmsg_template.find('content_template')
                            if content_template is not None:
                                template = content_template.find('template')
                                if template is not None:
                                    # 处理解散群聊通知
                                    if content_template.get('type') == TEMPLATE_TYPE_SUCCEED_CONTACT and template.text == TEXT_GROUP_DISMISS_TEMPLATE:
                                        # 获取群主信息
                                        link_list = content_template.find('link_list')
                                        if link_list is not None:
                                            link = link_list.find('link')
                                            if link is not None and link.get('name') == 'identity':
                                                memberlist = link.find('memberlist')
                                                if memberlist is not None:
                                                    member = memberlist.find('member')
                                                    if member is not None:
                                                        username = member.find('username')
                                                        nickname = member.find('nickname')
                                                        if username is not None and nickname is not None:
                                                            return {
                                                                'group_dismiss': GroupDismissContent(
                                                                    chat_id=msg_data['FromUserName']['string'],
                                                                    owner_username=username.text,
                                                                    owner_nickname=nickname.text
                                                                )
                                                            }
                except Exception as e:
                    print(f"解析解散群聊通知失败: {e}")
                return {'system_template': content}
            
            elif msg_type == MSG_TYPE_TODO:
                try:
                    # 解析待办消息内容
                    xml_content = msg_data['Content']['string']
                    root = ET.fromstring(xml_content)
                    todo = root.find('.//todo')
                    if todo is not None:
                        todo_id = todo.find('todoid').text
                        title = todo.find('title').text
                        creator = todo.find('creator').text
                        manager = todo.find('manager').text
                        time = int(todo.find('time').text)
                        scene = todo.find('scene').text
                        template = todo.find('template').text
                        
                        return {
                            'todo': TodoContent(
                                todo_id=todo_id,
                                title=title,
                                creator=creator,
                                manager=manager,
                                time=time,
                                scene=scene,
                                template=template
                            )
                        }
                except Exception as e:
                    print(f"解析群待办消息失败: {e}")
            
            elif msg_type == MSG_TYPE_EXIT_GROUP:
                try:
                    chat_id = msg_data['UserName']['string']
                    delete_scene = msg_data.get('DeleteContactScen', 0)
                    
                    return {
                        'exit_group': ExitGroupContent(
                            chat_id=chat_id,
                            delete_scene=delete_scene
                        )
                    }
                except Exception as e:
                    print(f"解析退出群聊通知失败: {e}")
            
            elif msg_type == MSG_TYPE_OFFLINE:
                try:
                    wxid = msg_data.get('Wxid', '')
                    
                    return {
                        'offline': OfflineContent(
                            wxid=wxid
                        )
                    }
                except Exception as e:
                    print(f"解析掉线通知失败: {e}")
            
            else:
                # 其他类型消息，保留原始内容
                return {'raw': content}
                
        except Exception as e:
            print(f"解析消息内容失败: {e}")
            return {'raw': content}
    
    def receive_message(self, data: Dict[str, Any]) -> Optional[Message]:
        """接收并处理消息
        
        Args:
            data: 原始消息数据
            
        Returns:
            处理后的消息对象
        """
        # 解析消息
        message = self.parse_message(data)
        if not message:
            return None
            
        # 根据消息类型进行处理
        if message.type_name == TYPE_ADD_MSG:
            return self._handle_new_message(message)
            
        elif message.type_name == TYPE_MOD_CONTACTS:
            return self._handle_contact_change(message)
            
        elif message.type_name == TYPE_DEL_CONTACTS:
            return self._handle_contact_delete(message)
            
        elif message.type_name == TYPE_OFFLINE:
            return self._handle_offline(message)
            
        return message
    
    def _handle_new_message(self, message: Message) -> Message:
        """处理新消息
        
        Args:
            message: 消息对象
            
        Returns:
            处理后的消息对象
        """
        # TODO: 添加新消息的特殊处理逻辑
        return message
    
    def _handle_contact_change(self, message: Message) -> Message:
        """处理联系人变更
        
        Args:
            message: 消息对象
            
        Returns:
            处理后的消息对象
        """
        try:
            data = message.raw_data.get('Data', {})
            wxid = data.get('UserName', {}).get('string', '')
            
            # 判断是否为群聊信息变更
            if '@chatroom' in wxid:
                # 构建群信息变更内容
                group_info = GroupInfoChangeContent(
                    chat_id=wxid,
                    nickname=data.get('NickName', {}).get('string', ''),
                    owner_username=data.get('ChatRoomOwner', ''),
                    member_count=data.get('RoomInfoCount', 0),
                    max_member_count=data.get('ChatroomMaxCount', 0),
                    status=data.get('ChatroomStatus', 0),
                    notify=data.get('ChatRoomNotify', 0)
                )
                message.content = {'group_info_change': group_info}
                return message
            
            # 处理普通联系人变更
            contact_info = ContactInfo(
                wxid=wxid,
                nickname=data.get('NickName', {}).get('string', ''),
                py_initial=data.get('PyInitial', {}).get('string', ''),
                quan_pin=data.get('QuanPin', {}).get('string', ''),
                remark=data.get('Remark', {}).get('string', ''),
                remark_py_initial=data.get('RemarkPYInitial', {}).get('string', ''),
                remark_quan_pin=data.get('RemarkQuanPin', {}).get('string', ''),
                avatar_big=data.get('BigHeadImgUrl', ''),
                avatar_small=data.get('SmallHeadImgUrl', ''),
                sex=data.get('Sex', 0),
                country=data.get('Country', {}).get('string', ''),
                province=data.get('Province', {}).get('string', ''),
                city=data.get('City', {}).get('string', ''),
                signature=data.get('Signature', {}).get('string', ''),
                encrypt_username=data.get('EncryptUsername', {}).get('string', ''),
                bitmask=data.get('BitMask', 0),
                bitval=data.get('BitVal', 0),
                contact_type=data.get('ContactType', 0),
                room_notify=data.get('ChatRoomNotify', 0),
                delete_flag=data.get('DeleteFlag', 0),
                verify_flag=data.get('VerifyFlag', 0),
                level=data.get('Level', 0),
                source=data.get('Source', 0),
                weibo_flag=data.get('WeiboFlag', 0),
                sns_flag=data.get('SnsFlag', 0),
                sns_bgimg_id=data.get('SnsUserInfo', {}).get('SnsBgImgId', ''),
                sns_bgobject_id=data.get('SnsUserInfo', {}).get('SnsBgobjectId', 0),
                sns_flag_ex=data.get('SnsUserInfo', {}).get('SnsFlagEx', 0),
                has_weixin_hd_head_img=bool(data.get('HasWeiXinHdHeadImg', 0)),
                personal_card=bool(data.get('PersonalCard', 0)),
                album_style=data.get('AlbumStyle', 0),
                album_flag=data.get('AlbumFlag', 0),
                chatroom_max_count=data.get('ChatroomMaxCount', 0),
                chatroom_status=data.get('ChatroomStatus', 0),
                chatroom_business_type=data.get('ChatRoomBusinessType', 0),
                ext_flag=data.get('Extflag', 0)
            )
            
            # 更新消息内容
            message.content = {'contact': contact_info}
            
        except Exception as e:
            print(f"处理联系人变更失败: {e}")
            
        return message
    
    def _handle_contact_delete(self, message: Message) -> Message:
        """处理联系人删除
        
        Args:
            message: 消息对象
        
        Returns:
            处理后的消息对象
        """
        try:
            # TODO: 添加联系人删除的处理逻辑
            return message
        except Exception as e:
            print(f"处理联系人删除失败: {e}")
            return message
    
    def _handle_offline(self, message: Message) -> Message:
        """处理离线通知
        
        Args:
            message: 消息对象
        
        Returns:
            处理后的消息对象
        """
        try:
            # TODO: 添加离线通知的处理逻辑
            return message
        except Exception as e:
            print(f"处理离线通知失败: {e}")
            return message

    # 以下是针对特定消息类型的处理方法，可以被子类重写或通过register_handler注册自定义处理器
    
    def handle_text_message(self, msg_info):
        """处理文本消息"""
        print(f"处理文本消息: {msg_info.get('content')}")
        return None
    
    def handle_image_message(self, msg_info):
        """处理图片消息"""
        print(f"处理图片消息: {msg_info.get('msg_id')}")
        return None
    
    def handle_voice_message(self, msg_info):
        """处理语音消息"""
        print(f"处理语音消息: {msg_info.get('msg_id')}")
        return None
    
    def handle_video_message(self, msg_info):
        """处理视频消息"""
        print(f"处理视频消息: {msg_info.get('msg_id')}")
        return None
    
    def handle_link_message(self, msg_info):
        """处理链接消息"""
        print(f"处理链接消息: {msg_info.get('title')} - {msg_info.get('url')}")
        return None
    
    def handle_file_message(self, msg_info):
        """处理文件消息"""
        print(f"处理文件消息: {msg_info.get('msg_id')}")
        return None
    
    def handle_revoke_message(self, msg_info):
        """处理撤回消息
        
        Args:
            msg_info: 消息信息
            
        Returns:
            处理后的消息对象
        """
        if not msg_info or 'revoke' not in msg_info:
            return None
            
        revoke_content = msg_info['revoke']
        print(f"处理撤回消息: {revoke_content.replacemsg}")
        return revoke_content
    
    def handle_pat_message(self, msg_info):
        """处理拍一拍消息
        
        Args:
            msg_info: 消息信息
            
        Returns:
            处理后的消息对象
        """
        if not msg_info or 'pat' not in msg_info:
            return None
            
        pat_content = msg_info['pat']
        print(f"处理拍一拍消息: {pat_content.template}")
        return pat_content
        
    def handle_emoji_message(self, msg_info):
        """处理表情消息"""
        print(f"处理表情消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_location_message(self, msg_info):
        """处理地理位置消息
        
        Args:
            msg_info: 消息信息
            
        Returns:
            处理后的消息对象
        """
        if not msg_info or 'location' not in msg_info:
            return None
            
        location_content = msg_info['location']
        print(f"处理地理位置消息: {location_content.poiname}({location_content.label})")
        return location_content
        
    def handle_card_message(self, msg_info):
        """处理名片消息"""
        print(f"处理名片消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_friend_verification(self, msg_info):
        """处理好友验证消息"""
        print(f"处理好友验证消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_mini_program_message(self, msg_info):
        """处理小程序消息"""
        print(f"处理小程序消息: {msg_info.get('title')}")
        return None
        
    def handle_quote_message(self, msg_info):
        """处理引用消息"""
        print(f"处理引用消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_transfer_message(self, msg_info):
        """处理转账消息"""
        print(f"处理转账消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_red_packet_message(self, msg_info):
        """处理红包消息"""
        print(f"处理红包消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_channels_message(self, msg_info):
        """处理视频号消息"""
        print(f"处理视频号消息: {msg_info.get('msg_id')}")
        return None
        
    def handle_group_invite_message(self, msg_info):
        """处理群聊邀请消息
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_invite' not in msg_info.content:
            return msg_info
        
        invite_content = msg_info.content['group_invite']
        print(f"收到群聊邀请消息: {invite_content.inviter_username} 邀请加入群聊 {invite_content.chat_name}")
        return msg_info
        
    def handle_group_remove_message(self, msg_info):
        """处理被移除群聊通知
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_remove' not in msg_info.content:
            return msg_info
        
        remove_content = msg_info.content['group_remove']
        print(f"你被 {remove_content.remover_username} 移出群聊 {remove_content.chat_id}")
        return msg_info
        
    def handle_group_kick_message(self, msg_info):
        """处理踢出群聊通知
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_kick' not in msg_info.content:
            return msg_info
        
        kick_content = msg_info.content['group_kick']
        print(f"你将用户 {kick_content.kicked_nickname}({kick_content.kicked_username}) 移出了群聊 {kick_content.chat_id}")
        return msg_info
        
    def handle_group_dismiss_message(self, msg_info):
        """处理解散群聊通知
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_dismiss' not in msg_info.content:
            return msg_info
        
        dismiss_content = msg_info.content['group_dismiss']
        print(f"群主 {dismiss_content.owner_nickname}({dismiss_content.owner_username}) 已解散群聊 {dismiss_content.chat_id}")
        return msg_info
        
    def handle_group_name_change(self, msg_info):
        """处理群名称修改通知
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_name_change' not in msg_info.content:
            return msg_info
        
        change_content = msg_info.content['group_name_change']
        print(f"群聊 {change_content.chat_id} 的名称被 {change_content.operator_username} 修改为 {change_content.new_name}")
        return msg_info
        
    def handle_group_owner_change(self, msg_info):
        """处理群主更换通知
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_owner_change' not in msg_info.content:
            return msg_info
        
        change_content = msg_info.content['group_owner_change']
        print(f"群聊 {change_content.chat_id} 的群主已更换为 {change_content.new_owner_username}")
        return msg_info
        
    def handle_group_info_change(self, msg_info):
        """处理群信息变更通知
        
        Args:
            msg_info (Message): 消息对象
            
        Returns:
            Message: 处理后的消息对象
        """
        if not msg_info or 'group_info_change' not in msg_info.content:
            return msg_info
        
        change_content = msg_info.content['group_info_change']
        print(f"群聊 {change_content.chat_id} 信息已更新:")
        print(f"- 群名称: {change_content.nickname}")
        print(f"- 群主: {change_content.owner_username}")
        print(f"- 成员数: {change_content.member_count}")
        print(f"- 最大成员数: {change_content.max_member_count}")
        print(f"- 群状态: {change_content.status}")
        print(f"- 消息通知: {change_content.notify}")
        return msg_info
        
    def handle_group_announcement(self, msg_info):
        """处理群公告消息

        Args:
            msg_info: Message对象
        """
        if not msg_info or 'group_announcement' not in msg_info.content:
            return msg_info
            
        announcement = msg_info.content['group_announcement']
        print(f"收到群公告消息 - 群ID: {announcement.chat_id}")
        print(f"发布者: {announcement.publisher_username}")
        print(f"公告内容: {announcement.content}")
        print(f"公告ID: {announcement.announcement_id}")
        print(f"发布时间: {datetime.fromtimestamp(announcement.create_time)}")
        
        return msg_info