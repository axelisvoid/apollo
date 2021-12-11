import subprocess as subp
from typing import List, Optional, Tuple


def comm(cmd: str) -> Tuple[str, Optional[bytes]]:
    """Executes a shell command using `subp.Popen` interface."""

    timeout = 15            # in seconds

    with subp.Popen(f"{cmd}", shell=True, stdout=subp.PIPE, stderr=subp.PIPE) as proc:
        try:
            outs, errs = proc.communicate(timeout=timeout)
        except subp.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        except KeyboardInterrupt:
            proc.kill()
            raise KeyboardInterrupt from KeyboardInterrupt

    return outs, errs


def cmd_concat(cmds: List[str]) -> str:
    """Concatenates cli commands with the `&&` operator."""

    return " && ".join(cmds)


def capture_and_remove_apt_warning(errs: bytes) -> Optional[bytes]:
    """Captures apt cli constant warning and removes it from an error bytes object."""

    warning = b"\nWARNING: apt does not have a stable CLI interface. Use with caution in scripts.\n\n"

    if warning in errs:
        errs = errs[len(apt_err):]
    if len(errs) == 0:
        errs = None
    return errs
