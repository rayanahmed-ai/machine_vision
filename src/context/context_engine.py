from __future__ import annotations

from typing import Any


class ContextEngine:
    """Summarize contextual risk from CV observations."""

    def assess(self, *, zone: str | None = None, dwell_time: float = 0.0, identity_status: str | None = None, nighttime: bool = False, behaviors: list[str] | None = None) -> dict[str, Any]:
        risk = "LOW"
        if behaviors:
            if any(item.lower() in {"tailgating", "loitering"} for item in behaviors):
                risk = "HIGH"
        if identity_status == "UNKNOWN" and zone:
            risk = "HIGH"
        if dwell_time > 30 and zone:
            risk = "HIGH"
        if nighttime and zone and identity_status != "KNOWN":
            risk = "HIGH"
        return {
            "risk": risk,
            "nighttime": nighttime,
            "zone": zone,
            "dwell_time": float(dwell_time),
            "identity": identity_status,
            "relevant_behavior": behaviors or [],
        }
