from pawpal_system import Owner, Pet, Task, Scheduler

# ── Owner ──────────────────────────────────────────────────────────────────
owner = Owner(
    name="Jordan",
    # "08:03" starts mid-way through the 5-min flea medication at 08:00 — triggers a conflict warning
    available_time_slots=["08:00", "08:03", "15:00", "18:00", "20:00"]
)

# ── Pets ───────────────────────────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog", age=3, dietary_needs=["grain-free"])
luna  = Pet(name="Luna",  species="cat", age=5, dietary_needs=["wet food only"])

# ── Tasks for Mochi (added out of order: low priority first) ───────────────
mochi.add_task(Task(
    title="Evening stroll",
    category="exercise",
    duration_minutes=20,
    priority="low",
    due_date="2026-03-29",
    frequency="daily",
))
mochi.add_task(Task(
    title="Morning walk",
    category="exercise",
    duration_minutes=30,
    priority="high",
    due_date="2026-03-29",
    frequency="daily",
))
mochi.add_task(Task(
    title="Flea medication",
    category="medication",
    duration_minutes=5,
    priority="high",
    due_date="2026-03-27",   # intentionally past → shows as overdue
    frequency="weekly",
))

# ── Tasks for Luna (added out of order: grooming before feeding) ───────────
luna.add_task(Task(
    title="Brush coat",
    category="grooming",
    duration_minutes=15,
    priority="medium",
    due_date="2026-03-29",
    frequency="weekly",
))
luna.add_task(Task(
    title="Wet food feeding",
    category="feeding",
    duration_minutes=10,
    priority="high",
    due_date="2026-03-29",
    frequency="daily",
))
luna.add_task(Task(
    title="Play session",
    category="exercise",
    duration_minutes=20,
    priority="low",
    due_date="2026-03-29",
    frequency="daily",
))

# ── Mark one task complete to demonstrate status filtering ─────────────────
luna.tasks[1].mark_complete()   # Wet food feeding → complete

# ── Register pets with owner ───────────────────────────────────────────────
owner.add_pet(mochi)
owner.add_pet(luna)

# ── Build schedule ─────────────────────────────────────────────────────────
scheduler = Scheduler(owner)
scheduler.build_plan()

# ── Scheduling warnings (non-fatal conflict messages) ─────────────────────
if scheduler.warnings:
    print("=== Scheduling Warnings ===")
    for w in scheduler.warnings:
        print(f"  {w}")
    print()

# ── Demo: conflict detection ───────────────────────────────────────────────
# Force an overlapping task directly into the schedule (bypasses assign_task)
# to demonstrate detect_conflicts. "Vet checkup" starts at 15:05 and runs
# 20 min. "Wet food feeding" occupies 15:00-15:10, so the windows overlap.
scheduler.schedule["15:05"] = Task(
    title="Vet checkup",
    category="medication",
    duration_minutes=20,
    priority="high",
    due_date="2026-03-29",
    frequency="once",
)

print("=== Conflict Detection ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(
            f"  CONFLICT [{c['kind']}]: '{c['task_a'].title}' ({c['pet_a']}) at {c['slot_a']}"
            f" overlaps '{c['task_b'].title}' ({c['pet_b']}) at {c['slot_b']}"
        )
else:
    print("  No conflicts detected.")

# remove the injected task so the rest of the demo is clean
del scheduler.schedule["15:05"]

# ── Demo: mark tasks complete and show advanced recurrence ─────────────────
# "Morning walk" was skipped (conflict warning), so only complete scheduled tasks.
completed_flea = scheduler.mark_task_complete("Flea medication")
print(f"Flea medication → new due_date: {completed_flea.due_date}")

# ── 1. Full schedule sorted chronologically ────────────────────────────────
print("=== Full Schedule (sorted by time) ===")
for slot, task in scheduler.sort_by_time():
    flag = " *** OVERDUE ***" if task.is_overdue() else ""
    print(f"  {slot} | [{task.priority.upper()}] {task.title} ({task.status}){flag}")

# ── 2. Filter: pending tasks only ──────────────────────────────────────────
print("\n=== Pending Tasks Only ===")
for slot, task in scheduler.filter_tasks(status="pending"):
    print(f"  {slot} | {task.title}")

# ── 3. Filter: tasks for Mochi only ───────────────────────────────────────
print("\n=== Mochi's Tasks Only ===")
for slot, task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"  {slot} | [{task.priority.upper()}] {task.title}")

# ── 4. Filter: Luna's pending tasks ───────────────────────────────────────
print("\n=== Luna's Pending Tasks ===")
for slot, task in scheduler.filter_tasks(status="pending", pet_name="Luna"):
    print(f"  {slot} | {task.title}")

# ── 5. Original summary ────────────────────────────────────────────────────
print()
print(scheduler.generate_summary())
