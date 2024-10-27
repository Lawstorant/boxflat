import psutil

def list(filter: str="") -> list[str]:
    processes = []

    for p in psutil.process_iter(['name']):
        if filter.lower() in p.name().lower():
            processes.append(p.name())

    return processes
