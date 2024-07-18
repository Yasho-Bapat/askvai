import multiprocessing
from ask_viridium_ai.tracking import AppInsightsConnector

logger = AppInsightsConnector().get_logger()

max_requests = 1000
max_requests_jitter = 50

log_file = "-"

bind = "0.0.0.0:8000"

workers = (multiprocessing.cpu_count() * 2) + 1

threads = workers

timeout = 120

logger.info(f"Starting with {workers} workers, {threads} threads and a timeout of {timeout} seconds")
