"""Background task queue backed by the `task_queue` DB table.

Design goals:
  - Tasks are persisted to DB before execution so they survive process crashes.
  - A pool of daemon threads dequeues and executes tasks, with automatic retries
    on failure (up to `max_retries`).
  - Tasks that exceed max_retries land in 'failed' state (dead-letter equivalent).
  - The queue is started once at server startup via `start_workers()`.

Task registration:

    from workers.task_queue import task_queue

    @task_queue.register("send_email")
    def handle_send_email(user_id, subject, message, **_):
        # actual SMTP / SendGrid call
        ...

Enqueuing a task:

    task_queue.enqueue("send_email", {"user_id": uid, "subject": s, "message": m})
"""

import json
import threading
import time
import uuid
import datetime
import traceback
from typing import Any, Callable, Dict

_POLL_INTERVAL = 2       # seconds between DB polls
_WORKER_THREADS = 3      # concurrent worker threads


class TaskQueue:
    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[..., Any]] = {}
        self._started = False

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, task_type: str) -> Callable:
        """Decorator — register a handler for `task_type`."""
        def decorator(fn: Callable) -> Callable:
            self._handlers[task_type] = fn
            return fn
        return decorator

    # ── Enqueuing ─────────────────────────────────────────────────────────────

    def enqueue(self, task_type: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        """Persist a task to the DB queue and return its ID."""
        import db as _db
        task_id = str(uuid.uuid4())
        _db.execute(
            """
            INSERT INTO task_queue (id, task_type, payload, max_retries)
            VALUES (%s, %s, %s, %s)
            """,
            (task_id, task_type, json.dumps(payload), max_retries),
        )
        return task_id

    # ── Worker loop ───────────────────────────────────────────────────────────

    def _claim_task(self) -> Dict[str, Any] | None:
        """Atomically claim one pending or retrying task. Returns None if queue is empty."""
        import db as _db
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        row = _db.execute_returning(
            """
            UPDATE task_queue
            SET status     = 'running',
                started_at = %s
            WHERE id = (
                SELECT id FROM task_queue
                WHERE status IN ('pending', 'retrying')
                  AND scheduled_at <= NOW()
                ORDER BY scheduled_at ASC
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            )
            RETURNING id, task_type, payload, retry_count, max_retries
            """,
            (now,),
        )
        return row

    def _complete_task(self, task_id: str) -> None:
        import db as _db
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _db.execute(
            "UPDATE task_queue SET status = 'done', completed_at = %s WHERE id = %s",
            (now, task_id),
        )

    def _fail_task(self, task_id: str, error: str, retry_count: int, max_retries: int) -> None:
        import db as _db
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if retry_count + 1 >= max_retries:
            _db.execute(
                "UPDATE task_queue SET status = 'failed', error = %s, completed_at = %s WHERE id = %s",
                (error[:2000], now, task_id),
            )
        else:
            # Exponential back-off: 2^retry seconds
            delay = 2 ** retry_count
            scheduled_at = (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(seconds=delay)
            ).isoformat()
            _db.execute(
                """
                UPDATE task_queue
                SET status       = 'retrying',
                    retry_count  = retry_count + 1,
                    error        = %s,
                    scheduled_at = %s
                WHERE id = %s
                """,
                (error[:2000], scheduled_at, task_id),
            )

    def _worker(self) -> None:
        while True:
            try:
                task = self._claim_task()
                if task is None:
                    time.sleep(_POLL_INTERVAL)
                    continue
                handler = self._handlers.get(task["task_type"])
                if handler is None:
                    self._fail_task(
                        task["id"],
                        f"No handler registered for task_type={task['task_type']!r}",
                        task["retry_count"],
                        task["max_retries"],
                    )
                    continue
                try:
                    payload = json.loads(task["payload"])
                    handler(**payload)
                    self._complete_task(task["id"])
                except Exception:
                    self._fail_task(
                        task["id"],
                        traceback.format_exc(),
                        task["retry_count"],
                        task["max_retries"],
                    )
            except Exception:
                # Worker must never crash — swallow unexpected errors and sleep
                time.sleep(_POLL_INTERVAL)

    # ── Startup ───────────────────────────────────────────────────────────────

    def start_workers(self) -> None:
        """Spawn worker threads. Call once at server startup."""
        if self._started:
            return
        self._started = True
        for _ in range(_WORKER_THREADS):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()


# Module-level singleton used throughout the application
task_queue = TaskQueue()
