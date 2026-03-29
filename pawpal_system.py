from dataclasses import dataclass, field
from datetime import date, timedelta
from itertools import combinations
RECUR_DELTA = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1)
}
def advance_recurring(task):
    """If task is recurring, move its due_date forward by the appropriate delta."""
    if task.frequency in RECUR_DELTA:
        new_due = date.fromisoformat(task.due_date) + RECUR_DELTA[task.frequency]
        task.due_date = new_due.isoformat()
        task.status = "pending"  # reset status for next occurrence


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
        """Mark this task as completed, then advance recurring due date."""
        self.status = "complete"
        advance_recurring(self)

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
        self.warnings: list[str] = []        # non-fatal conflict messages

    def sort_by_time(self) -> list[tuple[str, Task]]:
        """Return scheduled (slot, task) pairs sorted chronologically by slot time."""
        return sorted(
            self.schedule.items(),
            key=lambda item: self._to_minutes(item[0])
        )

    def filter_tasks(self, status: str | None = None, pet_name: str | None = None) -> list[tuple[str, Task]]:
        """
        Return (slot, task) pairs from the schedule filtered by status and/or pet name.
        - status: "pending" or "complete" — matches task.status
        - pet_name: case-insensitive pet name — matches tasks owned by that pet
        Filters combine (both must match when both are provided).
        """
        pet_task_sets = {}
        if pet_name is not None:
            for pet in self.owner.pets:
                if pet.name.lower() == pet_name.lower():
                    pet_task_sets = set(id(t) for t in pet.tasks)
                    break

        results = []
        for slot, task in self.schedule.items():
            if status is not None and task.status != status:
                continue
            if pet_name is not None and id(task) not in pet_task_sets:
                continue
            results.append((slot, task))
        return results

    def _pet_for_task(self, task: Task) -> str:
        """Return the pet name that owns this task, or 'Unknown' if not found."""
        for pet in self.owner.pets:
            if any(id(t) == id(task) for t in pet.tasks):
                return pet.name
        return "Unknown"

    def detect_conflicts(self) -> list[dict]:
        """
        Check every pair of scheduled tasks for time overlap.
        Returns a list of conflict dicts, each with:
          - slot_a, task_a, pet_a: first conflicting entry
          - slot_b, task_b, pet_b: second conflicting entry
          - kind: "same_pet" if both tasks belong to the same pet, else "cross_pet"
        """
        # Build reverse lookup {task id → pet name} once — O(total tasks)
        task_to_pet = {
            id(task): pet.name
            for pet in self.owner.pets
            for task in pet.tasks
        }

        # Pre-compute (slot, task, pet, start, end) once per entry — O(n)
        entries = [
            (slot, task, task_to_pet.get(id(task), "Unknown"),
             self._to_minutes(slot), self._to_minutes(slot) + task.duration_minutes)
            for slot, task in self.schedule.items()
        ]

        # combinations(entries, 2) yields every unique pair without index math
        return [
            {
                "slot_a": slot_a, "task_a": task_a, "pet_a": pet_a,
                "slot_b": slot_b, "task_b": task_b, "pet_b": pet_b,
                "kind": "same_pet" if pet_a == pet_b else "cross_pet",
            }
            for (slot_a, task_a, pet_a, start_a, end_a),
                (slot_b, task_b, pet_b, start_b, end_b)
            in combinations(entries, 2)
            if start_a < end_b and start_b < end_a
        ]

    def _prioritize(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks: overdue first, then by priority level."""
        return sorted(
            tasks,
            key=lambda t: (not t.is_overdue(), PRIORITY_ORDER.get(t.priority, 99))
        )

    @staticmethod
    def _to_minutes(slot: str) -> int:
        h, m = map(int, slot.split(":"))
        return h * 60 + m

    def _has_overlap(self, new_slot: str, new_duration: int) -> str | None:
        """Return the conflicting slot if new task overlaps an existing one, else None."""
        new_start = self._to_minutes(new_slot)
        new_end = new_start + new_duration
        for slot, task in self.schedule.items():
            existing_start = self._to_minutes(slot)
            existing_end = existing_start + task.duration_minutes
            if new_start < existing_end and existing_start < new_end:
                return slot
        return None

    def assign_task(self, task: Task, time_slot: str) -> None:
        """
        Assign a task to a time slot.
        On duration overlap: records a warning and skips the conflicting task
        instead of raising, so the schedule continues building.
        """
        conflict_slot = self._has_overlap(time_slot, task.duration_minutes)
        if conflict_slot is not None:
            existing = self.schedule[conflict_slot].title
            self.warnings.append(
                f"WARNING: '{task.title}' at {time_slot} ({task.duration_minutes} min)"
                f" overlaps '{existing}' at {conflict_slot} — skipped."
            )
            return
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

    def mark_task_complete(self, title: str) -> "Task":
        """
        Find a scheduled task by title (case-insensitive), mark it complete
        (which advances its due_date if recurring), remove it from the schedule,
        and return the updated task.

        Raises KeyError if no matching task is found.
        """
        for slot, task in list(self.schedule.items()):
            if task.title.lower() == title.lower():
                task.mark_complete()
                del self.schedule[slot]
                return task
        raise KeyError(f"No scheduled task found with title: '{title}'")

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
