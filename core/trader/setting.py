"""
Global setting of the trading platform.
"""

from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone_name

from .utility import load_json

SETTINGS: Dict[str, Any] = {
    "font.family": "微软雅黑",
    "font.size": 12,
    # 日志器配置
    "log.active": True,  # 日志启用
    "log.level": CRITICAL,  # 记录等级
    "log.console": True,  #
    "log.file": True,
    # 邮件服务器配置
    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",
    # 服务器数据服务配置
    "datafeed.name": "zquant_binancedata",
    "datafeed.username": "zzy",
    "datafeed.password": "123456",
    # 本地数据库配置
    "database.timezone": get_localzone_name(),
    "database.name": "mysql",
    "database.database": "vnpy_test",
    "database.host": "127.0.01",
    "database.port": 3306,
    "database.user": "root",
    "database.password": "123456"
}

# Load global setting from json file.从json文件加载全局设置
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    """搜索配置"""
    prefix_length: int = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
