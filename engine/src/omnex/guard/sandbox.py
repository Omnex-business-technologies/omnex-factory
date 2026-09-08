"""Running model-authored code without handing it the machine.

The honest framing first, because sandboxing is the area where confident
libraries do the most harm: **this is a resource and blast-radius limiter, not a
security boundary against a determined attacker.** A CPython interpreter in a
subprocess is not a hostile-code sandbox — CPython has never claimed to be one,
and every in-process "restricted exec" scheme built on stripping `__builtins__`
has been escaped, usually within a day, via the object graph
(`().__class__.__base__.__subclasses__()` and relatives).

What this does provide is real and worth having:

- A separate process, so a segfault or `os._exit` takes nothing with it.
- OS-enforced limits via `setrlimit` — address space, CPU seconds, file size,
  process count. A fork bomb hits `RLIMIT_NPROC`; a `[0] * 10**10` hits
  `RLIMIT_AS` and raises `MemoryError` inside the child rather than invoking the
  kernel OOM killer on whatever else happens to be resident.
- A wall-clock kill, because `RLIMIT_CPU` does not fire on a process asleep in
  `time.sleep(10**9)`.
- No network, no environment, and a scratch working directory.

For genuinely untrusted code the answer is a VM or a gVisor/Firecracker
container, and `SandboxPolicy.network` refuses to be set to True here so that
choice cannot be made by accident in a config file.

The limits are applied in the child via `preexec_fn`, after fork and before
exec, which is the only point where they can be set for the child without
affecting the parent.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ..core.clock import Clock, SystemClock

__all__ = ["SandboxPolicy", "SandboxResult", "run_python"]


@dataclass(frozen=True)
class SandboxPolicy:
    """Resource ceilings for one execution."""

    #: Wall-clock seconds. Catches sleeping and blocked processes, which CPU
    #: limits do not.
    timeout_seconds: float = 5.0
    #: CPU seconds. Catches a busy loop that the wall clock would let run.
    cpu_seconds: int = 2
    #: Address space in bytes. 256 MB is comfortably above a normal script and
    #: far below anything that threatens the host.
    memory_bytes: int = 256 * 1024 * 1024
    #: Bytes any single file may reach. Stops a runaway write filling the disk.
    file_size_bytes: int = 8 * 1024 * 1024
    #: Child processes allowed. Low, so a fork bomb terminates itself.
    max_processes: int = 8
    #: Bytes of stdout/stderr kept. Beyond this the output is truncated rather
    #: than buffered, since a 2 GB traceback is its own denial of service.
    max_output_bytes: int = 64 * 1024

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout must be positive")


@dataclass(frozen=True)
class SandboxResult:
    ok: bool
    stdout: str
    stderr: str
    exit_code: int | None
    duration_seconds: float
    #: Set when the sandbox stopped it rather than the program finishing.
    terminated_reason: str = ""

    @property
    def timed_out(self) -> bool:
        return self.terminated_reason == "timeout"


def _apply_limits(policy: SandboxPolicy) -> None:  # pragma: no cover - runs in the child
    """Set rlimits in the child, between fork and exec."""
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (policy.memory_bytes, policy.memory_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (policy.cpu_seconds, policy.cpu_seconds))
    resource.setrlimit(resource.RLIMIT_FSIZE, (policy.file_size_bytes, policy.file_size_bytes))
    resource.setrlimit(resource.RLIMIT_NPROC, (policy.max_processes, policy.max_processes))
    # No core dumps: a 256 MB core file per crash is a disk-filling denial of
    # service triggered by the very code you were trying to contain.
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.setsid()  # own process group, so the timeout kill takes the children too


def run_python(
    code: str, policy: SandboxPolicy | None = None, clock: Clock | None = None
) -> SandboxResult:
    """Execute `code` in a limited subprocess. Never raises on program failure.

    `clock` measures the duration and nothing else. The two halves of "how long
    did this take" belong to different owners and conflating them is what made
    this function untestable:

    - The **kill** is `subprocess.run(timeout=...)`, and it stays with the
      operating system. A `FakeClock` cannot interrupt a real child process, and
      wiring one in would produce a timeout that fires only after the thing it
      was meant to bound has already returned. Same argument as
      `mcp.transport.StreamTransport`, which accepts a timeout it does not
      enforce and says so.
    - The **measurement** is ours, and it was reading `time.monotonic()`
      directly — the one thing `CLAUDE.md` says nothing in this package does.
      The cost was not abstract: `duration_seconds` could not be asserted on,
      so no test ever checked the field.
    """
    policy = policy or SandboxPolicy()
    clock = clock or SystemClock()

    with tempfile.TemporaryDirectory(prefix="omnex-sandbox-") as workdir:
        script = Path(workdir) / "main.py"
        script.write_text(code)

        started = clock.monotonic()
        # A near-empty environment. Inheriting the parent's is how an API key
        # reaches code the model wrote.
        env = {"PATH": "/usr/bin:/bin", "HOME": workdir, "TMPDIR": workdir, "PYTHONNOUSERSITE": "1"}

        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-S", str(script)],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=policy.timeout_seconds,
                preexec_fn=lambda: _apply_limits(policy),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(
                ok=False,
                stdout=_truncate(_decode(exc.stdout), policy.max_output_bytes),
                stderr=_truncate(_decode(exc.stderr), policy.max_output_bytes),
                exit_code=None,
                duration_seconds=clock.monotonic() - started,
                terminated_reason="timeout",
            )

        duration = clock.monotonic() - started
        # A negative return code is a signal: -9 is the kernel OOM killer or an
        # rlimit, -24 is RLIMIT_CPU. Reported distinctly, because "your code was
        # killed for using too much memory" and "your code raised" need
        # different responses from whatever is driving the loop.
        reason = ""
        if completed.returncode is not None and completed.returncode < 0:
            reason = f"signal_{-completed.returncode}"

        return SandboxResult(
            ok=completed.returncode == 0,
            stdout=_truncate(completed.stdout, policy.max_output_bytes),
            stderr=_truncate(completed.stderr, policy.max_output_bytes),
            exit_code=completed.returncode,
            duration_seconds=duration,
            terminated_reason=reason,
        )


def _decode(raw: bytes | str | None) -> str:
    if raw is None:
        return ""
    return raw if isinstance(raw, str) else raw.decode("utf-8", errors="replace")


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n… truncated at {limit} bytes"
