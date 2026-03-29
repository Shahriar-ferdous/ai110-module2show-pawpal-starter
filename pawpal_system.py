from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# Task — a single pet care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    category: str           # e.g. "feeding", "grooming", "medication", "exercise"
    duration_minutes: int
    priority: str           # "high" | "medium" | "low"
    due_date: str           # ISO date string, e.g. "2026-03-28"
    frequency: str          # "once" | "daily" | "weekly"
    status: str = "pending" # "pending" | "complete"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "complete"

    def is_overdue(self) -> bool:
        """Return True if due_date has passed and task is still pending."""
        return self.status == "pending" and date.fromisoformat(self.due_date) < date.today()


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns its task list
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    dietary_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_context(self) -> dict:
        """Return scheduling-relevant info about this pet."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "dietary_needs": self.dietary_needs,
            "pending_tasks": len([t for t in self.tasks if t.status == "pending"]),
        }


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and exposes scheduling constraints
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_time_slots: list[str]):
        self.name = name
        self.available_time_slots = available_time_slots  # e.g. ["08:00", "12:00", "18:00"]
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_constraints(self) -> list[str]:
        """Return available time slots the scheduler must respect."""
        return self.available_time_slots

    def get_all_tasks(self) -> list[Task]:
        """Collect every pending task across all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return [t for t in all_tasks if t.status == "pending"]


# ---------------------------------------------------------------------------
# Scheduler — the brain: retrieves, prioritizes, and assigns tasks
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule: dict[str, Task] = {}  # time_slot -> Task

    def _prioritize(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks: overdue first, then by priority level."""
        return sorted(
            tasks,
            key=lambda t: (not t.is_overdue(), PRIORITY_ORDER.get(t.priority, 99))
        )

    def assign_task(self, task: Task, time_slot: str) -> None:
        """Assign a task to a time slot; raises ValueError if slot is taken."""
        if time_slot in self.schedule:
            existing = self.schedule[time_slot].title
            raise ValueError(f"Slot {time_slot} is already assigned to '{existing}'")
        self.schedule[time_slot] = task

    def build_plan(self) -> dict[str, Task]:
        """
        Build today's schedule:
          1. Fetch all pending tasks from all pets via Owner.
          2. Sort by overdue status then priority.
          3. Fit tasks into the owner's available time slots.
        """
        self.schedule = {}
        tasks = self._prioritize(self.owner.get_all_tasks())
        slots = self.owner.get_constraints()

        for slot, task in zip(slots, tasks):
            self.assign_task(task, slot)

        return self.schedule

    def generate_summary(self) -> str:
        """Return a human-readable daily schedule summary."""
        if not self.schedule:
            return "No tasks scheduled."

        lines = [f"=== Daily Plan for {self.owner.name} ==="]
        for slot, task in sorted(self.schedule.items()):
            flag = " *** OVERDUE ***" if task.is_overdue() else ""
            lines.append(
                f"  {slot} | [{task.priority.upper()}] {task.title}"
                f" — {task.duration_minutes} min ({task.frequency}){flag}"
            )

        unscheduled = [
            t for t in self.owner.get_all_tasks()
            if t not in self.schedule.values()
        ]
        if unscheduled:
            lines.append(f"\n  ⚠ {len(unscheduled)} task(s) could not be scheduled (not enough slots):")
            for t in unscheduled:
                lines.append(f"    - {t.title} [{t.priority}]")

        return "\n".join(lines)
