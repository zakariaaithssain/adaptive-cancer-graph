import logging 
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
LOG_OPTIONS = {"level" : logging.INFO,
                "format" : '%(asctime)s - %(levelname)s - %(message)s',
                "file_handler": f"./project_logs_{timestamp}.log",
                "mode" : "a"}