import numpy as np
import pandas as pd

from queue import PriorityQueue # For the heap

from dataclasses import dataclass, field # For struct-like classes
from typing import Any, Callable, Tuple, Union # For static typing


# TODO Add a special kind of class for variables inside the simulator (this class can control nominal and numerical values. It should also be capable of assigning ranges or restrictions)
# TODO Add a special kind of class for statistical metrics

@dataclass(order=True)
class PrioritizedItem:
    """
    Dataclass to stored information inside a PriorityQueue given an item that is not comparable.
    """
    priority: int # The priority value (or time in our case)
    item: Any = field(compare=False) # The data to be stored (or the event type and its additional data in our case)


class Simulator:
    """
    Simulator class. It is responsible of carrying the whole simulation of a
    given model. In order for it to work, one must provide first a set of
    initial variables, state varibles and statistical counters. One must also
    specify new event types, a stop condition and a set of statistical metrics
    to evaluate the simulation.
    """

    def __init__(self,
                 in_vars: Union[list, dict],
                 state_vars: Union[list, dict],
                 count_vars: Union[list, dict],
                 n_sims: int = 1
                 ):
        """The Simulator Class constructor

        Args:
            in_vars (Union[list, dict]): Also known as endogen variables. A set
            of variables with data that will be treated as read-only. It
            contains the information relevant to the simulation that is set
            outside of it.
            state_vars (Union[list, dict]): A set of variables with data that
            will be treated as read-and-write. It contains the information of
            auxiliary variables useful for carrying out the simulation.
            count_vars (Union[list, dict]): Also known as statistical counters.
            A set of variables with data that will be treated as read-and-write.
            It contains information useful for the final calculation of each
            statistical metric of the simulation.
            n_sims (int, optional): The number of simulations to execute.
            Defaults to 1.
        """
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
            self._exogens = {}
        elif type(in_vars) == list:
            self._exogens = {iv: None for iv in in_vars}
        elif type(in_vars) == dict:  # Allows for setting defaults
            self._exogens = in_vars

        # Read-Write
        if state_vars == None:
            self._endogens = {}
        if type(state_vars) == list:
            self._endogens = {st: None for st in state_vars}
        elif type(state_vars) == dict:
            self._endogens = state_vars

        if count_vars == None:
            self._counters = {}
        elif type(count_vars) == list:
            self._counters = {ct: None for ct in count_vars}
        elif type(count_vars) == dict:
            self._counters = count_vars

        # Write-only
        self._metrics = {}

        # Summary data
        self._summary = pd.DataFrame()

    @property
    def clock(self) -> float:
        """Access the value of the clock of the simulation.

        Returns:
            float: The current value of the clock.
        """
        return self._clock

    @property
    def sim_index(self) -> int:
        """Access the value of the simulation index.

        Returns:
            int: The index number of the simulation that is currently being executed.
        """
        return self._sim_index

    def initialize(self):  # Simulator initializer
        """
        Initializes the default information of the simulation and adds the
        initial event to the event list.
        """
        # Set a seed for the random number generators
        np.random.seed(self._seed)

        # Initialize the state
        self._clock = 0.0

        # Empty the event list
        while not self._event_list.empty():
            _ = self._event_list.get()

        # Add the Starting event
        self.spawn(0.0, 'Inicio')

    def timer(self) -> Tuple[Callable, dict]:  # Timer
        """Changes the current value of the clock of the simulation and gets the
        information of the event that must be executed alongside any additional
        data that it might require.

        Returns:
            Tuple[Callable, dict]: A tuple containing a callable for the event
            to be executed and a dictionary with additional data.
        """
        # We get the event
        event_data: PrioritizedItem = self._event_list.get()

        # Advance the clock
        self._clock = event_data.priority

        # Get the type of the event
        tipo = event_data.item['event_name']

        # Additional data
        data = None
        if 'data' in event_data.item:
            data = event_data.item['data']

        # Return the event callable alongside any additional data that might be required
        return (self._event_callables[tipo], data)

    # Event functions
    def event(self, event_name: str, **options):
        """
        Decorator used to specify and add a new type of event to the simulation.

        Args:
            event_name (str): _description_
        """
        def decorator(f):
            self.add_event_function(event_name, f, **options)
            return f
        return decorator

    def add_event_function(self,
                           event_name: str,
                           view_func: Callable = None,
                           **options
                           ) -> None:
        """
        Method used to specify and add a new type of event to the simulation.

        Args:
            event_name (str): The name or type of the event
            view_func (Callable, optional): A callable function that contains
            the instructions to be executed when the event happens. Defaults to
            None.
        """
        self._event_callables.update({event_name: view_func})

    def spawn(self, time: Union[float, int], event_name: str, data: dict = None):
        """Generates a new event given its time and type.

        Args:
            time (Union[float, int]): The time when the event must happen.
            event_name (str): The type of the event that will happen.
            data (dict, optional): Any additional data that the event might require for its execution. Defaults to None.
        """
        item = {'event_name': event_name}
        if data:
            item.update({'data': data})
        self._event_list.put(PrioritizedItem(time, item))

    # Summary generator
    def summarize_simulation(self):
        """
        Calculates the value of each metric of the simulation and adds them to
        the general summary of the simulation. The calculations are done once
        the stop condition evaluates to true.
        """
        values = []
        columns = []
        for key, metric_callable in self._metrics.items():
            values.append(metric_callable(self._endogens,
                          self._exogens, self._counters)[0])
            columns.append(key)
        row = pd.Series(data=values, index=columns, name=self._sim_index)
        new_df = pd.DataFrame([row])
        # self._summary = self._summary.append(row)
        self._summary = pd.concat([self._summary, new_df], axis=0)

    # Stop condition
    def stop(self, **options):
        """
        Decorator used to specify and add the stop condition of the simulator.
        """
        def decorator(f):
            self.add_stop_condition(f)
            return f
        return decorator

    # Add the stop condition
    def add_stop_condition(self, stop_func: Callable = None) -> None:
        """Method used to specify and add the stop condition of the simulation.

        Args:
            stop_func (Callable, optional): The function that serves as the stop condition. Defaults to None.
        """
        if self._stop_condition == None:  # Singleton. You can only have 1 stop condition
            self._stop_condition = stop_func

    # Metrics
    def metric(self, metric_name: str, **options):
        """
        Decorator used to add a new statistical metric to the simulation.

        Args:
            metric_name (str): The name of the new metric
        """
        def decorator(f):
            self.add_metric(metric_name, f, **options)
            return f
        return decorator

    # Add the stop condition
    def add_metric(self,
                   metric_name: str,
                   metric_func: Callable = None,
                   **options
                   ) -> None:
        """Method used to specify and add the stop condition of the simulation.

        Args:
            metric_name (str): The name of the new metric.
            metric_func (Callable, optional): The function that calculates the
            value of the new metric given the fact that the calculation will be
            made once the simulation stops. Defaults to None.
        """
        self._metrics.update({metric_name: metric_func})

    # Main loop
    def __call__(self):  # Executer
        """The main loop of the simulation. Executes its events until there are
        no more events to call or the stop condition evaluates to true.

        Returns:
            The final information of the evaluation metrics of the simulation.
        """
        # For each simulation to be carried out...
        for self._sim_index in range(self._n_sims):
            # Initialize the simulation
            self.initialize()
            # While there are events to be called or the stop condition evaluates to false...
            while not (self._event_list.empty() or self._stop_condition(self._exogens, self._endogens, self._counters)):
                # Get the event callable and its additional data
                event_callable, data = self.timer()
                # Execute the event
                event_callable(self._exogens, self._endogens,
                               self._counters, data)
            # Once outside the loop, calculate the statistical metrics
            self.summarize_simulation()
        # Once all simulations have been finished. Calculate the mean and standard deviation of the evaluation metrics.
        # Mean:
        row = self._summary.mean()
        row.rename("Media", inplace=True)
        new_df = pd.DataFrame([row])
        self._summary = pd.concat([self._summary, new_df], axis=0)

        # Std:
        row = self._summary.std()
        row.rename("Desv. Típ", inplace=True)
        new_df = pd.DataFrame([row])
        self._summary = pd.concat([self._summary, new_df], axis=0)

        # Return the final data
        return self._summary
