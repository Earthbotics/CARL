from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import time

@dataclass
class FocusSlot:
    owner: str              # "outer","inner","game","system"
    topic: str              # e.g., "human_dialogue","tic_tac_toe","planning"
    strength: float         # 0..1 salience
    started_at: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)

class AttentionManager:
    """Single-focal, cooperative attention with hysteresis & preemption budget."""
    def __init__(self):
        self.current: Optional[FocusSlot] = None
        self.last_switch_ts: float = 0.0
        self.switch_cooldown_s: float = 2.0     # prevent thrash
        self.preemption_budget_s: float = 10.0  # min dwell time before lower salience can preempt

    def _can_switch(self, new_strength: float) -> bool:
        if not self.current: return True
        since = time.time() - self.last_switch_ts
        # avoid flapping: require cooldown and meaningful improvement
        return (since >= self.switch_cooldown_s) and (new_strength >= self.current.strength + 0.1)

    def _can_preempt(self, new_owner: str, new_strength: float) -> bool:
        if not self.current: return True
        high_priority = (new_owner in ("outer","game"))
        dwell_ok = (time.time() - self.current.started_at) >= self.preemption_budget_s
        return high_priority or dwell_ok or (new_strength >= self.current.strength + 0.25)

    def propose(self, slot: FocusSlot) -> FocusSlot:
        if not self.current:
            self.current = slot; self.last_switch_ts = time.time(); return self.current
        # If same owner/topic → just refresh strength/context
        if self.current.owner == slot.owner and self.current.topic == slot.topic:
            if slot.strength > self.current.strength:
                self.current.strength = slot.strength
            self.current.context.update(slot.context)
            return self.current
        # Consider switch / preemption
        if self._can_switch(slot.strength) and self._can_preempt(slot.owner, slot.strength):
            self.current = slot; self.last_switch_ts = time.time()
        return self.current

    def view(self) -> Optional[FocusSlot]:
        return self.current
