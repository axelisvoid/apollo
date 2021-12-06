import subprocess as subp
from typing import List, Tuple


def comm(cmd: str) -> Tuple[str, str]:
    """Executes a shell command using `subp.Popen` interface."""

    with subp.Popen(f"{cmd}", shell=True, stdout=subp.PIPE) as proc:
        stdout_, stderr_ = proc.communicate()

    return stdout_.decode(), stderr_.decode()


def cmd_concat(cmds: List[str]) -> str:
    """Concatenates cli commands with the `&&` operator."""

    return " && ".join(cmds)

