import logging
import sys

# Get Logger
logger = logging.getLogger(__name__)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create handler
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('logs/app.log')

# set formatter
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.handlers = [stream_handler, file_handler]

# log will not be printed in the terminal
# # set formatter
# file_handler.setFormatter(formatter)
# # Add handlers to the logger (only file handler in this case)
# logger.handlers = [file_handler]

# Set log level
logger.setLevel(logging.INFO)