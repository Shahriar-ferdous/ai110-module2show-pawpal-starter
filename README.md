# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The core scheduling logic in `pawpal_system.py` goes beyond a basic task list with four algorithms built on top of the base `Scheduler` class:

- **Sort by time** — `sort_by_time()` returns scheduled tasks in chronological order using a `_to_minutes` key function, so output is always clock-ordered regardless of insertion order.
- **Filter tasks** — `filter_tasks(status, pet_name)` lets you query the live schedule by completion status, by pet, or both at once. It uses `id()` identity checks to reliably match task objects back to their owning pet.
- **Recurring task auto-advance** — calling `mark_complete()` on a daily or weekly task automatically advances its `due_date` by the correct `timedelta` and resets its status to pending, so it reappears in the next build without any manual intervention.
- **Conflict detection** — `detect_conflicts()` checks every pair of scheduled tasks for time-window overlap using interval arithmetic (`start_a < end_b and start_b < end_a`). It labels each conflict as `same_pet` or `cross_pet` and is optimized with a pre-built reverse lookup and `itertools.combinations` to avoid redundant work. `assign_task` uses the same overlap logic to emit a non-fatal warning and skip the conflicting task rather than crashing the program.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
