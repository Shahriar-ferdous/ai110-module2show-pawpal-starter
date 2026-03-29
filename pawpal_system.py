from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Dataclasses — simple value objects (Pet, Task)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    dietary_needs: list[str] = field(default_factory=list)

    def get_context(self) -> dict:
        """Return scheduling-relevant context for this pet."""
        pass


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str          # e.g. "high", "medium", "low"
    due_date: str          # ISO date string, e.g. "2026-03-28"
    status: str = "pending"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_overdue(self) -> bool:
        """Return True if due_date has passed and status is still pending."""
        pass


# ---------------------------------------------------------------------------
# Regular classes — stateful objects with behaviour (Owner, Scheduler)
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, available_time_slots: list[str]):
        self.available_time_slots = available_time_slots  # e.g. ["08:00", "12:00", "18:00"]

    def get_constraints(self) -> list[str]:
        """Return the list of available time slots to constrain scheduling."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pets: list[Pet], task_queue: list[Task]):
        self.owner = owner
        self.pets = pets
        self.task_queue = task_queue
        self.schedule: dict = {}   # maps time slot -> Task

    def build_plan(self) -> dict:
        """Build a schedule by matching tasks to owner's available time slots."""
        pass

    def assign_task(self, task: Task, time_slot: str) -> None:
        """Assign a single task to a specific time slot in the schedule."""
        pass

    def generate_summary(self) -> str:
        """Return a human-readable summary of the current schedule."""
        pass
