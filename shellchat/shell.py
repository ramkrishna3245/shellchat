import asyncio
import sys


async def run_command(command: str, timeout: int = 60) -> list[tuple[str, str]]:
    """Run a shell command and yield (stream, line) tuples.
    stream is 'stdout' or 'stderr'.
    """
    lines: list[tuple[str, str]] = []

    if sys.platform == "win32":
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    else:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    try:
        stdout_task = asyncio.create_task(_read_stream(proc.stdout, "stdout", lines))
        stderr_task = asyncio.create_task(_read_stream(proc.stderr, "stderr", lines))
        await asyncio.wait_for(asyncio.gather(stdout_task, stderr_task), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        lines.append(("system", f"[red]⏱ Command timed out after {timeout}s[/]"))

    return lines


async def _read_stream(stream, stream_name: str, lines: list) -> None:
    while True:
        line_bytes = await stream.readline()
        if not line_bytes:
            break
        line = line_bytes.decode(errors="replace").rstrip()
        if line:
            lines.append((stream_name, line))
