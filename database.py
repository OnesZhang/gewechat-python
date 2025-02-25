import mysql.connector
from mysql.connector import Error
import os
import logging
import json

from dotenv import load_dotenv
load_dotenv()

# 数据库配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 3306),
    'database': os.getenv('DB_NAME', 'wechat_contacts'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

logger = logging.getLogger(__name__)

def create_connection():
    """创建数据库连接"""
    connection = None
    try:
        # 连接到 MySQL
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )
        logger.info("成功连接到数据库服务器")

        # 检查数据库是否存在
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        logger.info(f"数据库 {db_config['database']} 已创建或已存在")
        
        # 连接到指定数据库
        connection.database = db_config['database']
        
    except Error as e:
        logger.error(f"数据库连接错误: {e}")
    return connection

def create_tables(connection):
    """创建数据库表"""
    create_friends_table = """
    CREATE TABLE IF NOT EXISTS friends (
        id INT AUTO_INCREMENT PRIMARY KEY,
        wxid VARCHAR(255) NOT NULL UNIQUE,
        nick_name VARCHAR(255),
        sex INT,
        country VARCHAR(50),
        province VARCHAR(100),
        city VARCHAR(100),
        head_img_url TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    create_chatrooms_table = """
    CREATE TABLE IF NOT EXISTS chatrooms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chatroom_id VARCHAR(255) NOT NULL UNIQUE,
        nick_name VARCHAR(255),
        head_img_url TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    create_ghs_table = """
    CREATE TABLE IF NOT EXISTS ghs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        gh_id VARCHAR(255) NOT NULL UNIQUE
    )
    """
    cursor = connection.cursor()
    cursor.execute(create_friends_table)
    cursor.execute(create_chatrooms_table)
    cursor.execute(create_ghs_table)
    connection.commit()
    cursor.close()

def save_contacts_to_db(connection, contacts, brief_info=None):
    """将通讯录保存到数据库"""
    cursor = connection.cursor()
    
    # 获取当前数据库中的记录
    cursor.execute("SELECT wxid FROM friends")
    existing_friends = {row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT chatroom_id FROM chatrooms")
    existing_chatrooms = {row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT gh_id FROM ghs")
    existing_ghs = {row[0] for row in cursor.fetchall()}
    
    # 保存好友
    new_friends = 0
    for wxid in contacts['friends']:
        if wxid not in existing_friends:
            new_friends += 1
        cursor.execute("INSERT INTO friends (wxid) VALUES (%s) ON DUPLICATE KEY UPDATE wxid=VALUES(wxid)", (wxid,))
    logger.info(f"保存好友信息: 总数{len(contacts['friends'])}，新增{new_friends}")
    
    # 保存群聊
    new_chatrooms = 0
    for chatroom_id in contacts['chatrooms']:
        if chatroom_id not in existing_chatrooms:
            new_chatrooms += 1
        cursor.execute("INSERT INTO chatrooms (chatroom_id) VALUES (%s) ON DUPLICATE KEY UPDATE chatroom_id=VALUES(chatroom_id)", (chatroom_id,))
    logger.info(f"保存群聊信息: 总数{len(contacts['chatrooms'])}，新增{new_chatrooms}")
    
    # 保存公众号
    new_ghs = 0
    for gh_id in contacts['ghs']:
        if gh_id not in existing_ghs:
            new_ghs += 1
        cursor.execute("INSERT INTO ghs (gh_id) VALUES (%s) ON DUPLICATE KEY UPDATE gh_id=VALUES(gh_id)", (gh_id,))
    logger.info(f"保存公众号信息: 总数{len(contacts['ghs'])}，新增{new_ghs}")
    
    # 删除不再存在的好友
    deleted_friends = 0
    for wxid in existing_friends:
        if wxid not in contacts['friends']:
            cursor.execute("DELETE FROM friends WHERE wxid = %s", (wxid,))
            deleted_friends += 1
    if deleted_friends > 0:
        logger.info(f"删除不存在的好友: {deleted_friends}个")
    
    # 删除不再存在的群聊
    deleted_chatrooms = 0
    for chatroom_id in existing_chatrooms:
        if chatroom_id not in contacts['chatrooms']:
            cursor.execute("DELETE FROM chatrooms WHERE chatroom_id = %s", (chatroom_id,))
            deleted_chatrooms += 1
    if deleted_chatrooms > 0:
        logger.info(f"删除不存在的群聊: {deleted_chatrooms}个")
    
    # 删除不再存在的公众号
    deleted_ghs = 0
    for gh_id in existing_ghs:
        if gh_id not in contacts['ghs']:
            cursor.execute("DELETE FROM ghs WHERE gh_id = %s", (gh_id,))
            deleted_ghs += 1
    if deleted_ghs > 0:
        logger.info(f"删除不存在的公众号: {deleted_ghs}个")
    
    # 保存联系人简要信息
    if brief_info:
        updated_friends = 0
        updated_chatrooms = 0
        
        for info in brief_info:
            user_name = info.get('userName')
            
            # 处理好友信息
            if user_name in contacts['friends']:
                query = """
                UPDATE friends SET 
                    nick_name = %s,
                    sex = %s,
                    country = %s,
                    province = %s,
                    city = %s,
                    head_img_url = %s
                WHERE wxid = %s
                """
                data = (
                    info.get('nickName'),
                    info.get('sex'),
                    info.get('country'),
                    info.get('province'),
                    info.get('city'),
                    info.get('smallHeadImgUrl'),
                    user_name
                )
                cursor.execute(query, data)
                updated_friends += 1
            
            # 处理群聊信息
            elif user_name in contacts['chatrooms']:
                query = """
                UPDATE chatrooms SET 
                    nick_name = %s,
                    head_img_url = %s
                WHERE chatroom_id = %s
                """
                data = (
                    info.get('nickName'),
                    info.get('smallHeadImgUrl'),
                    user_name
                )
                cursor.execute(query, data)
                updated_chatrooms += 1
        
        logger.info(f"更新好友详细信息: {updated_friends}个")
        logger.info(f"更新群聊详细信息: {updated_chatrooms}个")
    
    connection.commit()
    cursor.close()

def get_friends(connection, limit=100, offset=0):
    """获取好友列表"""
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT * FROM friends
    ORDER BY nick_name
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_chatrooms(connection, limit=100, offset=0):
    """获取群聊列表"""
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT * FROM chatrooms
    ORDER BY nick_name
    LIMIT %s OFFSET %s
    """
    cursor.execute(query, (limit, offset))
    results = cursor.fetchall()
    cursor.close()
    return results

def search_contacts(connection, keyword, contact_type=None, limit=100, offset=0):
    """
    搜索联系人
    
    参数:
        connection: 数据库连接
        keyword: 搜索关键词
        contact_type: 联系人类型，可选 ('friend', 'chatroom')
        limit: 返回结果数量限制，默认100
        offset: 分页偏移量，默认0
        
    返回:
        匹配的联系人列表
    """
    cursor = connection.cursor(dictionary=True)
    
    if contact_type == 'friend':
        query = """
        SELECT * FROM friends
        WHERE nick_name LIKE %s OR wxid LIKE %s
        ORDER BY nick_name
        LIMIT %s OFFSET %s
        """
        search_param = f"%{keyword}%"
        cursor.execute(query, (search_param, search_param, limit, offset))
    elif contact_type == 'chatroom':
        query = """
        SELECT * FROM chatrooms
        WHERE nick_name LIKE %s OR chatroom_id LIKE %s
        ORDER BY nick_name
        LIMIT %s OFFSET %s
        """
        search_param = f"%{keyword}%"
        cursor.execute(query, (search_param, search_param, limit, offset))
    else:
        # 搜索所有类型
        query = """
        (SELECT 'friend' as type, id, wxid as contact_id, nick_name, head_img_url FROM friends
         WHERE nick_name LIKE %s OR wxid LIKE %s)
        UNION
        (SELECT 'chatroom' as type, id, chatroom_id as contact_id, nick_name, head_img_url FROM chatrooms
         WHERE nick_name LIKE %s OR chatroom_id LIKE %s)
        ORDER BY nick_name
        LIMIT %s OFFSET %s
        """
        search_param = f"%{keyword}%"
        cursor.execute(query, (search_param, search_param, search_param, search_param, limit, offset))
    
    results = cursor.fetchall()
    cursor.close()
    return results 