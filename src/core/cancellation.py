"""
处理取消相关的共享定义。
"""


class ProcessingCancelledError(Exception):
    """用户主动取消当前处理任务。"""

