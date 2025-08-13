# -*- encoding: utf-8 -*-
'''
@File    :   log_record.py
@Time    :   2020/04/04
@Author  :   Coder-Sakura
@Version :   1.0
@Desc    :   log
'''

# here put the import lib
import os
import sys
from loguru import logger
from config import DEBUG
import threading
import re
import atexit

if DEBUG:
    level = "DEBUG"
else:
    level = "INFO"

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")

# remove default handler
logger.remove()

# ============== 控制台单行汇聚日志（多前缀） ==============
_agg_state = {
    "active": False,      # 是否处于单行显示状态
    "width": 0,           # 当前行宽，用于清除
    "count": 0,           # 当前类别累计计数
    "category": None,     # 当前类别标识
}
_agg_lock = threading.Lock()
_ansi_re = re.compile(r"\x1b\[[0-9;]*m")

def _visible_len(text: str) -> int:
    try:
        return len(_ansi_re.sub("", text))
    except Exception:
        return len(text)
def _erase_line():
    """清除整行内容并将光标回到行首。"""
    try:
        # ANSI: 清除整行并回到行首，兼容支持虚拟终端的 Windows 终端/PowerShell 7+
        sys.stderr.write("\r\x1b[2K\r")
        # 兼容降级：若终端不支持 ANSI，则用空格覆盖当前记录宽度
        if _agg_state.get("width", 0) > 0:
            sys.stderr.write(" " * _agg_state["width"]) 
            sys.stderr.write("\r")
        sys.stderr.flush()
    except Exception:
        pass


def _is_skip_message(record):
    try:
        msg = record.get("message", "")
        return isinstance(msg, str) and msg.startswith("SKIP_ISEXISTS_ILLUST")
    except Exception:
        return False


def _is_bookmark_now_message(record):
    try:
        msg = record.get("message", "")
        return isinstance(msg, str) and msg.startswith("Pixiv收藏作品第")
    except Exception:
        return False


def _is_skip_db_message(record):
    try:
        msg = record.get("message", "")
        return isinstance(msg, str) and msg.startswith("SKIP_DB_EXISTS_ILLUST")
    except Exception:
        return False


def _clear_agg_line():
    if _agg_state["active"]:
        _erase_line()
        _agg_state["active"] = False
        _agg_state["width"] = 0
        _agg_state["count"] = 0
        _agg_state["category"] = None


def _general_console_sink(message: str):
    # 在输出其他日志前，若存在单行聚合状态，则先清除该行
    with _agg_lock:
        _clear_agg_line()
    sys.stderr.write(message)


def _agg_write(category: str, message: str):
    # 单行动态刷新聚合输出
    with _agg_lock:
        # 切换类别时清空行并重置计数
        if _agg_state["category"] != category:
            _clear_agg_line()
            _agg_state["category"] = category
        _agg_state["count"] += 1
        text = f"{message.strip()} (x{_agg_state['count']})"
        try:
            # 使用 ANSI 清行，避免多字节/颜色转义导致的残留
            _erase_line()
            sys.stderr.write("\r" + text)
            sys.stderr.flush()
            _agg_state["active"] = True
            _agg_state["width"] = _visible_len(text)
        except Exception:
            sys.stderr.write(message + "\n")


def _skip_console_sink(message: str):
    _agg_write("skip_exists", message)


def _bookmark_now_console_sink(message: str):
    _agg_write("bookmark_now", message)


# 控制台输出（常规日志，不包括单行聚合的行）
logger.add(
    _general_console_sink,
    level=level,
    filter=lambda record: not (
        _is_skip_message(record) or _is_bookmark_now_message(record) or _is_skip_db_message(record)
    ),
    colorize=True
)

# 控制台输出（仅处理以 SKIP_ISEXISTS_ILLUST 开头的行，单行动态刷新）
logger.add(
    _skip_console_sink,
    level=level,
    filter=lambda record: _is_skip_message(record),
    format="<level>{message}</level>",
    colorize=True
)

# 控制台输出（仅处理 BOOKMARK_NOW_INFO 行，单行动态刷新）
logger.add(
    _bookmark_now_console_sink,
    level=level,
    filter=lambda record: _is_bookmark_now_message(record),
    format="<level>{message}</level>",
    colorize=True
)

# 控制台输出（仅处理 SKIP_DB_EXISTS_ILLUST 行，单行动态刷新）
def _skip_db_console_sink(message: str):
    _agg_write("skip_db_exists", message)


logger.add(
    _skip_db_console_sink,
    level=level,
    filter=lambda record: _is_skip_db_message(record),
    format="<level>{message}</level>",
    colorize=True
)

# 程序结束时，确保清除聚合行，避免残留
def _agg_finalize():
    try:
        with _agg_lock:
            _clear_agg_line()
    except Exception:
        pass

atexit.register(_agg_finalize)

# 日志写入文件（保持原状，包含所有日志）
logger.add(
    os.path.join(log_path, "{time}.log"),
    encoding="utf-8",
    rotation="00:00",
    enqueue=True,
    level=level
)


# def log_str(*args, end=None):
#     for i in args:
#         print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S"),i),end=end)