from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state bootstrap ────────────────────────────────────────────────
# All objects live here so they survive reruns for the session.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_time_slots=["08:00", "12:00", "15:00", "18:00", "20:00"],
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ── Section 1: Add a Pet ───────────────────────────────────────────────────
st.subheader("Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", placeholder="e.g. Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

    dietary_input = st.text_input("Dietary needs (comma-separated)", placeholder="e.g. grain-free, no dairy")
    submitted = st.form_submit_button("Add Pet")

if submitted and pet_name.strip():
    dietary_needs = [d.strip() for d in dietary_input.split(",") if d.strip()]
    new_pet = Pet(name=pet_name.strip(), species=species, age=age, dietary_needs=dietary_needs)
    owner.add_pet(new_pet)           # ← Owner.add_pet() handles the data
    st.success(f"{new_pet.name} added!")

# Show current pets
if owner.pets:
    st.write("**Registered pets:**")
    for pet in owner.pets:
        ctx = pet.get_context()
        st.markdown(
            f"- **{ctx['name']}** ({ctx['species']}, age {ctx['age']}) "
            f"— {ctx['pending_tasks']} pending task(s)"
        )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Section 2: Add a Task ──────────────────────────────────────────────────
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)

        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
            category   = st.selectbox("Category", ["feeding", "grooming", "medication", "exercise", "other"])
            frequency  = st.selectbox("Frequency", ["once", "daily", "weekly"])
        with col2:
            duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority   = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            due_date   = st.date_input("Due date", value=date.today())

        task_submitted = st.form_submit_button("Add Task")

    if task_submitted and task_title.strip():
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            title=task_title.strip(),
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            due_date=due_date.isoformat(),
            frequency=frequency,
        )
        target_pet.add_task(new_task)   # ← Pet.add_task() handles the data
        st.success(f"Task '{new_task.title}' added to {target_pet.name}.")

    # Show all pending tasks across pets
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**Pending tasks:**")
        rows = [
            {
                "Pet": next((p.name for p in owner.pets if t in p.get_tasks()), "—"),
                "Task": t.title,
                "Category": t.category,
                "Priority": t.priority,
                "Duration": f"{t.duration_minutes} min",
                "Due": t.due_date,
                "Overdue": "⚠ Yes" if t.is_overdue() else "No",
            }
            for t in all_tasks
        ]
        st.table(rows)
    else:
        st.info("No pending tasks yet.")

st.divider()

# ── Section 3: Build Schedule ──────────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("Generate schedule", disabled=not owner.get_all_tasks()):
    plan = scheduler.build_plan()       # ← Scheduler.build_plan() does the work
    if plan:
        st.success("Schedule built!")
        st.text(scheduler.generate_summary())
    else:
        st.warning("No tasks could be scheduled. Add tasks first.")
