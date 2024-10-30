import psutil
from threading import Thread, Event
from time import sleep
from boxflat.subscription import EventDispatcher
from os import environ, path
import subprocess


def list_processes(filter: str="") -> list[str]:
    if environ["BOXFLAT_FLATPAK_EDITION"] == "true":
        return _list_process_flatpak(filter)

    return _list_process_native(filter)


def _list_process_native(filter: str) -> list[str]:
    output = []

    for p in psutil.process_iter(['name']):
        name = p.name()
        if not filter.lower() in name.lower():
            continue

        if name in output:
            continue

        output.append(name)

    return output


def _list_process_flatpak(filter: str) -> list[str]:
    output = []

    for name in _flatpak_ps_comm():
        if len(name) < 3:
            continue

        name = path.basename(name)
        if not filter.lower() in name.lower():
            continue

        if name in output:
            continue

        output.append(name)

    return output


def _flatpak_ps_comm() -> list[str]:
    processes = subprocess.check_output(["flatpak-spawn", "--host", "ps", "-wwu", psutil.Process().username(), "-o", "comm="])
    return processes.decode().split()


def _flatpk_ps_command() -> list[str]:
    processes = subprocess.check_output(["flatpak-spawn", "--host", "ps", "-wwu", psutil.Process().username(), "-o", "command="])
    return processes.decode().replace("\\", "/").split("\n")


class ProcessObserver(EventDispatcher):
    def __init__(self) -> None:
        super().__init__()
        self._shutdown = Event()
        self._current_processs = "no_process_yet"
        Thread(target=self._process_observer_worker, daemon=True).start()


    def _process_observer_worker(self) -> None:
        while not self._shutdown.is_set():
            sleep(5)
            process_list = list_processes()

            for name in self.list_events():
                if name not in process_list:
                    continue

                if name == self._current_processs:
                    continue

                print(f"Process \"{name}\" found")
                self._current_processs = name
                self._dispatch(name)


    def register_process(self, process_name: str) -> None:
        if len(process_name) < 1:
            return

        # print(f"Registering process: {process_name}")
        self._register_event(process_name)


    def deregister_process(self, process_name: str) -> None:
        self._deregister_event(process_name)


    def deregister_all_processes(self) -> None:
        self._deregister_all_events()
