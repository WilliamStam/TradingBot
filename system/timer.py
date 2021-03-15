import time
from contextlib import contextmanager

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    # timers: Dict[str, float] = dict()
    # name: Optional[str] = None
    # text: str = "Elapsed time: {:0.4f} seconds"
    # logger: Optional[Callable[[str], None]] = print
    # _start_time: Optional[float] = field(default=None, init=False, repr=False)


    def __init__(self,text="{name}, Elapsed time: {total:0.3f} seconds",logger=None):
        self.timers = dict()
        self.text = text
        self.logger = logger

        self.last_timer = None
        self.__started = time.time()


    def setText(self,text):
        self.text = text
    def setLogger(self,logger):
        self.logger = logger


    def start(self,name:str) -> None:
        self.last_timer = self.timers.setdefault(name, {
            "name":name,
            "start":time.time(),
            "end":None,
            "total":None
        })
        

    def stop(self,name:str=None)->float:

        timer = self.last_timer
        if name:
            if self.timers.get(name) is None:
                raise TimerError(f"No Timer with that label {name}")
            timer = self.timers.get(name)

        timer['end'] = time.time()
        timer['total'] = time.time() - timer['start']


        # print(timer)

        elapsed_time = timer['total']
        # elapsed_time = time.perf_counter() - timer.start
        # timer['total'] = elapsed_time

        # # Report elapsed time
        if self.logger:
            self.logger(self.text.format(**timer))
        

        return elapsed_time

    def show(self):
        t = dict()
        for x in self.timers:
            t[x] = self.timers[x]['total']
        return t

    def total(self):
        return time.time() - self.__started

    @contextmanager
    def timer(self,name):
        self.start(name)
        try:
            yield
        finally:
            self.stop(name)


