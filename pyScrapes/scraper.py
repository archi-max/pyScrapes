from queue import Queue
import threading
import json
from selenium.webdriver import Chrome, Edge, Safari, Firefox
from typing import TypeVar, Any
import time

WebDriver = Chrome | Edge | Safari | Firefox
_T = TypeVar("_T")

class DataItem: # Class used for entering data and ids in queues.
    data: Any
    id: Any

    def __init__(self, data, data_id):
        self.data = data
        self.id = data_id

    def from_iterable(self, data_list, id_list):
        if len(data_list) != len(id_list):
            raise Exception("Length of data list and id list should be equal")
        return [self.__class__(data_list[i], id_list[i]) for i in range(data_list)]


class UpdateItem: # For storing update data
    data_id: Any
    type: str
    item_data: Any
    update: str

    def __init__(self, data_id, type, item_data, update):
        self.data_id = data_id
        self.type = type
        self.item_data = item_data
        self.update = update

    def __str__(self):
        return f"ID: {self.data_id} STAGE: {self.type} DATA: {self.item_data} UPDATE: {self.update}"

# TODO: Make it such that whenver ordered is True, any DataItem cannot have None as id
class Scraper:

    saving_through = "JSON"

    class DataItemQueue(Queue):

        def __init__(self, item_type, get_status, put_status, updates_queue, *args, **kwargs):
            self.item_type = item_type
            self.get_status = get_status
            self.put_status = put_status
            self.updateQ = updates_queue
            super().__init__(*args, **kwargs)

        def get(self, *args, **kwargs) -> _T:
            # Implement putting updates whenever an item is put or get.
            item: DataItem = super().get(*args, **kwargs)
            self.updateQ.put(UpdateItem(item.id, self.item_type, item.data, self.get_status)) # Update that the item has been taken out of queue
            return item.data, item.id

        def put(self, item: _T, data_id: Any = None, *args, **kwargs) -> None:
            data_item = DataItem(item, data_id)
            self.updateQ.put(UpdateItem(data_item.id, self.item_type, data_item.data,
                                        self.put_status))  # Update that the item has been put in queue
            super().put(data_item, *args, **kwargs)


    def __init__(self ):

        self.updateQ = Queue()
        self.consumer = self.DataItemQueue("input-item", "Processing", "In queue", self.updateQ) # Send data to the scraping script
        self.producer = self.DataItemQueue("output-item", "Saving data", "Processed", self.updateQ) # Save data obtained from scraping

    def get_browser(self) -> WebDriver:
        """Get browser with all the options"""
        pass

    def scrape(self, driver: WebDriver, consumer_queue, producer_queue):
        """Function to be overridden representing the scraping script"""
        pass

    @staticmethod
    def scrape_function(scrape_func, browser_func, ):
        # Function based approach rather than creating whole class.
        pass

    def start(self, iterable=None, order=None,max_workers=10, save_file_path=None, updates=True, saves=True, stop_after_empty=False, stop_after_empty_delay=0):
        self.running = True

        # Start updating
        if updates is True:
            self.updating = True
            update_thread = threading.Thread(target=self.updates_worker)
            update_thread.start()

        # Start the thread to save all data which has been scraped

        if saves:
            self.saves = True
            if save_file_path is None:
                raise Exception("save_file_path needs to be provided if saves are enabled")
            self.save_file_path = save_file_path
            save_worker_thread = threading.Thread(target=self.save_worker)
            save_worker_thread.start()

        self.ordered = None
        if order is None:
            self.ordered = False
        elif type(order) is list:
            self.ordered = True
        else:
            raise Exception("Unknown value for order parameter given")

        # Start monitoring queues for stopping when queues are done

        if stop_after_empty:
            stopper_worker_thread = threading.Thread(target=self.stopper_worker, args=(stop_after_empty_delay,))
            stopper_worker_thread.start()


        # Start the scraper threads
        workers = [threading.Thread(target=self.scrape, args=(self.get_browser(), self.consumer, self.producer)) for work_number in range(max_workers)]
        for worker in workers:
            worker.start()

        # Send all data to be consumed
        if type(iterable) is list:
            if self.ordered is False:
                [self.consumer.put(item) for item in iterable]
            elif len(iterable) == len(order):
                for i, item in enumerate(iterable):
                    self.consumer.put(item, order[i]) # Feed consumer with items
            else:
                raise Exception("Invalid order provided")

        # Wait for all workers to finish
        for worker in workers:
            worker.join()

        if self.saves:
            save_worker_thread.join()

        if self.updating:
            update_thread.join()

        if stop_after_empty:
            stopper_worker_thread.join()

        # Exit
        print("Exited!")

    def save_worker(self):
        print("Save worker started")
        save_file = open(self.save_file_path, "w+")
        while self.running or (self.producer.empty() is False):
            data_to_save, id = self.producer.get()
            # Load existing data
            save_file.seek(0)
            try:
                data: dict = json.load(save_file)
            except json.decoder.JSONDecodeError:
                data = {}
            if data is None:
                data = {}
            # Update data
            if self.ordered == True and id is None:
                raise Exception("Id not provided for data")
            if id is None and self.ordered == False:
                try:
                    save_index = int(sorted(data.keys())[-1])+1
                except IndexError:
                    save_index = 0
                data[save_index] = data_to_save

            else:
                data[id] = data_to_save

            #Save data
            save_file.seek(0)
            json.dump(data, save_file)
            save_file.flush()
        save_file.close()

    def updates_worker(self):
        """Provides updates"""
        print("Updates worker started")
        updates = []
        while self.running or (self.updateQ.empty() is False):
            update = self.updateQ.get()
            print("UPDATE:", update)
            updates.append(update)


    def stop(self):
        self.running = False

    def stopper_worker(self, stop_delay=0):
        """Monitors queues and stops based on provided conditions"""
        while True:
            if self.consumer.empty() and self.producer.empty():
                break
            time.sleep(0.5)
        time.sleep(stop_delay)
        self.running = False