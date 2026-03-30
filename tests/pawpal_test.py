import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task, Owner, Scheduler


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


# ── Test 3: sort_by_time() returns slots in chronological order ────────────

def test_sort_by_time_returns_chronological_order():
    pet = Pet(name="Biscuit", species="cat", age=2)
    owner = Owner(name="Alex", available_time_slots=["18:00", "08:00", "12:00"])
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    # Manually place tasks out of order so sort_by_time has real work to do
    scheduler.schedule["18:00"] = make_task(title="Evening feed")
    scheduler.schedule["08:00"] = make_task(title="Morning walk")
    scheduler.schedule["12:00"] = make_task(title="Midday groom")

    sorted_slots = [slot for slot, _ in scheduler.sort_by_time()]

    assert sorted_slots == ["08:00", "12:00", "18:00"], (
        f"Expected ['08:00', '12:00', '18:00'], got {sorted_slots}"
    )
    print("PASS: test_sort_by_time_returns_chronological_order")


# ── Test 4: daily task advances due_date by one day after mark_complete() ──

def test_daily_task_advances_due_date_after_complete():
    task = make_task(frequency="daily", due_date="2026-03-29")

    task.mark_complete()

    assert task.due_date == "2026-03-30", (
        f"Expected '2026-03-30', got '{task.due_date}'"
    )
    assert task.status == "pending", (
        "Daily task should reset to 'pending' after advancing"
    )
    print("PASS: test_daily_task_advances_due_date_after_complete")


# ── Test 5: assign_task() warns and skips on duplicate time slot ────────────

def test_conflict_detection_warns_on_duplicate_slot():
    owner = Owner(name="Sam", available_time_slots=[])
    scheduler = Scheduler(owner)

    first  = make_task(title="Bath",  duration_minutes=30)
    second = make_task(title="Brush", duration_minutes=30)

    scheduler.assign_task(first,  "09:00")
    scheduler.assign_task(second, "09:00")  # exact duplicate — should be skipped

    assert "09:00" in scheduler.schedule, "First task should still be scheduled"
    assert scheduler.schedule["09:00"].title == "Bath", "First task should not be replaced"
    assert len(scheduler.warnings) == 1, (
        f"Expected 1 warning, got {len(scheduler.warnings)}"
    )
    assert "Brush" in scheduler.warnings[0], "Warning should mention the skipped task"
    print("PASS: test_conflict_detection_warns_on_duplicate_slot")


# ── Runner ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_mark_complete_changes_status()
    test_add_task_increases_pet_task_count()
    test_sort_by_time_returns_chronological_order()
    test_daily_task_advances_due_date_after_complete()
    test_conflict_detection_warns_on_duplicate_slot()
