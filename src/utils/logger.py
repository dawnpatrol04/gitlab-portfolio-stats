import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    # Create a logger with the provided name
    logger = logging.getLogger(logger_name)
    
    # Set the logging level (e.g., INFO, DEBUG, ERROR, etc.)
    logger.setLevel(level)
    
    # Define the format for the log messages
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    
    # Setup file handler to write logs to a file
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    
    # Setup stream handler to write logs to the console
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    
    return logger
