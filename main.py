from pawpal_system import Owner, Pet, Task, Scheduler

# ── Owner ──────────────────────────────────────────────────────────────────
owner = Owner(
    name="Jordan",
    available_time_slots=["08:00", "12:00", "15:00", "18:00", "20:00"]
)

# ── Pets ───────────────────────────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog", age=3, dietary_needs=["grain-free"])
luna  = Pet(name="Luna",  species="cat", age=5, dietary_needs=["wet food only"])

# ── Tasks for Mochi ────────────────────────────────────────────────────────
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

# ── Tasks for Luna ─────────────────────────────────────────────────────────
luna.add_task(Task(
    title="Wet food feeding",
    category="feeding",
    duration_minutes=10,
    priority="high",
    due_date="2026-03-29",
    frequency="daily",
))
luna.add_task(Task(
    title="Brush coat",
    category="grooming",
    duration_minutes=15,
    priority="medium",
    due_date="2026-03-29",
    frequency="weekly",
))
luna.add_task(Task(
    title="Play session",
    category="exercise",
    duration_minutes=20,
    priority="low",
    due_date="2026-03-29",
    frequency="daily",
))

# ── Register pets with owner ───────────────────────────────────────────────
owner.add_pet(mochi)
owner.add_pet(luna)

# ── Build and print schedule ───────────────────────────────────────────────
scheduler = Scheduler(owner)
scheduler.build_plan()

print(scheduler.generate_summary())
