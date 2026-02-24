"""Chaos Controller — manages state for 20 independent fault channels."""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from app.config import CHANNEL_REGISTRY

logger = logging.getLogger("nova7.chaos")

# Channel states
STANDBY = "STANDBY"
ACTIVE = "ACTIVE"
RESOLVING = "RESOLVING"

# Maximum fault duration (seconds)
MAX_FAULT_DURATION = 3600  # 1 hour


class ChaosController:
    """Thread-safe chaos channel state management."""

    def __init__(self, channel_registry: dict[int, dict[str, Any]] | None = None):
        self._lock = threading.RLock()
        self._channel_registry = channel_registry or CHANNEL_REGISTRY
        self._channels: dict[int, dict[str, Any]] = {}
        for ch_id in self._channel_registry:
            self._channels[ch_id] = {
                "state": STANDBY,
                "mode": None,
                "se_name": None,
                "triggered_at": None,
                "resolved_at": None,
                "callback_url": "",
                "user_email": "",
            }
        self._infra_spikes: dict[str, float] = {
            "cpu_pct": 0,
            "memory_pct": 0,
            "k8s_oom_intensity": 0,
            "latency_multiplier": 1.0,
        }

    def trigger(
        self,
        channel: int,
        mode: str = "calibration",
        se_name: str = "",
        callback_url: str = "",
        user_email: str = "",
    ) -> dict[str, Any]:
        if channel not in self._channel_registry:
            return {"error": f"Unknown channel {channel}"}

        with self._lock:
            ch = self._channels[channel]
            if ch["state"] == ACTIVE:
                return {"status": "already_active", "channel": channel}

            ch["state"] = ACTIVE
            ch["mode"] = mode
            ch["se_name"] = se_name
            ch["triggered_at"] = time.time()
            ch["resolved_at"] = None
            ch["callback_url"] = callback_url
            ch["user_email"] = user_email

        ch_def = self._channel_registry[channel]
        logger.info(
            "CHAOS: Channel %d [%s] ACTIVATED (mode=%s)",
            channel,
            ch_def["name"],
            mode,
        )
        return {
            "status": "triggered",
            "channel": channel,
            "name": ch_def["name"],
            "mode": mode,
        }

    def resolve(self, channel: int) -> dict[str, Any]:
        if channel not in self._channel_registry:
            return {"error": f"Unknown channel {channel}"}

        with self._lock:
            ch = self._channels[channel]
            if ch["state"] == STANDBY:
                return {"status": "already_standby", "channel": channel}

            ch["state"] = STANDBY
            ch["mode"] = None
            ch["resolved_at"] = time.time()
            ch["callback_url"] = ""
            ch["user_email"] = ""

        ch_def = self._channel_registry[channel]
        logger.info("CHAOS: Channel %d [%s] RESOLVED", channel, ch_def["name"])
        return {
            "status": "resolved",
            "channel": channel,
            "name": ch_def["name"],
        }

    def _expire_stale(self) -> None:
        """Auto-resolve channels that have been active longer than MAX_FAULT_DURATION.

        Must be called while holding self._lock.
        """
        now = time.time()
        for ch_id, ch in self._channels.items():
            if ch["state"] != ACTIVE:
                continue
            if ch["triggered_at"] and (now - ch["triggered_at"]) >= MAX_FAULT_DURATION:
                ch["state"] = STANDBY
                ch["mode"] = None
                ch["resolved_at"] = now
                ch["callback_url"] = ""
                ch["user_email"] = ""
                ch_def = self._channel_registry[ch_id]
                logger.info(
                    "CHAOS: Channel %d [%s] AUTO-EXPIRED after %ds",
                    ch_id,
                    ch_def["name"],
                    MAX_FAULT_DURATION,
                )

    def is_active(self, channel: int) -> bool:
        with self._lock:
            self._expire_stale()
            ch = self._channels.get(channel)
            return ch is not None and ch["state"] == ACTIVE

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            self._expire_stale()
            result = {}
            for ch_id, ch_state in self._channels.items():
                ch_def = self._channel_registry[ch_id]
                result[ch_id] = {
                    "name": ch_def["name"],
                    "subsystem": ch_def["subsystem"],
                    "state": ch_state["state"],
                    "mode": ch_state["mode"],
                    "triggered_at": ch_state["triggered_at"],
                    "affected_services": ch_def["affected_services"],
                    "description": ch_def["description"],
                }
            return result

    def get_channel_status(self, channel: int) -> dict[str, Any]:
        if channel not in self._channel_registry:
            return {"error": f"Unknown channel {channel}"}
        with self._lock:
            ch_state = self._channels[channel]
            ch_def = self._channel_registry[channel]
            return {
                "channel": channel,
                "name": ch_def["name"],
                "subsystem": ch_def["subsystem"],
                "state": ch_state["state"],
                "mode": ch_state["mode"],
                "se_name": ch_state["se_name"],
                "triggered_at": ch_state["triggered_at"],
                "resolved_at": ch_state["resolved_at"],
                "callback_url": ch_state.get("callback_url", ""),
                "user_email": ch_state.get("user_email", ""),
                "affected_services": ch_def["affected_services"],
                "cascade_services": ch_def["cascade_services"],
                "error_type": ch_def["error_type"],
                "sensor_type": ch_def["sensor_type"],
                "vehicle_section": ch_def["vehicle_section"],
                "description": ch_def["description"],
            }

    def get_channel_metadata(self, channel: int) -> dict[str, str]:
        """Return callback_url and user_email for a channel."""
        with self._lock:
            ch = self._channels.get(channel)
            if ch is None:
                return {"callback_url": "", "user_email": ""}
            return {
                "callback_url": ch.get("callback_url", ""),
                "user_email": ch.get("user_email", ""),
            }

    def get_active_channels(self) -> list[int]:
        with self._lock:
            return [ch_id for ch_id, ch in self._channels.items() if ch["state"] == ACTIVE]

    def set_infra_spikes(self, spikes: dict[str, float]) -> None:
        with self._lock:
            for key in self._infra_spikes:
                if key in spikes:
                    self._infra_spikes[key] = float(spikes[key])

    def get_infra_spikes(self) -> dict[str, float]:
        with self._lock:
            return dict(self._infra_spikes)
