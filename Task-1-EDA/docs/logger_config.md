# src/logger_config.py

**Purpose**

Provides a consistent, project-wide logger with both console and rotating
file output, plus a context manager for timing and logging the duration of
pipeline stages.

## `get_logger(name, log_dir=LOGS_DIR, log_file=LOG_FILE_NAME) -> logging.Logger`

Returns a logger that writes to both the console and a rotating log file
(`output/logs/eda_project.log` by default — rotates at a set size, keeps a
few backups). Every module in `src/` calls this once at import time:

```python
from src.logger_config import get_logger
logger = get_logger(__name__)
```

Calling `get_logger` multiple times with the same name is safe — handlers
are not duplicated.

## `log_execution_time(logger, task_name)`

Context manager that logs the start of a task, its duration on success, or
the exception on failure (still logged, then re-raised — this context
manager never swallows errors).

```python
from src.logger_config import log_execution_time

with log_execution_time(logger, "Chart generation"):
    visualizer.generate_all()
```

Produces log lines like:

```
INFO  Started: Chart generation
INFO  Finished: Chart generation (took 4.71s)
```

or, on failure:

```
INFO     Started: Chart generation
ERROR    Failed: Chart generation
Traceback (most recent call last): ...
```

This is what powers the execution-timing output you see in `main.py` for
every pipeline stage (loading, cleaning, exploration, anomaly detection,
hypothesis testing, chart generation, report generation).
