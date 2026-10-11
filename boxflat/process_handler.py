import psutil
from threading import Thread, Event
from time import sleep
from boxflat.subscription import EventDispatcher
from os import environ, path
import ntpath
import subprocess
import re


FLATPAK = environ["BOXFLAT_FLATPAK_EDITION"] == "true"


def list_processes(filter: str="") -> list[str]:
    output: list[str] = []

    for arg in _ps():
        # starts with at least 3 word characters (letters, numbers)
        # filters out arguments
        if not re.search("^\\w{3,}", arg):
            continue

        if not filter.lower() in arg.lower():
            continue

        if arg in output:
            continue

        output.append(arg)

    return output


def basename(name: str) -> str:
    return ntpath.basename(path.basename(name))


def _ps() -> list[str]:
    ps = _ps_flatpak if FLATPAK else _ps_native
    return [basename(cmd) for cmd in ps()]


def _ps_native() -> list[str]:
    output: list[str] = []

    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            output.append(p.info["name"])
            for arg in p.info["cmdline"] or []:
                output.append(arg)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return output


def _ps_flatpak() -> list[str]:
    return subprocess.check_output([
        "flatpak-spawn",
        "--host",
        "ps",
        "-wwu",
        psutil.Process().username(),
        "-o",
        "comm= command=",
    ]).decode().split()


class ProcessObserver(EventDispatcher):
    def __init__(self) -> None:
        super().__init__()
        self._shutdown = Event()
        self._current_processs = "empty"
        self._register_event("no-games")
        Thread(target=self._process_observer_worker, daemon=True).start()


    def _process_observer_worker(self) -> None:
        while not self._shutdown.is_set():
            try:
                sleep(5)
                self._observe()
            except:
                pass # some error in process observer


    def _observe(self) -> None:
        process_list = list_processes()

        for name in self.list_events():
            if name not in process_list:
                if name == self._current_processs:
                    self._current_processs = "empty"
                    self._dispatch("no-games")
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
        for name in self.list_events():
            if name == "no-games":
                continue
            self._deregister_event(name)
