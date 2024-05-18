import logging
from logging.config import dictConfig
import os
import traceback

# ログファイルのディレクトリを作成（存在しない場合）
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# ロギング設定
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'access_log': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 15,
            'filename': os.path.join(log_directory, 'access.log'),
            'formatter': 'default',
        },
        'error_log': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 15,
            'filename': os.path.join(log_directory, 'error.log'),
            'formatter': 'default',
        },
        'exception_log': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 15,
            'filename': os.path.join(log_directory, 'exception.log'),
            'formatter': 'default',
        },
    },
    'loggers': {
        'uvicorn.access': {
            'handlers': ['access_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'uvicorn.error': {
            'handlers': ['error_log'],
            'level': 'ERROR',
            'propagate': False,
        },
        'app.exception': {
            'handlers': ['exception_log'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


dictConfig(LOGGING_CONFIG)

def log_error(e: Exception) -> None:
    error_logger = logging.getLogger("app.exception")
    detailed_tb = get_error_message(e)
    error_logger.error(f"An error occurred: {e}\n{detailed_tb}")
    
def get_error_message(e: Exception) -> str:
    tb = traceback.format_exception(type(e), e, e.__traceback__)
    return "".join(tb[::-1]) # 逆順にしてスタックトレースを取得