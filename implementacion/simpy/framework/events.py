from functools import wraps

class Event:
    def __init__(self,fn):
        self.function = fn
        # self.simulator = simulator
        # self.tipo = tipo
        # self.data = data

    def __call__(self):
        print("++++")
        res = self.function()
        print("++++")
        return res

@Event
def test():
    return 5

print(test())