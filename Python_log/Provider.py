# Privder.py
from Utility.logging_config import logger

log = logger(__name__)  # Creates a logger with the module name

def getProvider():
    log.debug("Provider Debug message for internal testing")
    log.info(" ProviderInfo message for standard operation")
    log.warning(" Provider Warning message for potential issues")
    log.error(" Provider Error message when something fails")
    log.critical(" Provider Critical issue encountered")
    name="Praveen"
    id="1029526"
    return name + " " + id