# utils/firestore_client.py
from __future__ import annotations

"""Firestore client worker for Qt (PySide6).

This worker is designed to match the Firestore schema the project uses:
  - robots:       current snapshot per robot_id
  - tasks:        task lifecycle records
  - events:       append-only event stream (limited in UI)
  - interaction:  user inputs / commands (telegram/button/etc.)

It provides:
  - Realtime listeners (on_snapshot) for each collection.
  - Initial fetch on startup.
  - Optional generic upload queue (useful if Qt needs to write interaction docs).

Notes
-----
- We intentionally keep listeners "light": each listener is limited to recent N docs.
- For events, you typically want to show only the latest N items to avoid UI overload.
"""

from dataclasses import dataclass
from queue import Queue, Empty
from typing import Any, Dict, List, Tuple, Optional
import time

from PySide6.QtCore import QThread, Signal

import firebase_admin
from firebase_admin import credentials, firestore


@dataclass
class FirestoreConfig:
    service_account_path: str

    robots_collection: str = "robots"
    tasks_collection: str = "tasks"
    events_collection: str = "events"
    interaction_collection: str = "interaction"

    # limits for realtime snapshot queries
    robots_limit: int = 20
    tasks_limit: int = 200
    events_limit: int = 300
    interactions_limit: int = 200

    # =====================
    # Streaming (per-event) throttle
    # =====================
    # Firestore "events" can be very noisy when pose updates are logged frequently.
    # We typically want to stream (emit) pose-like events at a lower rate for the UI,
    # while still allowing important non-pose events (task_status_update, error, ...)
    # to pass through immediately.
    #
    # Set to 0 to disable throttling.
    events_pose_emit_interval_s: float = 1.0


class FirestoreWorker(QThread):
    # -------------------------
    # writes (optional)
    # -------------------------
    upload_ok = Signal(str)              # doc_id
    upload_fail = Signal(str, str)       # doc_id, error

    # -------------------------
    # reads (realtime snapshots)
    # -------------------------
    robots_updated = Signal(list)        # list[dict]
    tasks_updated = Signal(list)         # list[dict]
    interactions_updated = Signal(list)  # list[dict]
    events_updated = Signal(list)        # list[dict] (latest N)

    # events can be noisy; sometimes you want per-event streaming
    event_added = Signal(dict)           # single event dict

    # debug
    log = Signal(str)
    ready = Signal(bool)

    def __init__(self, cfg: FirestoreConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._running = True
        self._db = None

        # upload queue: (collection, doc_id, data)
        self._upload_q: Queue[Tuple[str, str, Dict[str, Any]]] = Queue()

        # Watch handles
        self._robots_watch = None
        self._tasks_watch = None
        self._events_watch = None
        self._interactions_watch = None

        # simple throttles (seconds)
        self._last_emit = {
            "app_config": 0.0,
            "events": 0.0,
            "interactions": 0.0,
            "robots": 0.0,
            "tasks": 0.0,
        }

        # per-robot throttles for noisy per-event streaming (pose-like events)
        self._last_pose_event_emit_by_robot: Dict[str, float] = {}

    # ---------- public API ----------
    def request_upload(self, collection: str, doc_id: str, data: Dict[str, Any]):
        """Queue a document write.

        Qt HMI generally does NOT need to write robots/tasks/events (usually Node-RED/server does).
        But writing interaction logs from the HMI can be useful.
        """
        self._upload_q.put((collection, doc_id, data))

    def stop(self):
        self._running = False

    # ---------- internal ----------
    def _init_firestore(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.cfg.service_account_path)
            firebase_admin.initialize_app(cred)
        self._db = firestore.client()

    def _to_rows(self, docs) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for d in docs:
            item = d.to_dict() or {}
            item["_id"] = d.id
            rows.append(item)
        return rows

    def _fetch_recent(self, collection_name: str, order_field_candidates: List[str], limit: int) -> List[Dict[str, Any]]:
        col = self._db.collection(collection_name)

        # try to order_by a known timestamp field
        for field in order_field_candidates:
            try:
                docs = col.order_by(field, direction=firestore.Query.DESCENDING).limit(limit).stream()
                return self._to_rows(docs)
            except Exception:
                continue

        # fallback
        try:
            docs = col.limit(limit).stream()
            return self._to_rows(docs)
        except Exception:
            return []

    def _throttled_emit(self, key: str, sig: Signal, payload: Any, min_interval_s: float = 0.05):
        now = time.time()
        if now - self._last_emit.get(key, 0.0) >= min_interval_s:
            self._last_emit[key] = now
            sig.emit(payload)

    def _start_listener(self, collection_name: str, order_fields: List[str], limit: int,
                        emit_key: str, emit_sig: Signal,
                        on_changes: Optional[callable] = None,
                        label: str = ""):
        col = self._db.collection(collection_name)

        query = None
        for field in order_fields:
            try:
                query = col.order_by(field, direction=firestore.Query.DESCENDING).limit(limit)
                break
            except Exception:
                continue
        if query is None:
            query = col.limit(limit)

        def on_snapshot(col_snapshot, changes, read_time):
            try:
                rows = self._to_rows(col_snapshot)
                self._throttled_emit(emit_key, emit_sig, rows)

                if on_changes is not None:
                    on_changes(changes)

                self.log.emit(f"[FS] {label} on_snapshot: {len(rows)} docs (col={collection_name})")
            except Exception as e:
                self.log.emit(f"[FS] {label} on_snapshot error: {e}")

        return query.on_snapshot(on_snapshot)

    def _start_all_listeners(self):
        if self._robots_watch is None:
            self._robots_watch = self._start_listener(
                self.cfg.robots_collection,
                order_fields=["updated_at", "ts"],
                limit=self.cfg.robots_limit,
                emit_key="robots",
                emit_sig=self.robots_updated,
                label="robots",
            )

        if self._tasks_watch is None:
            self._tasks_watch = self._start_listener(
                self.cfg.tasks_collection,
                order_fields=["created_at", "started_at", "finished_at", "ts"],
                limit=self.cfg.tasks_limit,
                emit_key="tasks",
                emit_sig=self.tasks_updated,
                label="tasks",
            )

        if self._interactions_watch is None:
            self._interactions_watch = self._start_listener(
                self.cfg.interaction_collection,
                order_fields=["ts", "created_at"],
                limit=self.cfg.interactions_limit,
                emit_key="interaction",
                emit_sig=self.interactions_updated,
                label="interaction",
            )

        if self._events_watch is None:
            def _emit_added(changes):
                # emit per-added event for optional streaming views
                try:
                    for ch in changes:
                        change_type = getattr(getattr(ch, "type", None), "name", None) or str(getattr(ch, "type", ""))
                        if change_type == "ADDED" or change_type.endswith(".ADDED") or change_type.endswith("ADDED"):
                            d = ch.document
                            item = d.to_dict() or {}
                            item["_id"] = d.id
                            # Throttle only pose-like high-frequency events
                            pose = item.get("pose")
                            is_pose_like = isinstance(pose, dict) and ("x" in pose) and ("y" in pose)
                            interval = float(getattr(self.cfg, "events_pose_emit_interval_s", 0.0) or 0.0)

                            if is_pose_like and interval > 0.0:
                                robot_key = str(item.get("robot_id") or "_")
                                now = time.time()
                                last = self._last_pose_event_emit_by_robot.get(robot_key, 0.0)
                                if now - last >= interval:
                                    self._last_pose_event_emit_by_robot[robot_key] = now
                                    self.event_added.emit(item)
                            else:
                                # non-pose events should pass immediately
                                self.event_added.emit(item)
                except Exception as e:
                    self.log.emit(f"[FS] events change parse error: {e}")

            self._events_watch = self._start_listener(
                self.cfg.events_collection,
                order_fields=["ts", "created_at"],
                limit=self.cfg.events_limit,
                emit_key="events",
                emit_sig=self.events_updated,
                on_changes=_emit_added,
                label="events",
            )

    def _stop_watch(self, watch, name: str):
        if watch is None:
            return None
        try:
            watch.unsubscribe()
            self.log.emit(f"[FS] {name} listener stopped")
        except Exception as e:
            self.log.emit(f"[FS] {name} stop error: {e}")
        return None

    # ---------- thread ----------
    def run(self):
        self.log.emit(f"[FS] worker started: id={id(self)}")

        try:
            self._init_firestore()
            self.ready.emit(True)
            self.log.emit("[FS] initialized")
        except Exception as e:
            self.ready.emit(False)
            self.log.emit(f"[FS] init failed: {e}")
            return

        # ---- initial fetch ----
        try:
            robots = self._fetch_recent(self.cfg.robots_collection, ["updated_at", "ts"], self.cfg.robots_limit)
            self.robots_updated.emit(robots)
            self.log.emit(f"[FS] initial fetch robots: {len(robots)}")
        except Exception as e:
            self.log.emit(f"[FS] initial fetch robots error: {e}")

        try:
            tasks = self._fetch_recent(self.cfg.tasks_collection, ["created_at", "started_at", "finished_at", "ts"], self.cfg.tasks_limit)
            self.tasks_updated.emit(tasks)
            self.log.emit(f"[FS] initial fetch tasks: {len(tasks)}")
        except Exception as e:
            self.log.emit(f"[FS] initial fetch tasks error: {e}")

        try:
            interactions = self._fetch_recent(self.cfg.interaction_collection, ["ts", "created_at"], self.cfg.interactions_limit)
            self.interactions_updated.emit(interactions)
            self.log.emit(f"[FS] initial fetch interaction: {len(interactions)}")
        except Exception as e:
            self.log.emit(f"[FS] initial fetch interaction error: {e}")

        try:
            events = self._fetch_recent(self.cfg.events_collection, ["ts", "created_at"], self.cfg.events_limit)
            self.events_updated.emit(events)
            self.log.emit(f"[FS] initial fetch events: {len(events)}")
        except Exception as e:
            self.log.emit(f"[FS] initial fetch events error: {e}")

        # ---- start listeners ----
        try:
            self._start_all_listeners()
        except Exception as e:
            self.log.emit(f"[FS] failed to start listeners: {e}")

        # ---- upload loop ----
        while self._running:
            try:
                collection, doc_id, data = self._upload_q.get(timeout=0.2)
                try:
                    self._db.collection(collection).document(doc_id).set(data)
                    self.upload_ok.emit(doc_id)
                except Exception as e:
                    self.upload_fail.emit(doc_id, str(e))
            except Empty:
                pass
            except Exception as e:
                self.log.emit(f"[FS] loop error: {e}")

        # ---- cleanup ----
        self._robots_watch = self._stop_watch(self._robots_watch, "robots")
        self._tasks_watch = self._stop_watch(self._tasks_watch, "tasks")
        self._events_watch = self._stop_watch(self._events_watch, "events")
        self._interactions_watch = self._stop_watch(self._interactions_watch, "interactions")

