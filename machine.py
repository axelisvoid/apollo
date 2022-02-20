from platform import uname
from exceptions import NotSupportedMachineError

supported_machines = {
    "linux": [
        "ubuntu",
        "wsl2",
    ],
    "windows": [
        "10"
    ],
}
 

def get_machine():
    """Returns machine's operating system."""

   
    name = uname()
    info = {
        "system":  name.system.lower(),
        "release": name.release.lower(),
        "version": name.version.lower(),
    }

    machine = {"system": "", "version": ""}

    for sys in supported_machines.keys():
        if sys in info["system"]:
            machine["system"] = sys

    if machine["system"] == "linux":
        for ver in supported_machines["linux"]:
            if ver in (info["release"] or info["version"]):
                machine["version"] = ver

    if machine["system"] == "windows":
        for ver in supported_machines["windows"]:
            if ver in info["release"]:
                machine["version"] = ver

    # check machine dictionary is not empty
    for i in machine.values():
        if not i:
          raise NotSupportedMachineError

    return machine

