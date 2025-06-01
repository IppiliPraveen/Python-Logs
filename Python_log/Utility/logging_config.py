import logging
import os
import sys
from datetime import datetime
import configparser
import warnings

# Custom log level for STDOUT
STDOUT_LEVEL_NUM = 15
logging.addLevelName(STDOUT_LEVEL_NUM, "STDOUT")

def stdout(self, message, *args, **kwargs):
    if self.isEnabledFor(STDOUT_LEVEL_NUM):
        self._log(STDOUT_LEVEL_NUM, message, args, **kwargs)

logging.Logger.stdout = stdout

# Deprecation-safe warning method
def warn(self, msg, *args, **kwargs):
    if 'stacklevel' in kwargs:
        self._log(logging.WARNING, msg, args, **kwargs)
    else:
        self._log(logging.WARNING, msg, args, stacklevel=3, **kwargs)

logging.Logger.warn = warn
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*warn.*deprecated.*")


logger_file_map = {}

def get_logger_file_map(base_dir='.', exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'venv', '__pycache__', '.git', '.idea'}

    logger_map = {}
    for file in os.listdir(base_dir):
        if file.endswith('.py') and os.path.isfile(os.path.join(base_dir, file)):
            logger_name = file[:-3]
            logger_map[logger_name] = os.path.abspath(os.path.join(base_dir, file))
    return logger_map

logger_file_map = get_logger_file_map()

def get_log_directory():
    # Construct the full path to 'Configration/config.ini'
    config_file_path = os.path.join(os.getcwd(), 'Configration', 'config.ini')
    print(f"The config.ini directory is: '{os.path.dirname(config_file_path)}'")

    config = configparser.ConfigParser()
    config.read(config_file_path)

    try:
        return config['logging']['log_directory']
    except KeyError:
        raise KeyError("Missing [logging] section or log_directory key in config.ini")

# Stream redirect class
class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            if line.strip():
                self.logger.log(self.log_level, line.rstrip(), stacklevel=3)

    def flush(self):
        pass

# Uncaught exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.getLogger("ERROR").error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Logger initialization function
def loggers(log_level=logging.ERROR):
    log_directory = get_log_directory()
    os.makedirs(log_directory, exist_ok=True)

    log_date = datetime.now().strftime("%d%m%Y")
    log_filename = f"referanceapplog_{log_date}.log"
    log_path = os.path.join(log_directory, log_filename)

    if not logging.getLogger().handlers:
        # Root logger
        handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-8s - %(filename)-20s:%(lineno)-4d - %(message)s'))

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)
        root_logger.addHandler(logging.StreamHandler())
        logger_file_map[root_logger.name] = log_filename

    # Redirect sys.stdout and stderr
    sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), STDOUT_LEVEL_NUM)
    sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)
    sys.excepthook = handle_exception

    # === Console-only handlers for werkzeug and flask ===
    console_handler = logging.StreamHandler(sys.__stdout__)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    # Werkzeug logger (Flask dev server output)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.propagate = False
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(console_handler)

    # Flask app logger
    flask_logger = logging.getLogger('flask.app')
    flask_logger.propagate = False
    flask_logger.setLevel(logging.INFO)
    flask_logger.handlers.clear()
    flask_logger.addHandler(console_handler)

# Get a named logger
def logger(name=None):
    log = logging.getLogger(name)
    if name not in logger_file_map:
        logger_file_map[name] = 'referanceapplog_' + datetime.now().strftime("%d%m%Y") + ".log"
    return log
