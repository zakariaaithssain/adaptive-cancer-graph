import os
import logging

from config.log_config import LOG_OPTIONS

"""deleting the older logs file, because I am using 'a' mode for the file. 
This is to prevent having a logs file that contains all logs
 from my very first time running the script.
 configuring logs from __init__ file of the modules is the best place in my opinion."""

def initialize_logs():
    if os.path.exists(LOG_OPTIONS["file_handler"]): 
        os.remove(LOG_OPTIONS["file_handler"]) 

    logging.basicConfig(level=LOG_OPTIONS["level"], format=LOG_OPTIONS["format"],
    handlers=[

                logging.FileHandler(LOG_OPTIONS["file_handler"], mode= LOG_OPTIONS["mode"])
                                    
                ]
                )
    logging.info("Logs file initialized.")  


initialize_logs()

 