class Subscription():
    def __init__(self, callback: callable, *args):
        self._callback = callback
        self._args = args


    def __call__(self):
        self.call()


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


    def append_subscription(self, subscription: Subscription):
        self._subscriptions.append(subscription)


    def call(self):
        """
        Call all subscribers with default arguments
        """
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



class EventDispatcher():
    def __init__(self):
        self.__events = {}


    def list_events(self) -> list[str]:
        return list(self.__events.keys())


    @property
    def events(self) -> list[str]:
        return self.list_events()


    def __find_event(self, event_name: str) -> bool:
        return bool(self.__events.get(event_name, False))


    def _register_event(self, event_name: str) -> bool:
        if not self.__find_event(event_name):
            self.__events[event_name] = SubscriptionList()
            return True
        return False
        # TODO debug warn if event already exists


    def _register_events(self, *event_names: str):
        for event in event_names:
            self._register_event(event)


    def _deregister_event(self, event_name: str) -> bool:
        if event_name not in self.events:
            return False

        self.__events.pop(event_name)
        return True

    def _deregister_events(self) -> bool:
        self.__events = {}


    def _dispatch(self, event_name: str, value=None) -> bool:
        if not self.__find_event(event_name):
            return False

        if value == None:
            self.__events[event_name].call()
        else:
            self.__events[event_name].call_with_value(value)
        return True


    def subscribe(self, event_name: str, callback: callable, *args) -> bool:
        if not self.__find_event(event_name):
            return False

        self.__events[event_name].append(callback, *args)
        return True


    def _clear_event_subscriptions(self, event_name: str) -> bool:
        if not self.__find_event(event_name):
            return False

        self.__events[event_name].clear()


    def _clear_subscriptions(self):
        for event in self.__events.values():
            event.clear()



class SimpleEventDispatcher():
    def __init__(self):
        self.__events = SubscriptionList()


    def _dispatch(self, value=None):
        if value is None:
            self.__events.call()
        else:
            self.__events.call_with_value(value)


    def subscribe(self, callback: callable, *args):
        self.__events.append(callback, *args)


    def _clear_subscriptions(self):
        self.__events.clear()
