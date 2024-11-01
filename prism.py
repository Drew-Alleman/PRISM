from libraries.google.client.google import Google
from libraries.google.authentication.exceptions import ConfigurationException
from loguru import logger
import sys


logger.remove()
logger.add("prism.log", level="INFO", format="{time:YYYY-MM-DD hh:mm:ss A} {level} {message}")
logger.add(sys.stdout, level="DEBUG", format="{time:hh:mm A} {level} {message}")

try:
    google = Google()
except ConfigurationException as e:
    logger.error(e.message)