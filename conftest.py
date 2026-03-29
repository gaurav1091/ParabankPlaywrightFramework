import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_MAIN_PYTHON = PROJECT_ROOT / "src" / "main" / "python"
SRC_TEST_PYTHON = PROJECT_ROOT / "src" / "test" / "python"
FRAMEWORK_PROPERTIES_PATH = PROJECT_ROOT / "src" / "test" / "resources" / "config" / "framework.properties"

for path in (SRC_MAIN_PYTHON, SRC_TEST_PYTHON):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def _read_properties_file(file_path: Path) -> dict[str, str]:
    properties: dict[str, str] = {}

    if not file_path.exists():
        return properties

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        properties[key.strip()] = value.strip()

    return properties


def _get_cli_option_value(args: list[str], option_name: str) -> str | None:
    prefix = f"{option_name}="

    for index, arg in enumerate(args):
        if arg.startswith(prefix):
            return arg[len(prefix) :].strip()

        if arg == option_name and index + 1 < len(args):
            next_arg = args[index + 1].strip()
            if not next_arg.startswith("-"):
                return next_arg

    return None


def _has_cli_option(args: list[str], *option_names: str) -> bool:
    for option_name in option_names:
        prefix = f"{option_name}="
        for arg in args:
            if arg == option_name or arg.startswith(prefix):
                return True
    return False


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"true", "1", "yes", "y", "on"}


def _to_int(value: str | None, default: int) -> int:
    if value is None:
        return default

    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _resolve_parallel_dist_mode(
    cli_dist_mode: str | None,
    properties: dict[str, str],
) -> str:
    if cli_dist_mode and cli_dist_mode.strip():
        return cli_dist_mode.strip().lower()

    configured_dist_mode = properties.get("parallel.dist.mode")
    if configured_dist_mode and configured_dist_mode.strip():
        return configured_dist_mode.strip().lower()

    parallel_mode = (properties.get("parallel.mode") or "methods").strip().lower()

    mode_to_dist_map = {
        "off": "no",
        "methods": "load",
        "classes": "loadscope",
        "tests": "loadfile",
    }

    return mode_to_dist_map.get(parallel_mode, "load")


def pytest_load_initial_conftests(early_config, parser, args) -> None:
    properties = _read_properties_file(FRAMEWORK_PROPERTIES_PATH)

    xdist_auto_apply = _to_bool(properties.get("xdist.auto.apply"), default=True)
    if not xdist_auto_apply:
        return

    if _has_cli_option(args, "-n", "--numprocesses"):
        return

    configured_parallel_enabled = _to_bool(properties.get("parallel.enabled"), default=False)
    cli_parallel_enabled = _get_cli_option_value(args, "--parallel-enabled")
    effective_parallel_enabled = _to_bool(cli_parallel_enabled, default=configured_parallel_enabled)

    cli_thread_count = _get_cli_option_value(args, "--thread-count")
    configured_thread_count = _to_int(properties.get("thread.count"), default=1)
    effective_thread_count = _to_int(cli_thread_count, default=configured_thread_count)

    should_parallelize = effective_parallel_enabled or effective_thread_count > 1

    if not should_parallelize:
        return

    if effective_thread_count <= 1:
        return

    args.extend(["-n", str(effective_thread_count)])

    if not _has_cli_option(args, "--dist"):
        cli_dist_mode = _get_cli_option_value(args, "--dist-mode")
        effective_dist_mode = _resolve_parallel_dist_mode(cli_dist_mode, properties)

        if effective_dist_mode and effective_dist_mode != "no":
            args.append(f"--dist={effective_dist_mode}")
