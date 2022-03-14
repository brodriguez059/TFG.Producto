import numpy as np
import pandas as pd

from queue import PriorityQueue

from dataclasses import dataclass, field
from typing import Any


# TODO Add a special kind of class for variables inside the simulator (this class can control nominal and numerical values. It should also be capable of assigning ranges or restrictions)
# TODO Add a special kind of class for statistical metrics

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

class Simulator:
    def __init__(self,
                 in_vars,
                 state_vars,
                 count_vars,
                 n_sims = 1
                 ):
        # Simulator's basic variables
        self._clock = 0.0
        self._seed = None
        self._n_sims = n_sims
        self._sim_index = 0

        # Event management
        self._event_list = PriorityQueue()
        self._event_callables = {}

        # Stop condition
        self._stop_condition = None

        # Read-Only
        if in_vars == None:
            self._exogens  = {}
        elif type(in_vars) == list:
            self._exogens = {iv:None for iv in in_vars}
        elif type(in_vars) == dict: # Allows for setting defaults
            self._exogens = in_vars

        # Read-Write
        if state_vars == None:
            self._endogens = {}
        if type(state_vars) == list:
            self._endogens = {st:None for st in state_vars}
        elif type(state_vars) == dict:
            self._endogens = state_vars

        if count_vars == None:
            self._counters = {}
        elif type(count_vars) == list:
            self._counters = {ct:None for ct in count_vars}
        elif type(count_vars) == dict:
            self._counters = count_vars

        # Write-only
        self._metrics  = {}

        # Summary data
        self._summary = pd.DataFrame()

    @property
    def clock(self):
        return self._clock

    @property
    def sim_index(self):
        return self._sim_index

    def initialize(self): # Simulator initializer
        np.random.seed(self._seed)
        # Initialize the state
        self._clock = 0.0
        # Empty the event list
        while not self._event_list.empty():
            _ = self._event_list.get()
        # Add the Starting event
        self.spawn(0.0, 'Inicio')

    def timer(self): # Timer
        event_data : PrioritizedItem = self._event_list.get()
        self._clock = event_data.priority
        tipo = event_data.item['event_name']
        data = None
        if 'data' in event_data.item:
            data = event_data.item['data']
        return (self._event_callables[tipo], data) # Return the event callable alongside any additional data that might be required

    # Event functions
    def event(self, event_name: str, **options):
        def decorator(f):
            self.add_event_function(event_name, f, **options)
            return f
        return decorator

    def add_event_function(self,
        event_name : str,
        view_func = None,
        **options
    ) -> None:
        self._event_callables.update({event_name:view_func})

    def spawn(self, time, event_name, data = None):
        item = {'event_name': event_name}
        if data:
            item.update({'data': data})
        self._event_list.put(PrioritizedItem(time, item))

    # Summary generator
    def summarize_simulation(self):
        values = []
        columns = []
        for key,metric_callable in self._metrics.items():
            values.append(metric_callable(self._endogens, self._exogens, self._counters)[0])
            columns.append(key)
        row = pd.Series(data=values, index=columns, name=self._sim_index)
        new_df = pd.DataFrame([row])
        # self._summary = self._summary.append(row)
        self._summary = pd.concat([self._summary, new_df], axis=0)

    # Stop condition
    def stop(self, **options):
        def decorator(f):
            self.add_stop_condition(f)
            return f
        return decorator

    # Add the stop condition
    def add_stop_condition(self, stop_func = None) -> None:
        if self._stop_condition == None: # Singleton. You can only have 1 stop condition
            self._stop_condition = stop_func

    # Metrics
    def metric(self, metric_name: str, **options):
        def decorator(f):
            self.add_metric(metric_name, f, **options)
            return f
        return decorator

    # Add the stop condition
    def add_metric(self,
        metric_name : str,
        metric_func = None,
        **options
    ) -> None:
        self._metrics.update({metric_name:metric_func})

    # Main loop
    def __call__(self): # Executer
        for self._sim_index in range(self._n_sims):
            self.initialize()
            while not (self._event_list.empty() or self._stop_condition(self._exogens, self._endogens, self._counters)):
                event_callable, data = self.timer()
                event_callable(self._exogens, self._endogens, self._counters, data)
            self.summarize_simulation()
        row = self._summary.mean()
        row.rename("Media",inplace=True)
        new_df = pd.DataFrame([row])
        self._summary = pd.concat([self._summary, new_df], axis=0)
        row = self._summary.std()
        row.rename("Desv. Típ", inplace=True)
        new_df = pd.DataFrame([row])
        self._summary = pd.concat([self._summary, new_df], axis=0)
        return self._summary