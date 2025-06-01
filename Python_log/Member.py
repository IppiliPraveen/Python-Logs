# Member.py
from Utility.logging_config import logger

log = logger(__name__)  # Creates a logger with the module name

def getMember():
    log.debug("Debug message for internal testing")
    log.info("Info message for standard operation")
    log.warning("Warning message for potential issues")
    log.error("Error message when something fails")
    log.critical("Critical issue encountered")
    name="Praveen"
    id="1029526"
    return name + " " + id
