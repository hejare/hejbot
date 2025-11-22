from multiprocessing import Process
import time
import schedule
from logging import Logger


class Scheduler:
    logger: Logger

    def test_job(self):
        self.logger.info("Job triggered after 10 seconds")
        # Cancel recurring jobs
        return schedule.CancelJob

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        schedule.every(10).seconds.do(self.test_job)

        p = Process(target=self.run)
        p.start()

    def __init__(self, logger: Logger):
        self.logger = logger
