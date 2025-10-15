# import logging
# import os
# import sys
# from logging.handlers import RotatingFileHandler
#
#
# class Logger:
#     BASE_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
#     os.makedirs(BASE_LOG_DIR, exist_ok=True)  # ساخت پوشه log در صورت عدم وجود
#
#     APP_LOG = os.path.join(BASE_LOG_DIR, "app.log")
#     ERROR_LOG = os.path.join(BASE_LOG_DIR, "error.log")
#     DEBUG_LOG = os.path.join(BASE_LOG_DIR, "debug.log")
#
#     NOTICE_LEVEL = 25
#     logging.addLevelName(NOTICE_LEVEL, "NOTICE")
#
#     # Logger اصلی
#     logger = logging.getLogger("timo_bot")
#     logger.setLevel(logging.DEBUG)
#
#     if not logger.handlers:
#         formatter = logging.Formatter(
#             '%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s',
#             datefmt='%Y-%m-%d %H:%M:%S'
#         )
#
#         # --- app.log ---
#         app_handler = RotatingFileHandler(APP_LOG, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
#         app_handler.setLevel(logging.INFO)
#         app_handler.setFormatter(formatter)
#         logger.addHandler(app_handler)
#
#         # --- error.log ---
#         error_handler = RotatingFileHandler(ERROR_LOG, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
#         error_handler.setLevel(logging.ERROR)
#         error_handler.setFormatter(formatter)
#         logger.addHandler(error_handler)
#
#         # --- debug.log ---
#         debug_handler = RotatingFileHandler(DEBUG_LOG, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
#         debug_handler.setLevel(logging.DEBUG)
#         debug_handler.setFormatter(formatter)
#         logger.addHandler(debug_handler)
#
#     @staticmethod
#     def notice(message, *args, **kwargs):
#         """Log in Notice Level"""
#         if Logger.logger.isEnabledFor(Logger.NOTICE_LEVEL):
#             Logger.logger._log(Logger.NOTICE_LEVEL, message, args, **kwargs)
#
#
# # -----------------------------
# # ثبت خطاهای uncaught
# def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
#     if issubclass(exc_type, KeyboardInterrupt):
#         # اجازه می‌دهد Ctrl+C برنامه را متوقف کند
#         sys.__excepthook__(exc_type, exc_value, exc_traceback)
#         return
#     Logger.logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
#
#
# sys.excepthook = handle_uncaught_exception

import logging
import os


class Logger:
    LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.log")

    logging.basicConfig(filename=LOG_FILE_PATH,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filemode="w",
                        datefmt='%Y-%m-%d %H:%M:%S',
                        encoding="utf-8")

    NOTICE_LEVEL = 25
    logging.addLevelName(NOTICE_LEVEL, "NOTICE")

    @staticmethod
    def notice(message, *args, **kwargs):
        logger = logging.getLogger(__name__)
        if logger.isEnabledFor(Logger.NOTICE_LEVEL):
            logger._log(Logger.NOTICE_LEVEL, message, args, **kwargs)

    logger = logging.getLogger(__name__)


