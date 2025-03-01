"""
回调消息数据模型
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

@dataclass
class BaseMessage:
    """基础消息模型"""
    type_name: str
    appid: str
    wxid: str
    raw_data: Dict[str, Any]

@dataclass
class TextContent:
    """文本内容
    
    Attributes:
        content: 消息文本内容
        push_content: 推送通知内容
        msg_source: 消息来源信息
        msg_seq: 消息序列号
        status: 消息状态
    """
    content: str
    push_content: Optional[str] = None
    msg_source: Optional[str] = None
    msg_seq: Optional[int] = None
    status: Optional[int] = None

@dataclass
class ImageContent:
    """图片内容
    
    Attributes:
        image_url: 图片的CDN URL
        thumb_url: 缩略图URL
        aes_key: 解密密钥
        thumb_aes_key: 缩略图解密密钥
        file_length: 文件大小
        thumb_length: 缩略图大小
        thumb_width: 缩略图宽度
        thumb_height: 缩略图高度
        md5: 文件MD5
        thumb_buffer: 缩略图base64数据
        encryver: 加密版本
        mid_width: 中等尺寸图片宽度
        mid_height: 中等尺寸图片高度
        hd_width: 高清图片宽度
        hd_height: 高清图片高度
        mid_image_url: 中等尺寸图片URL
    """
    image_url: str
    thumb_url: str
    aes_key: str
    thumb_aes_key: str
    file_length: int
    thumb_length: int
    thumb_width: int
    thumb_height: int
    md5: str
    thumb_buffer: Optional[str] = None
    encryver: Optional[int] = None
    mid_width: Optional[int] = None
    mid_height: Optional[int] = None
    hd_width: Optional[int] = None
    hd_height: Optional[int] = None
    mid_image_url: Optional[str] = None

@dataclass
class VideoContent:
    """视频内容
    
    Attributes:
        video_url: 视频的CDN URL
        thumb_url: 视频缩略图URL
        aes_key: 视频解密密钥
        thumb_aes_key: 缩略图解密密钥
        file_length: 视频文件大小
        play_length: 视频播放时长(秒)
        thumb_length: 缩略图大小
        thumb_width: 缩略图宽度
        thumb_height: 缩略图高度
        md5: 视频文件MD5
        new_md5: 新的MD5值
        from_user: 发送者wxid
        is_placeholder: 是否为占位视频
        raw_md5: 原始视频MD5
        raw_length: 原始视频大小
        raw_video_url: 原始视频URL
        raw_video_aes_key: 原始视频解密密钥
        origin_source_md5: 源视频MD5
        is_ad: 是否为广告视频
    """
    video_url: str
    thumb_url: str
    aes_key: str
    thumb_aes_key: str
    file_length: int
    play_length: int
    thumb_length: int
    thumb_width: int
    thumb_height: int
    md5: str
    new_md5: str
    from_user: str
    is_placeholder: bool = False
    raw_md5: Optional[str] = None
    raw_length: Optional[int] = None
    raw_video_url: Optional[str] = None
    raw_video_aes_key: Optional[str] = None
    origin_source_md5: Optional[str] = None
    is_ad: bool = False

@dataclass
class EmojiContent:
    """表情内容
    
    Attributes:
        md5: 表情文件MD5
        cdn_url: 表情CDN URL
        aes_key: 解密密钥
        file_length: 文件大小
        width: 表情宽度
        height: 表情高度
        thumb_url: 缩略图URL
        encrypt_url: 加密URL
        extern_url: 外部URL
        extern_md5: 外部MD5
        type: 表情类型
        product_id: 产品ID
        attached_text: 附加文本
        attached_text_color: 附加文本颜色
        lens_id: 镜头ID
        emoji_attr: 表情属性
        link_id: 链接ID
        desc: 描述
    """
    md5: str
    cdn_url: str
    aes_key: str
    file_length: int
    width: int
    height: int
    thumb_url: str = ''
    encrypt_url: str = ''
    extern_url: str = ''
    extern_md5: str = ''
    type: str = '2'
    product_id: str = ''
    attached_text: str = ''
    attached_text_color: str = ''
    lens_id: str = ''
    emoji_attr: str = ''
    link_id: str = ''
    desc: str = ''

@dataclass
class VoiceContent:
    """语音内容
    
    Attributes:
        voice_url: 语音文件的CDN URL
        voice_length: 语音时长(毫秒)
        aes_key: 解密密钥
        file_length: 文件大小
        voice_format: 语音格式
        buffer: 语音文件的base64数据
        md5: 文件MD5
    """
    voice_url: str
    voice_length: int
    aes_key: str
    file_length: int
    voice_format: int
    buffer: Optional[str] = None
    md5: Optional[str] = None

@dataclass
class LocationContent:
    """地理位置消息内容
    
    Attributes:
        latitude: 纬度
        longitude: 经度
        scale: 缩放级别
        label: 位置标签
        maptype: 地图类型
        poiname: 地点名称
        poiid: 地点ID
        building_id: 建筑ID
        floor_name: 楼层名称
        poi_category_tips: 地点分类提示
        poi_business_hour: 营业时间
        poi_phone: 联系电话
        poi_price_tips: 价格提示
        is_from_poi_list: 是否来自POI列表
        adcode: 行政区划代码
        cityname: 城市名称
    """
    latitude: float
    longitude: float
    scale: int
    label: str
    maptype: str
    poiname: str
    poiid: str = ''
    building_id: str = ''
    floor_name: str = ''
    poi_category_tips: str = ''
    poi_business_hour: str = ''
    poi_phone: str = ''
    poi_price_tips: str = ''
    is_from_poi_list: bool = False
    adcode: str = ''
    cityname: str = ''

@dataclass
class AppMessageContent:
    """公众号链接内容
    
    Attributes:
        title: 标题
        type: 消息类型
        url: 链接URL
        source_username: 公众号原始ID
        source_displayname: 公众号显示名称
        thumb_url: 缩略图URL
        thumb_width: 缩略图宽度
        thumb_height: 缩略图高度
        thumb_aes_key: 缩略图解密密钥
        thumb_length: 缩略图大小
        thumb_md5: 缩略图MD5
        des: 描述
        action: 动作
        app_id: 应用ID
        sdk_ver: SDK版本
        show_type: 显示类型
        sound_type: 声音类型
        content: 内容
        content_attr: 内容属性
    """
    title: str
    type: int
    url: str
    source_username: str
    source_displayname: str
    thumb_url: str
    thumb_width: int
    thumb_height: int
    thumb_aes_key: str
    thumb_length: int
    thumb_md5: str
    des: str = ''
    action: str = ''
    app_id: str = ''
    sdk_ver: str = '0'
    show_type: int = 0
    sound_type: int = 0
    content: str = ''
    content_attr: int = 0

@dataclass
class FileNotifyContent:
    """文件发送通知内容
    
    Attributes:
        title: 文件名
        file_ext: 文件扩展名
        total_len: 文件总大小(字节)
        md5: 文件MD5值
        file_upload_token: 文件上传令牌
        status: 文件状态
        from_user: 发送者wxid
        lan_info: 语言信息
    """
    title: str
    file_ext: str
    total_len: int
    md5: str
    file_upload_token: str
    status: int
    from_user: str
    lan_info: str = ''

@dataclass
class FileContent:
    """文件内容
    
    Attributes:
        title: 文件名
        file_ext: 文件扩展名
        total_len: 文件总大小(字节)
        attach_id: 附件ID
        cdn_attach_url: CDN附件URL
        aes_key: 解密密钥
        md5: 文件MD5值
        encryver: 加密版本
        overwrite_newmsgid: 覆盖的新消息ID
        file_upload_token: 文件上传令牌
        from_user: 发送者wxid
    """
    title: str
    file_ext: str
    total_len: int
    attach_id: str
    cdn_attach_url: str
    aes_key: str
    md5: str
    encryver: int
    overwrite_newmsgid: int
    file_upload_token: str
    from_user: str

@dataclass
class LinkContent:
    """链接内容"""
    title: str
    url: str
    description: Optional[str] = None
    thumb_url: Optional[str] = None

@dataclass
class ContactCardContent:
    """名片内容
    
    Attributes:
        wxid: 用户唯一标识
        nickname: 用户昵称
        avatar: 头像URL
        alias: 微信号
        sex: 性别(1男2女0未知)
        province: 省份
        city: 城市
        sign: 个性签名
        scene: 场景值
        v3: 是否v3数据
        v4: 是否v4数据
        antispam_ticket: 防垃圾票据
    """
    wxid: str
    nickname: str
    avatar: str
    alias: str = ''
    sex: int = 0
    province: str = ''
    city: str = ''
    sign: str = ''
    scene: int = 0
    v3: bool = False
    v4: bool = False
    antispam_ticket: str = ''

@dataclass
class FriendRequestContent:
    """好友请求内容
    
    Attributes:
        wxid: 请求者wxid
        encrypt_username: 加密的用户名
        nickname: 请求者昵称
        content: 验证消息内容
        avatar: 头像URL
        scene: 添加场景
        ticket: 验证票据
        sex: 性别(1男2女0未知)
        province: 省份
        city: 城市
        sign: 个性签名
        weibo: 微博账号
        alias: 微信号
        v3: 是否v3数据
        v4: 是否v4数据
        opcode: 操作码
    """
    wxid: str
    encrypt_username: str
    nickname: str
    content: str
    avatar: str
    scene: int
    ticket: str
    sex: int = 0
    province: str = ''
    city: str = ''
    sign: str = ''
    weibo: str = ''
    alias: str = ''
    v3: bool = False
    v4: bool = False
    opcode: str = '2'

@dataclass
class ContactInfo:
    """联系人信息
    
    Attributes:
        wxid: 用户唯一标识
        nickname: 用户昵称
        py_initial: 昵称拼音首字母
        quan_pin: 昵称全拼
        remark: 备注名
        remark_py_initial: 备注拼音首字母
        remark_quan_pin: 备注全拼
        avatar_big: 大头像URL
        avatar_small: 小头像URL
        sex: 性别(1男2女0未知)
        country: 国家
        province: 省份
        city: 城市
        signature: 个性签名
        encrypt_username: 加密用户名
        bitmask: 位掩码
        bitval: 位值
        contact_type: 联系人类型
        room_notify: 群消息通知
        delete_flag: 删除标记
        verify_flag: 验证标记
        level: 等级
        source: 来源
        weibo_flag: 微博标记
        sns_flag: 朋友圈标记
        sns_bgimg_id: 朋友圈背景图片ID
        sns_bgobject_id: 朋友圈背景对象ID
        sns_flag_ex: 朋友圈扩展标记
        has_weixin_hd_head_img: 是否有高清头像
        personal_card: 是否是名片
        album_style: 相册样式
        album_flag: 相册标记
        chatroom_max_count: 群聊最大人数
        chatroom_status: 群聊状态
        chatroom_business_type: 群聊业务类型
        ext_flag: 扩展标记
    """
    wxid: str
    nickname: str
    py_initial: str = ''
    quan_pin: str = ''
    remark: str = ''
    remark_py_initial: str = ''
    remark_quan_pin: str = ''
    avatar_big: str = ''
    avatar_small: str = ''
    sex: int = 0
    country: str = ''
    province: str = ''
    city: str = ''
    signature: str = ''
    encrypt_username: str = ''
    bitmask: int = 0
    bitval: int = 0
    contact_type: int = 0
    room_notify: int = 0
    delete_flag: int = 0
    verify_flag: int = 0
    level: int = 0
    source: int = 0
    weibo_flag: int = 0
    sns_flag: int = 0
    sns_bgimg_id: str = ''
    sns_bgobject_id: int = 0
    sns_flag_ex: int = 0
    has_weixin_hd_head_img: bool = False
    personal_card: bool = False
    album_style: int = 0
    album_flag: int = 0
    chatroom_max_count: int = 0
    chatroom_status: int = 0
    chatroom_business_type: int = 0
    ext_flag: int = 0

@dataclass
class FriendPassVerifyContent:
    """好友通过验证消息内容
    
    Attributes:
        title: 标题
        description: 描述
        type: 消息类型(33/36)
        url: 链接URL
        source_username: 来源用户名
        source_displayname: 来源显示名称
        thumb_url: 缩略图URL
        thumb_width: 缩略图宽度
        thumb_height: 缩略图高度
        thumb_aes_key: 缩略图解密密钥
        thumb_length: 缩略图大小
        thumb_md5: 缩略图MD5
        from_user: 发送者wxid
        scene: 场景值
        weapp_info: 小程序信息
    """
    title: str
    description: str
    type: int
    url: str
    source_username: str
    source_displayname: str
    thumb_url: str
    thumb_width: int
    thumb_height: int
    thumb_aes_key: str
    thumb_length: int
    thumb_md5: str
    from_user: str
    scene: int = 0
    weapp_info: Optional[Dict[str, Any]] = None

@dataclass
class MiniProgramContent:
    """小程序消息内容
    
    Attributes:
        title: 小程序标题
        description: 小程序描述
        username: 小程序原始ID
        appid: 小程序appid
        type: 小程序类型
        version: 小程序版本号
        icon_url: 小程序图标URL
        page_path: 小程序页面路径
        share_id: 分享ID
        thumb_url: 缩略图URL
        thumb_width: 缩略图宽度
        thumb_height: 缩略图高度
        thumb_aes_key: 缩略图解密密钥
        thumb_length: 缩略图大小
        thumb_md5: 缩略图MD5
        source_username: 来源用户名
        source_displayname: 来源显示名称
        url: 链接URL
        from_user: 发送者wxid
        scene: int = 0
        app_service_type: int = 0
        is_brand_official: bool = False
        show_relieved_buy_flag: int = 0
        has_relieved_buy_plugin: bool = False
        is_flagship: bool = False
        sub_type: int = 0
        is_private_message: bool = False
    """
    title: str
    description: str
    username: str
    appid: str
    type: int
    version: int
    icon_url: str
    page_path: str
    share_id: str
    thumb_url: str
    thumb_width: int
    thumb_height: int
    thumb_aes_key: str
    thumb_length: int
    thumb_md5: str
    source_username: str
    source_displayname: str
    url: str
    from_user: str
    scene: int = 0
    app_service_type: int = 0
    is_brand_official: bool = False
    show_relieved_buy_flag: int = 0
    has_relieved_buy_plugin: bool = False
    is_flagship: bool = False
    sub_type: int = 0
    is_private_message: bool = False

@dataclass
class QuoteContent:
    """引用消息内容
    
    Attributes:
        title: 引用消息标题
        type: 引用消息类型
        url: 链接URL
        source_username: 来源用户名
        source_displayname: 来源显示名称
        thumb_url: 缩略图URL
        thumb_width: 缩略图宽度
        thumb_height: 缩略图高度
        thumb_aes_key: 缩略图解密密钥
        thumb_length: 缩略图大小
        thumb_md5: 缩略图MD5
        des: 描述
        action: 动作
        app_id: 应用ID
        sdk_ver: SDK版本
        show_type: 显示类型
        sound_type: 声音类型
        content: 内容
        content_attr: 内容属性
        refer_msg_type: 引用消息类型
        refer_msg_id: 引用消息ID
        refer_msg_svrid: 引用消息服务器ID
        refer_msg_from_user: 引用消息发送者
        refer_msg_chat_user: 引用消息聊天用户
        refer_msg_display_name: 引用消息显示名称
        refer_msg_content: 引用消息内容
        refer_msg_source: 引用消息来源
    """
    title: str
    type: int
    url: str = ''
    source_username: str = ''
    source_displayname: str = ''
    thumb_url: str = ''
    thumb_width: int = 0
    thumb_height: int = 0
    thumb_aes_key: str = ''
    thumb_length: int = 0
    thumb_md5: str = ''
    des: str = ''
    action: str = ''
    app_id: str = ''
    sdk_ver: str = '0'
    show_type: int = 0
    sound_type: int = 0
    content: str = ''
    content_attr: int = 0
    refer_msg_type: int = 0
    refer_msg_id: str = ''
    refer_msg_svrid: str = ''
    refer_msg_from_user: str = ''
    refer_msg_chat_user: str = ''
    refer_msg_display_name: str = ''
    refer_msg_content: str = ''
    refer_msg_source: str = ''

@dataclass
class TransferContent:
    """转账消息内容
    
    Attributes:
        title: 标题，通常为"微信转账"
        type: 消息类型，固定为2000
        des: 描述，如"收到转账0.10元"
        url: 链接URL
        thumb_url: 缩略图URL
        pay_subtype: 支付子类型
        fee_desc: 金额描述，如"￥0.10"
        transcation_id: 交易ID
        transfer_id: 转账ID
        invalid_time: 失效时间戳
        begin_transfer_time: 开始转账时间戳
        effective_date: 生效日期
        pay_memo: 支付备注
        receiver_username: 接收者用户名
        payer_username: 支付者用户名
    """
    title: str
    type: int
    des: str = ''
    url: str = ''
    thumb_url: str = ''
    pay_subtype: int = 0
    fee_desc: str = ''
    transcation_id: str = ''
    transfer_id: str = ''
    invalid_time: int = 0
    begin_transfer_time: int = 0
    effective_date: int = 0
    pay_memo: str = ''
    receiver_username: str = ''
    payer_username: str = ''

@dataclass
class RedPacketContent:
    """红包消息内容
    
    Attributes:
        title: 标题，通常为"微信红包"
        type: 消息类型，固定为2001
        des: 描述，如"我给你发了一个红包，赶紧去拆!"
        url: 红包链接URL
        thumb_url: 缩略图URL，通常为红包封面图
        native_url: 原生URL，用于客户端打开红包
        sender_title: 发送者标题，通常为"恭喜发财，大吉大利"
        receiver_title: 接收者标题，通常为"恭喜发财，大吉大利"
        sender_desc: 发送者描述，通常为"查看红包"
        receiver_desc: 接收者描述，通常为"领取红包"
        scene_text: 场景文本，通常为"微信红包"
        scene_id: 场景ID
        inner_type: 内部类型
        pay_msg_id: 支付消息ID
        invalid_time: 失效时间戳
        template_id: 模板ID
    """
    title: str
    type: int
    des: str = ''
    url: str = ''
    thumb_url: str = ''
    native_url: str = ''
    sender_title: str = ''
    receiver_title: str = ''
    sender_desc: str = ''
    receiver_desc: str = ''
    scene_text: str = ''
    scene_id: str = ''
    inner_type: str = ''
    pay_msg_id: str = ''
    invalid_time: int = 0
    template_id: str = ''

@dataclass
class FinderFeedContent:
    """视频号消息内容
    
    Attributes:
        object_id: 视频号内容ID
        feed_type: 视频号类型
        nickname: 发布者昵称
        avatar: 发布者头像URL
        desc: 视频号描述
        media_count: 媒体数量
        object_nonce_id: 视频号内容唯一ID
        live_id: 直播ID
        username: 视频号用户名
        web_url: 网页URL
        auth_icon_type: 认证图标类型
        auth_icon_url: 认证图标URL
        biz_nickname: 商家昵称
        biz_avatar: 商家头像URL
        biz_username_v2: 商家用户名v2
        media_list: 媒体列表
    """
    object_id: str
    feed_type: int
    nickname: str
    avatar: str
    desc: str
    media_count: int
    object_nonce_id: str
    live_id: str
    username: str
    web_url: str = ''
    auth_icon_type: int = 0
    auth_icon_url: str = ''
    biz_nickname: str = ''
    biz_avatar: str = ''
    biz_username_v2: str = ''
    media_list: List[Dict[str, Any]] = None

@dataclass
class FinderMediaContent:
    """视频号媒体内容
    
    Attributes:
        media_type: 媒体类型(4=视频)
        url: 媒体URL
        thumb_url: 缩略图URL
        width: 宽度
        height: 高度
        cover_url: 封面URL
        full_cover_url: 完整封面URL
        video_play_duration: 视频播放时长
    """
    media_type: int
    url: str
    thumb_url: str
    width: int
    height: int
    cover_url: str
    full_cover_url: str
    video_play_duration: str = ''

@dataclass
class RevokeContent:
    """撤回消息内容
    
    Attributes:
        session: 会话ID
        msgid: 被撤回消息的ID
        newmsgid: 新消息ID
        replacemsg: 替换显示的消息内容
    """
    session: str
    msgid: str
    newmsgid: str
    replacemsg: str

@dataclass
class PatContent:
    """拍一拍消息内容
    
    Attributes:
        from_username: 发起拍一拍的用户wxid
        chat_username: 聊天对象的wxid
        patted_username: 被拍的用户wxid
        pat_suffix: 拍一拍后缀
        pat_suffix_version: 后缀版本
        template: 拍一拍消息模板
    """
    from_username: str
    chat_username: str
    patted_username: str
    pat_suffix: str = ''
    pat_suffix_version: int = 0
    template: str = ''

@dataclass
class GroupInviteContent:
    """群聊邀请消息内容
    
    Attributes:
        title: 标题，通常为"邀请你加入群聊"
        description: 描述，如"xxx邀请你加入群聊xxx，进入可查看详情。"
        url: 邀请链接URL
        thumb_url: 群头像URL
        inviter_username: 邀请者wxid
        chat_name: 群聊名称
    """
    title: str
    description: str
    url: str
    thumb_url: str = ''
    inviter_username: str = ''
    chat_name: str = ''

@dataclass
class GroupRemoveContent:
    """被移除群聊通知内容
    
    Attributes:
        chat_id: 群聊ID
        remover_username: 执行移除操作的用户名
    """
    chat_id: str
    remover_username: str

@dataclass
class GroupKickContent:
    """踢出群聊通知内容
    
    Attributes:
        chat_id: 群聊ID
        kicker_username: 执行踢出操作的用户名
        kicked_username: 被踢出的用户名
        kicked_nickname: 被踢出的用户昵称
    """
    chat_id: str
    kicker_username: str
    kicked_username: str
    kicked_nickname: str

@dataclass
class GroupDismissContent:
    """解散群聊通知内容
    
    Attributes:
        chat_id: 群聊ID
        owner_username: 群主的wxid
        owner_nickname: 群主的昵称
    """
    chat_id: str
    owner_username: str
    owner_nickname: str

@dataclass
class GroupNameChangeContent:
    """群名称修改通知内容
    
    Attributes:
        chat_id: 群聊ID
        new_name: 新的群名称
        operator_username: 操作者的wxid
    """
    chat_id: str
    new_name: str
    operator_username: str

@dataclass
class GroupInfoChangeContent:
    """群信息变更通知内容
    
    Attributes:
        chat_id: 群聊ID
        nickname: 群名称
        owner_username: 群主wxid
        member_count: 群成员数量
        max_member_count: 最大成员数量
        status: 群状态
        notify: 群消息通知设置
    """
    chat_id: str
    nickname: str
    owner_username: str
    member_count: int = 0
    max_member_count: int = 0
    status: int = 0
    notify: int = 0

@dataclass
class GroupAnnouncementContent:
    """群公告内容
    
    Attributes:
        chat_id: 群聊ID
        content: 公告内容
        publisher_username: 发布者wxid
        announcement_id: 公告ID
        create_time: 发布时间
    """
    chat_id: str
    content: str
    publisher_username: str
    announcement_id: str
    create_time: int

@dataclass
class TodoContent:
    """群待办消息内容
    
    Attributes:
        todo_id: 待办ID
        title: 待办标题
        creator: 创建者的wxid
        manager: 管理者的wxid
        time: 创建时间
        scene: 场景
        template: 模板内容
    """
    todo_id: str
    title: str
    creator: str
    manager: str
    time: int
    scene: str
    template: str

@dataclass
class ExitGroupContent:
    """退出群聊通知内容
    
    Attributes:
        chat_id: 退出的群聊ID
        delete_scene: 删除场景
    """
    chat_id: str
    delete_scene: int

@dataclass
class OfflineContent:
    """掉线通知内容
    
    Attributes:
        wxid: 掉线号的wxid
    """
    wxid: str

@dataclass
class Message(BaseMessage):
    """完整消息模型"""
    msg_id: str
    from_user: str
    to_user: str
    msg_type: int
    create_time: datetime
    content: Optional[Dict[str, Any]] = None
    
    @property
    def is_group_message(self) -> bool:
        """是否是群消息"""
        return '@@' in (self.from_user or '') or '@chatroom' in (self.from_user or '') or \
               '@@' in (self.to_user or '') or '@chatroom' in (self.to_user or '')
    
    @property
    def actual_sender(self) -> Optional[str]:
        """实际发送人
        
        群消息格式：
        1. 普通文本消息：wxid_xxx:\n消息内容
        2. 引用消息：wxid_xxx:\n引用"消息内容"\n回复内容
        """
        if not self.is_group_message:
            return self.from_user
            
        if not self.content:
            return None
            
        # 获取原始内容
        raw_content = None
        if 'text' in self.content:
            raw_content = self.content['text'].content
        elif 'raw' in self.content:
            raw_content = self.content['raw']
            
        if not raw_content:
            return None
            
        # 尝试从内容中提取发送者
        match = re.match(r'^(.*?):', raw_content)
        if match:
            return match.group(1)
            
        return None
    
    @property
    def actual_content(self) -> Optional[Any]:
        """解析后的实际内容
        
        群消息格式：
        1. 普通文本消息：wxid_xxx:\n消息内容
        2. 引用消息：wxid_xxx:\n引用"消息内容"\n回复内容
        """
        if not self.is_group_message:
            return self.content
            
        if not self.content:
            return None
            
        # 获取原始内容
        raw_content = None
        if 'text' in self.content:
            raw_content = self.content['text'].content
        elif 'raw' in self.content:
            raw_content = self.content['raw']
            
        if not raw_content:
            return self.content
            
        # 尝试提取实际内容
        parts = raw_content.split(':', 1)
        if len(parts) > 1:
            actual_content = parts[1].lstrip('\n')
            if 'text' in self.content:
                return {'text': TextContent(content=actual_content)}
            return {'raw': actual_content}
            
        return self.content 