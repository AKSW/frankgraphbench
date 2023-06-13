from threading import Thread
import queue

class Worker(Thread):
    def __init__(self, request_queue, query_function, pbar=None):
        """
        Parameters:
            request_queue: queue containing requests to be consumed by workers
            query_function: function to make the query to the endpoint
            pbar: tqdm progressbar to be updated after each query
        """
        super().__init__()
        self.queue = request_queue
        self.local_results = []
        self.query = query_function
        self.pbar = pbar
    
    def run(self):
        while True:
            try:
                idx, params = self.queue.get(block=False)
                response = self.query(params)
                self.local_results.append((idx, response))
                if self.pbar is not None:
                    self.pbar.update(n=1)
                self.queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                print(f'Exception:')
                print(e)    