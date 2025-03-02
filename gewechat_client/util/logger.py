import logging
from logging.handlers import RotatingFileHandler
import os
from colorama import init, Fore, Style

# 初始化colorama
init()

class ColoredFormatter(logging.Formatter):
    """为不同级别的日志添加颜色"""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        # 保存原始消息和级别名称
        if not hasattr(record, 'raw_msg'):
            record.raw_msg = record.msg
            record.raw_levelname = record.levelname
            
        # 如果消息是字典，美化输出
        if isinstance(record.msg, dict):
            import json
            record.msg = json.dumps(record.msg, ensure_ascii=False, indent=2)
            
        # 使用原始的级别名称来查找颜色
        if record.raw_levelname in self.COLORS:
            color = self.COLORS[record.raw_levelname]
            record.levelname = f"{color}{record.raw_levelname}{Style.RESET_ALL}"
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
            
        return super().format(record)

# 创建日志目录
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
log_file = os.path.join(log_dir, 'app.log')

# 文件处理器
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
file_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# 控制台处理器
console_handler = logging.StreamHandler()
console_formatter = ColoredFormatter(
    '%(asctime)s │ %(levelname)-8s │ %(name)s:%(lineno)d │ %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(console_formatter)

# 配置logger
logger = logging.getLogger(__name__)
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))
logger.addHandler(file_handler)
logger.addHandler(console_handler) 