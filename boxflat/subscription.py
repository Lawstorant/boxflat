from threading import Event
from queue import SimpleQueue


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
        self._single_time_subs = SimpleQueue()


    def count(self) -> int:
        count = len(self._subscriptions)
        count += self._single_time_subs.qsize()
        return count


    def get(self, index: int) -> Subscription:
        return self._subscriptions[index]


    def append(self, callback: callable, *args) -> Subscription:
        if not callable(callback):
            return

        sub = Subscription(callback, *args)
        self._subscriptions.append(sub)
        return sub


    def append_single(self, callback: callable, *args):
        if not callable(callback):
            return

        sub = Subscription(callback, *args)
        self._single_time_subs.put(sub)


    def remove(self, sub: Subscription):
        if sub in self._subscriptions:
            self._subscriptions.remove(sub)


    def append_subscription(self, subscription: Subscription):
        self._subscriptions.append(subscription)


    def call(self):
        for sub in self._subscriptions:
            sub.call()

        while not self._single_time_subs.empty():
            self._single_time_subs.get().call()


    def call_with_value(self, value):
        for sub in self._subscriptions:
            sub.call_with_value(value)

        while not self._single_time_subs.empty():
            self._single_time_subs.get().call_with_value(value)


    def call_with_values(self, *values):
        for sub in self._subscriptions:
            sub.call_with_values(*values)

        while not self._single_time_subs.empty():
            self._single_time_subs.get().call_with_values(*values)


    def call_without_args(self):
        for sub in self._subscriptions:
            sub.call_without_args()

        while not self._single_time_subs.empty():
            self._single_time_subs.get().call_without_args()


    def call_with_custom_args(self, *args):
        for sub in self._subscriptions:
            sub.call_with_custom_args(*args)

        while not self._single_time_subs.empty():
            self._single_time_subs.get().call_with_custom_args(*args)


    def clear(self):
        self._subscriptions.clear()
        while not self._single_time_subs.empty():
            self._single_time_subs.get()



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


    def _deregister_all_events(self) -> bool:
        self.__events = {}


    def _dispatch(self, event_name: str, *values) -> bool:
        if not self.__find_event(event_name):
            return False

        if len(values) == 0:
            self.__events[event_name].call()
        else:
            self.__events[event_name].call_with_values(*values)
        return True


    def subscribe(self, event_name: str, callback: callable, *args) -> Subscription:
        if not self.__find_event(event_name):
            return False

        return self.__events[event_name].append(callback, *args)


    def subscribe_once(self, event_name: str, callback: callable, *args):
        if not self.__find_event(event_name):
            return

        self.__events[event_name].append_single(callback, *args)


    def _clear_event_subscriptions(self, event_name: str) -> bool:
        if not self.__find_event(event_name):
            return False

        self.__events[event_name].clear()


    def _remove_event_subscription(self, event_name: str, sub: Subscription) -> bool:
        if not self.__find_event(event_name):
            return False

        self.__events[event_name].remove(sub)


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


    def subscribe_once(self, event_name: str, callback: callable, *args):
        self.__events.append_single(callback, *args)


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



class BlockingValue():
    def __init__(self):
        self._value = None
        self._event = Event()


    def set_value(self, new_value):
        self._value = new_value
        self._event.set()


    def get_value(self, timeout=0.05):
        self._event.wait(timeout)
        self._event.clear()
        return self._value


    def get_value_no_clear(self, timeout=0.05):
        self._event.wait(timeout)
        return self._value
