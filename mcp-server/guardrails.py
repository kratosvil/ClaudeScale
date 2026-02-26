"""
ClaudeScale Guardrails — Safety mechanisms for LLM-driven scaling

Protections:
1. Cooldown — minimum time between scaling actions
2. State snapshot — saves cluster state before any action for rollback
3. Audit log — persistent log of every action with full context
4. Scale-down guard — extra conservative checks before reducing replicas
5. No destructive ops — only scale up/down within hard limits, never delete
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# ─── Configuration ────────────────────────────────────────────────────────────

COOLDOWN_SECONDS = 90          # Minimum seconds between scaling operations
SCALEDOWN_COOLDOWN_SECONDS = 180  # Scale-down is more conservative (3 min)
AUDIT_LOG_PATH = Path("/tmp/claudescale-audit.log")
SNAPSHOT_PATH = Path("/tmp/claudescale-snapshot.json")

# ─── In-memory state ──────────────────────────────────────────────────────────

_last_scale_time: Optional[datetime] = None
_last_scale_action: Optional[str] = None  # "up" or "down"

logger = logging.getLogger("claudescale.guardrails")


# ─── Cooldown ─────────────────────────────────────────────────────────────────

def check_cooldown(action: str) -> Dict[str, Any]:
    """
    Verify enough time has passed since last scaling operation.

    Scale-down has a longer cooldown than scale-up to prevent
    the LLM from aggressively reducing replicas.

    Returns:
        {"allowed": True} or {"allowed": False, "reason": ..., "retry_in_seconds": ...}
    """
    global _last_scale_time, _last_scale_action

    if _last_scale_time is None:
        return {"allowed": True}

    elapsed = (datetime.now() - _last_scale_time).total_seconds()
    required = SCALEDOWN_COOLDOWN_SECONDS if action == "down" else COOLDOWN_SECONDS

    if elapsed < required:
        remaining = int(required - elapsed)
        return {
            "allowed": False,
            "reason": (
                f"Cooldown active. Last scaling was {int(elapsed)}s ago. "
                f"Minimum wait for scale-{action}: {required}s. "
                f"Retry in {remaining}s."
            ),
            "retry_in_seconds": remaining,
            "last_action": _last_scale_action,
            "last_action_time": _last_scale_time.isoformat()
        }

    return {"allowed": True}


def record_scale_action(action: str):
    """Record that a scaling action just occurred."""
    global _last_scale_time, _last_scale_action
    _last_scale_time = datetime.now()
    _last_scale_action = action


# ─── State snapshot (rollback support) ───────────────────────────────────────

def save_snapshot(state: Dict[str, Any]):
    """
    Save cluster state before performing a scaling action.
    Allows quick rollback if something goes wrong.
    """
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "rollback_instructions": (
            "To restore: use claudescale_scale_deployment with the "
            "previous_replicas value for each deployment listed above."
        )
    }
    try:
        SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2))
        logger.info(f"Snapshot saved to {SNAPSHOT_PATH}")
    except Exception as e:
        logger.warning(f"Could not save snapshot: {e}")


def get_last_snapshot() -> Optional[Dict[str, Any]]:
    """Load the most recent pre-action snapshot."""
    try:
        if SNAPSHOT_PATH.exists():
            return json.loads(SNAPSHOT_PATH.read_text())
    except Exception:
        pass
    return None


# ─── Audit log ────────────────────────────────────────────────────────────────

def audit_log(event: str, details: Dict[str, Any]):
    """
    Append a structured entry to the persistent audit log.
    Every scaling decision is recorded with full context.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        **details
    }
    try:
        with AUDIT_LOG_PATH.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.warning(f"Could not write audit log: {e}")


def get_recent_audit(lines: int = 20) -> list:
    """Return the last N audit log entries."""
    try:
        if not AUDIT_LOG_PATH.exists():
            return []
        entries = AUDIT_LOG_PATH.read_text().strip().splitlines()
        return [json.loads(e) for e in entries[-lines:]]
    except Exception:
        return []


# ─── Scale-down guard ─────────────────────────────────────────────────────────

def validate_scaledown(
    current_replicas: int,
    desired_replicas: int,
    cpu_utilization_pct: Optional[float] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extra safety checks before allowing scale-down.

    Rules:
    - Reason is mandatory for scale-down (LLM must justify)
    - CPU must be below 40% to scale down (conservative threshold)
    - Cannot reduce by more than 1 replica at a time
    """
    if desired_replicas >= current_replicas:
        return {"allowed": True}

    errors = []

    # Rule 1: Reason required
    if not reason or reason.strip() == "" or reason == "No reason provided":
        errors.append(
            "Scale-down requires an explicit reason explaining why it is safe "
            "to reduce replicas right now."
        )

    # Rule 2: CPU must be low
    if cpu_utilization_pct is not None and cpu_utilization_pct > 40:
        errors.append(
            f"Scale-down blocked: CPU is at {cpu_utilization_pct:.1f}%. "
            f"Must be below 40% before scaling down."
        )

    # Rule 3: Max 1 replica reduction per action
    reduction = current_replicas - desired_replicas
    if reduction > 1:
        errors.append(
            f"Scale-down blocked: Cannot reduce by {reduction} replicas at once. "
            f"Maximum reduction per action is 1 replica. "
            f"Target {current_replicas - 1} instead of {desired_replicas}."
        )

    if errors:
        return {
            "allowed": False,
            "reason": " | ".join(errors)
        }

    return {"allowed": True}
