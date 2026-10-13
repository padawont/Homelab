"""Configuration loading and validation for the cv sender worker.

The worker reads a single YAML document describing the account, the source view,
the row filters, the outgoing email signature, the daily rate limit, the
enrichment endpoints and the on-disk paths. Secrets are deliberately *not* part
of this document: the Gmail app password is read from the environment by
``sender.py`` only.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

#: Environment variable that overrides the config file location.
CONFIG_ENV_VAR = "CV_SENDER_CONFIG"

#: Location used inside the worker image when no override is provided.
DEFAULT_CONFIG_PATH = "/app/config/config.yaml"

#: ``(key path, label)`` pairs that must resolve to a present, non-empty value.
_REQUIRED_FIELDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("account", "email"), "account.email"),
    (("filters", "postdistrikter"), "filters.postdistrikter"),
    (("email", "signature_name"), "email.signature_name"),
    (("email", "signature_phone"), "email.signature_phone"),
    (("rate", "daily_cap"), "rate.daily_cap"),
)


def load_config(path: str | None = None) -> dict:
    """Load and validate the cv sender configuration.

    Parameters
    ----------
    path:
        Explicit config path. When omitted the ``CV_SENDER_CONFIG`` environment
        variable is consulted, falling back to :data:`DEFAULT_CONFIG_PATH`.

    Returns
    -------
    dict
        The parsed YAML document.

    Raises
    ------
    ValueError
        If the file is missing, is not a YAML mapping, or is missing any of the
        required settings.
    """

    resolved = _resolve_path(path)
    config_path = Path(resolved)
    if not config_path.is_file():
        raise ValueError(f"cv sender config not found: {resolved}")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"cv sender config is not valid YAML: {resolved}: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError(f"cv sender config must be a mapping: {resolved}")

    missing = [label for keys, label in _REQUIRED_FIELDS if not _is_present(_dig(config, keys))]
    if missing:
        raise ValueError("cv sender config is missing required fields: " + ", ".join(missing))

    dry_run = _dig(config, ("dry_run",))
    if dry_run is not None and not isinstance(dry_run, bool):
        raise ValueError(
            "cv sender config has invalid dry_run: expected a bool, got "
            f"{type(dry_run).__name__} ({dry_run!r})"
        )

    logger.debug("Loaded cv sender config from %s", resolved)
    return config


def _resolve_path(path: str | None) -> str:
    """Return the config path, honouring the ``CV_SENDER_CONFIG`` override."""

    if path:
        return path
    return os.environ.get(CONFIG_ENV_VAR) or DEFAULT_CONFIG_PATH


def _dig(config: dict, keys: tuple[str, ...]) -> Any:
    """Return the nested value at ``keys`` or ``None`` if any level is absent."""

    value: Any = config
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _is_present(value: Any) -> bool:
    """Return ``True`` when ``value`` is set and not empty."""

    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    return True
