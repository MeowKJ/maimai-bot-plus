# my_database_lib/exceptions.py

class UserNotFoundError(Exception):
    """表示用户未找到的异常"""
    pass

class DatabaseOperationError(Exception):
    """表示数据库操作错误的异常"""
    pass
