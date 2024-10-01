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


    def call_with_values(self, *values):
        self._callback(*values, *self._args)


    def call_with_custom_args(self, *args):
        self._callback(*args)



class SubscriptionList():
    def __init__(self):
        self._subscriptions = []


    def count(self) -> int:
        return len(self._subscriptions)


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


    def call_with_values(self, *values):
        for sub in self._subscriptions:
            sub.call_with_values(*values)


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


    def _event_sub_count(self, event_name: str) -> int:
        if event_name in self.__events:
            return self.__events[event_name].count()
        return -1


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
            #print(f"Event \"{event}\" registered")


    def _deregister_event(self, event_name: str) -> bool:
        if event_name not in self.events:
            return False

        self.__events.pop(event_name)
        return True

    def _deregister_events(self) -> bool:
        self.__events = {}


    def _dispatch(self, event_name: str, *values) -> bool:
        if not self.__find_event(event_name):
            return False

        if len(values) == 0:
            self.__events[event_name].call()
        else:
            self.__events[event_name].call_with_values(*values)
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


    def _clear_subscriptions(self, event_names=None):
        if not event_names:
            event_names = self.__events.keys()

        for event in event_names:
            self._clear_event_subscriptions(event)



class SimpleEventDispatcher():
    def __init__(self):
        self.__events = SubscriptionList()


    def _dispatch(self, *values):
        if len(values) == 0:
            self.__events.call()
        else:
            self.__events.call_with_values(*values)


    def subscribe(self, callback: callable, *args):
        self.__events.append(callback, *args)


    def _clear_subscriptions(self):
        self.__events.clear()



class Observable(SimpleEventDispatcher):
    def __init__(self, init_value=None):
        super().__init__()
        self._value = init_value


    def __call__(self):
        self._dispatch(self._value)


    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            self._dispatch(new_value)
        self._value = new_value


class Semaphore(EventDispatcher):
    def __init__(self, maximum: int):
        super().__init__()
        self._value = 0
        self._max = maximum
        self._register_event("value-changed")
        self._register_event("quorum-established")
        self._register_event("quorum-dissolved")


    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, new_value: int):
        if new_value > self._max:
            return

        if new_value < 0:
            return

        old_value = self._value
        self._value = new_value

        if new_value != old_value:
            self._dispatch(new_value)
            if new_value == self._max:
                self._dispatch("quorum-established")
            elif old_value == self._max:
                self._dispatch("quorum-dissolved")


    def increment(self):
        self.value += 1


    def decrement(self):
        self.value -= 1
