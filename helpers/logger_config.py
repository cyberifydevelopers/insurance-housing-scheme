import logging

LOG_FILE = "newfile.log"

logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    filemode="a",  
    force=True       
)

def get_logger(name):
    """
    Returns a named logger for the calling module
    """
    return logging.getLogger(name)
