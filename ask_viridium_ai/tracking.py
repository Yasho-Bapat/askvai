import os
import dotenv
import pandas as pd
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

dotenv.load_dotenv()


class AppInsightsConnector:
    def __init__(self):
        self.ai_conn_string = os.getenv("APPINSIGHTS_CONNECTION_STRING")

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Azure App Insights Handler
        self.azure_handler = AzureLogHandler(connection_string=self.ai_conn_string)
        self.logger.addHandler(self.azure_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler("data_dump/log.log")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
