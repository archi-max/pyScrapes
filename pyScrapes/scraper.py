from queue import Queue
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from selenium.webdriver import Chrome, Edge, Safari, Firefox
from typing import TypeVar

WebDriver = Chrome | Edge | Safari | Firefox
_T = TypeVar("_T")

class Scraper:

    class ItemQueue(Queue):
        def get(self, block: bool = ..., timeout: float | None = ...) -> _T:
            # Implement putting updates whenever an item is put or get.
            pass

    def __init__(self, save_filename=None, updates=True, save=True, ):
        self.running = True

        self.consumer = Queue() # Send data to the scraping script
        self.producer = Queue() # Save data obtained from scraping

        if updates:
            self.updates = True
            self.updateQ = Queue()  # Updates for each iterable and each thread worker

        if save:
            self.save_file = save_filename
            self.saves = True

    def get_browser(self) -> WebDriver:
        """Get browser with all the options"""
        pass

    def scrape(self, driver: WebDriver, ):
        """Function to be overridden representing the scraping script"""
        pass

    @staticmethod
    def scrape_function(scrape_func, browser_func):
        # Function based approach rather than creating whole class.
        # How to handle queues?
        pass


    def start(self, iterable=None, max_workers=10):
        # Start the thread to save all data which has been scraped
        if self.saves:
            save_worker_thread = threading.Thread(target=self.save_worker)
            save_worker_thread.start()

        # Start the scraper threads
        workers = [threading.Thread(target=self.scrape, args=(self.get_browser(), )) for work_number in range(max_workers)]
        for worker in workers:
            worker.start()

        # Send all data to be consumed
        if type(iterable) is list:
            for i, item in enumerate(iterable):
                # if self.updates:
                    # self.updateQ.put({"type":"iterable-item", "row":i, "value":item, "update": "In Queue"})  TODO: Update inside queue
                self.consumer.put(item) # Feed consumer with items

        # Wait for all workers to finish
        for worker in workers:
            worker.join()

        if self.saves:
            save_worker_thread.join()

        # Exit

    def save_worker(self):
        pass