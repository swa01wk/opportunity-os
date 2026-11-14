# ruff: noqa: S307, S602, S607

import subprocess

# ruleid: oos.python.dangerous-exec
eval("1")

# ruleid: oos.python.subprocess
subprocess.run(["echo", "hi"], shell=True)


# ok: oos.python.dangerous-exec
SAFE = 1


# ok: oos.python.subprocess
def no_subprocess() -> None:
    return None
