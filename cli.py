import re
import subprocess as subp
from typing import List, Optional, Tuple


def comm(cmd: str) -> Tuple[bytes, Optional[bytes]]:
    """Executes a shell command using `subp.Popen` interface."""

    with subp.Popen(f"{cmd}", shell=True, stdout=subp.PIPE, stderr=subp.PIPE) as proc:
        try:
            outs, errs = proc.communicate()
        except KeyboardInterrupt:
            proc.kill()
            raise KeyboardInterrupt from KeyboardInterrupt

    return outs, errs


def cmd_concat(cmds: List[str]) -> str:
    """Concatenates cli commands with the `&&` operator."""

    return " && ".join(cmds)


def car_expected_err_msg(msg: bytes, errs: bytes) -> Optional[bytes]:
    """Captures an expected error message and removes it from an error bytes object."""
    
    if msg in errs:
        s_msg = msg.decode()
        s_errs = errs.decode()
        patt = re.compile(s_msg)
        # search will not return None because we already know the warning is in errs
        res = patt.search(s_errs).span()
        tmp_subs = s_errs[res[0]:res[1]]
        s_errs = s_errs.replace(tmp_subs, "")
        errs_ = bytes(s_errs, "utf8")
        errs = capture_and_remove_apt_warning(errs_)
    
    return errs


def car_apt_warning(errs: bytes) -> Optional[bytes]:
    """Capture and remove apt cli constant warning and removes it from an error bytes object."""

    warning = b"\nWARNING: apt does not have a stable CLI interface. Use with caution in scripts.\n\n"
    return car_expected_err_msg(warning, errs)
