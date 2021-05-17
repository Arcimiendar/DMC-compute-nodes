import time


class TimedDict(dict):
    # Proxy to the dict, that allows create key-item pairs with lazy ttl functionality
    def __init__(self, ttl):
        self.ttl = ttl
        self.ttls = dict()
        self.dict = dict()
        super(TimedDict, self).__init__()

    def __contains__(self, item):
        return self.__getattribute__('__contains__')(item)
        
    def __getattribute__(self, item):
        if item in ('ttls', 'ttl', 'dict', '__setitem__', '__delitem__', 'clear'):
            return super(TimedDict, self).__getattribute__(item)

        now = time.time()
        copy = self.ttls.copy()
        for key, value in copy.items():
            if now - value > self.ttl:
                del self.ttls[key]
                del self.dict[key]

        return self.dict.__getattribute__(item)

    def __setitem__(self, key, value):
        self.dict[key] = value
        self.ttls[key] = time.time()

    def __delitem__(self, key):
        self.dict.__delitem__(key)
        self.ttls.__delitem__(key)

    def clear(self) -> None:
        self.ttls.clear()
        self.dict.clear()
