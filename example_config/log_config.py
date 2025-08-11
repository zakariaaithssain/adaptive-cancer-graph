import logging 

LOG_OPTIONS = {"level" : logging.INFO,
                "format" : '%(asctime)s - %(levelname)s - %(message)s',
                "file_handler": f"./project_logs.log",
                "mode" : "a"}