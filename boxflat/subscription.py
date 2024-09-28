class Subscription():
    def __init__(self, callback: callable, *args):
        self._callback = callback
        self._args = args


    def call(self, additional=None):
        self._callback(*self._args)


    def call_without_args(self):
        self._callback()


    def call_with_value(self, value):
        self._callback(value, *self._args)


    def call_with_custom_args(self, *args):
        self._callback(*args)


class SubscribtionList():
    def __init__(self):
        self._subscribtions = []


    def append(self, callback: callable, *args):
        if callable(callback):
            self._subscribtions.append(Subscription(callback, *args))

        elif isinstance(Subscription, callback):
            self.append_subscription(callback)


    def append_subscription(self, subscription: Subscription):
        self._subscribtions.append(subscription)


    def call(self, additional=None):
        for sub in self._subscribtions:
            sub.call()


    def call_with_value(self, value):
        for sub in self._subscribtions:
            sub.call_with_value(value)


    def call_without_args(self):
        for sub in self._subscribtions:
            sub.call_without_args()


    def clear(self):
        self._subscribtions.clear()
