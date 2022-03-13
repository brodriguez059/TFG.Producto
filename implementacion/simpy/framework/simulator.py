from queue import PriorityQueue
import pandas as pd
import numpy as np

from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

class Simulator:
    def __init__(self,
                 in_variables,
                 state_variables,
                 count_variables,
                 out_variables,
                 stop_condition,
                 sucesos,
                 seed=None,
                 simulations=1,
                 clock = 0.0,
                 ):
        # Important structures:
        self.lsuc = PriorityQueue()

        # Read-only:
        # # Variables exógenas (o de entrada)
        self.seed = seed
        self.simulations = simulations
        if type(in_variables) == list:
            self.in_variables = {iv:None for iv in in_variables}
        elif type(in_variables) == dict: # Allows for setting defaults
            self.in_variables = in_variables

        # Read-write:
        # # Variables endógenas (o de estado)
        self.clock = clock
        if type(state_variables) == list:
            self.state_variables = {st:None for st in state_variables}
        elif type(state_variables) == dict:
            self.state_variables = state_variables

        # # Contadores estadísticos
        if type(count_variables) == list:
            self.count_variables = {ct:None for ct in count_variables}
        elif type(count_variables) == dict:
            self.count_variables = count_variables

        # Write-only:
        self.out_variables = pd.DataFrame(
            columns=[out_variables]
        ) # Also known as our "informe"

        # Rutinas de sucesos
        self.sucesos = sucesos

        # Stop condition
        self.stop = stop_condition

    def temporizador(self):
        suc = self.lsuc.get()
        self.clock = suc.priority
        tipo = suc.item['type']
        data = None
        if 'data' in suc.item:
            data = suc.item['data']
        return (self.sucesos[tipo], data)# Call the corresponding function

    def inicializar(self):
        np.random.seed(self.seed)
        # Initialize the state
        self.clock = 0.0
        # Empty the event list
        while not self.lsuc.empty():
            self.lsuc.get()
        # Add the Starting event
        self.lsuc.put(PrioritizedItem(0.0, {'type': 0}))

    def insertar_suceso(self, tiempo, tipo, data = None):
        item = {'type':tipo}
        if data:
            item.update({'data':data})
        self.lsuc.put(PrioritizedItem(tiempo, item))

    def __call__(self):
        for i in range(self.simulations):
            self.inicializar()
            while not self.stop(self):
                suceso,data = self.temporizador()
                suceso(self,data)
