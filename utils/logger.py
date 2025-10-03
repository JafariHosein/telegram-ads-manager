import logging
import os


class Logger:
    BASE_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")

    APP_LOG = os.path.join(BASE_LOG_DIR, "app.log")
    ERROR_LOG = os.path.join(BASE_LOG_DIR, "error.log")
    DEBUG_LOG = os.path.join(BASE_LOG_DIR, "debug.log")

    NOTICE_LEVEL = 25
    logging.addLevelName(NOTICE_LEVEL, "NOTICE")

    # Define Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # --- app.log ---
        app_handler = logging.FileHandler(APP_LOG, mode="w", encoding="utf-8")
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        logger.addHandler(app_handler)

        # --- error.log ---
        error_handler = logging.FileHandler(ERROR_LOG, mode="w", encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # --- debug.log ---
        debug_handler = logging.FileHandler(DEBUG_LOG, mode="w", encoding="utf-8")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)



    @staticmethod
    def notice(message, *args, **kwargs):
        """Log in Notice Level"""
        if Logger.logger.isEnabledFor(Logger.NOTICE_LEVEL):
            Logger.logger._log(Logger.NOTICE_LEVEL, message, args, **kwargs)

