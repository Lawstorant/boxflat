class Subscription():
    def __init__(self, callback: callable, *args):
        self._callback = callback
        self._args = args


    def call(self):
        self._callback(*self._args)


    def call_without_args(self):
        self._callback()


    def call_with_value(self, value):
        self._callback(value, *self._args)


    def call_with_custom_args(self, *args):
        self._callback(*args)


class SubscriptionList():
    def __init__(self):
        self._subscriptions = []

    def append(self, callback: callable, *args):
        if callable(callback):
            self._subscriptions.append(Subscription(callback, *args))

        elif isinstance(Subscription, callback):
            self.append_subscription(callback)


    def append_subscription(self, subscription: Subscription):
        self._subscriptions.append(subscription)


    def call(self):
        for sub in self._subscriptions:
            sub.call()


    def call_with_value(self, value):
        for sub in self._subscriptions:
            sub.call_with_value(value)


    def call_without_args(self):
        for sub in self._subscriptions:
            sub.call_without_args()


    def call_with_custom_args(self, *args):
        for sub in self._subscriptions:
            sub.call_with_custom_args(*args)


    def clear(self):
        self._subscriptions.clear()
