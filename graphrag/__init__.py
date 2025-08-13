# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""The GraphRAG package."""

import logging

try:
    from graphrag.logger.standard_logging import init_console_logger
except Exception:  # pragma: no cover - optional dependencies may be missing
    def init_console_logger(*args, **kwargs):  # type: ignore
        """Fallback logger initializer used when dependencies are absent."""
        return None

logger = logging.getLogger(__name__)
init_console_logger()
