import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task


def make_task(**overrides):
    """Return a Task with sensible defaults; override any field via kwargs."""
    defaults = dict(
        title="Test task",
        category="grooming",
        duration_minutes=10,
        priority="low",
        due_date="2026-03-29",
        frequency="once",
    )
    defaults.update(overrides)
    return Task(**defaults)


# ── Test 1: mark_complete() changes status ─────────────────────────────────

def test_mark_complete_changes_status():
    task = make_task()
    assert task.status == "pending", "Task should start as pending"

    task.mark_complete()

    assert task.status == "complete", "Task status should be 'complete' after mark_complete()"
    print("PASS: test_mark_complete_changes_status")


# ── Test 2: add_task() increases pet's task count ─────────────────────────

def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0, "Pet should start with no tasks"

    pet.add_task(make_task(title="Walk"))
    pet.add_task(make_task(title="Feed"))

    assert len(pet.get_tasks()) == 2, "Pet should have 2 tasks after adding two"
    print("PASS: test_add_task_increases_pet_task_count")


# ── Runner ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_mark_complete_changes_status()
    test_add_task_increases_pet_task_count()
