import subprocess as subp
from typing import List, Optional, Tuple


def comm(cmd: str) -> Tuple[str, Optional[str]]:
    """Executes a shell command using `subp.Popen` interface."""

    with subp.Popen(f"{cmd}", shell=True, stdout=subp.PIPE) as proc:
        try:
            stdout_, stderr_ = proc.communicate()
        except KeyboardInterrupt:
            raise KeyboardInterrupt from KeyboardInterrupt
        else:
            dec_stdout = stdout_.decode()

    if stderr_:
        return dec_stdout, stderr_.decode()
    return dec_stdout, None


def cmd_concat(cmds: List[str]) -> str:
    """Concatenates cli commands with the `&&` operator."""

    return " && ".join(cmds)
