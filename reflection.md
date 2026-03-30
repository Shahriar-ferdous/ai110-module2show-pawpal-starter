# PawPal+ Project Reflection

## 1. System Design
- The User should be able to add a pet
- The User will be able to see today's tasks
- The User should be able to schedule a walk
**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
I have included 4 classes in the UML design: Owner, Pet, Task, and Scheduler. 
Owner → provides constraints
Pet → provides context
Task → provides work items
Scheduler → builds the plan .

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

--- Yes, the design was missing pet: "Pet" = None   # which pet this task is for. The Task class has no link to pet and without this the build_plan can't use pet context(age, dietary needs) when scheduling a task.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints when building a plan:

1. **Time slots** — the owner declares available windows (e.g. "08:00", "12:00"). Tasks can only be placed into those slots; the scheduler will not invent new ones.
2. **Priority** — tasks are ranked high → medium → low using a `PRIORITY_ORDER` dict, so high-priority care (medication, feeding) lands in the earliest open slot.
3. **Overdue status** — any task whose `due_date` has already passed jumps to the front of the queue, ahead of all priority levels, so nothing critical is silently dropped.

Overdue status was treated as the most important constraint because a missed flea medication or vet-recommended feeding schedule has real health consequences, while a low-priority grooming task being delayed a day does not.

**b. Tradeoffs**

The scheduler uses a greedy first-fit strategy: it sorts tasks once, then assigns them to slots in order, stopping when it runs out of slots. This means the schedule is built in O(n log n) time and is easy to reason about, but it does not guarantee an optimal packing. A 30-minute walk assigned to the first slot may block two shorter tasks that could have fit there together.

This tradeoff is reasonable for a pet care scenario because the number of tasks and slots is small (typically under 10 each), so the theoretical suboptimality rarely matters in practice. Simplicity and predictability — the owner can look at the output and immediately understand why each task landed where it did — is more valuable here than squeezing out maximum utilization.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code (AI) across every phase of this project, but the way I used it shifted as the work got more concrete.

During design, I used it for brainstorming and UML generation — I described the four-class architecture in plain English and asked it to turn that into a Mermaid diagram. The most useful prompts at this stage were constraint-based: instead of asking "build me a pet app," I gave it a ten-rule refactoring spec and asked it to strip down the diagram to MVP only. That kind of structured prompt produced a much tighter result than open-ended requests.

During implementation, inline autocomplete in VS Code was most useful for filling in method bodies once the skeleton was in place — it could see the docstring and infer what `is_overdue()` or `mark_complete()` should do. For more complex logic like `detect_conflicts()` using `itertools.combinations`, I asked the chat to explain the algorithm before accepting it, which helped me understand the interval arithmetic (`start_a < end_b and start_b < end_a`) rather than just copy it.

For debugging, the most effective prompts were narrow: "why does `git rm --cached` return pathspec not found?" rather than "help me with git." Specific questions got specific, usable answers.

**b. Judgment and verification**

During the skeleton review, the AI flagged that `Task` had no reference to `Pet` and suggested adding `pet: "Pet" = None` as a field on the `Task` dataclass. I did not accept that suggestion as written.

The reason: putting a back-reference from `Task` to `Pet` creates a circular dependency and makes `Task` aware of its parent, which breaks the idea that `Task` is a simple value object. Instead I kept the relationship one-directional — `Pet` owns a `tasks: list[Task]` field, and `Owner.get_all_tasks()` traverses pets to collect tasks. The `Scheduler` only ever needs to call `owner.get_all_tasks()` and never touches the pet-task link directly.

I verified the choice was correct by tracing the data flow in `build_plan()`: it calls `owner.get_all_tasks()` → which iterates `owner.pets` → which reads `pet.tasks`. No circular reference, no `Task` knowing about `Pet`. The design stayed clean.

**c. VS Code Copilot / AI chat sessions and organization**

Using separate chat sessions for separate phases — UML design, skeleton generation, implementation, testing, UI wiring — helped significantly. Each session had a narrow context, which meant the AI's suggestions stayed relevant to the task at hand. When I mixed concerns.The suggestions became less focused. Keeping sessions phase-specific acted like a forcing function to finish one layer before moving to the next.

**d. Being the lead architect**

The biggest lesson was that AI is excellent at execution but has no stake in coherence. It will generate a technically correct method that doesn't belong in the class you're building, suggest an abstraction you don't need, or add a feature that looks useful but violates your refactoring rules — and it will do all of this confidently. The only thing that kept the system coherent was me holding the design in my head and pushing back when a suggestion drifted from it.

The refactoring rules I wrote before touching any code ("keep only MVP attributes," "one owner," "no external systems") were the most important thing I did. They gave me a clear standard to evaluate every suggestion against, so "should I accept this?" became a checklist, not a judgment call made in the moment.

---

## 4. Testing and Verification

**a. What you tested**

Five behaviors were tested:

1. **`mark_complete()` changes status** — confirmed `task.status` moves from `"pending"` to `"complete"`. Critical because the entire task lifecycle depends on this state transition being reliable.
2. **`add_task()` grows the pet's task list** — confirmed `len(pet.get_tasks())` increments correctly. Catches any bug where the list is reassigned instead of mutated.
3. **`sort_by_time()` returns chronological order** — inserted slots out of order (`"18:00"`, `"08:00"`, `"12:00"`) and confirmed the output is always `["08:00", "12:00", "18:00"]`. The schedule display depends on this.
4. **Daily recurrence advances `due_date`** — confirmed a `frequency="daily"` task dated `"2026-03-29"` moves to `"2026-03-30"` after completion, and status resets to `"pending"`. Without this the task would never reappear.
5. **`assign_task()` skips duplicates and warns** — confirmed the first task stays in the slot, the second is skipped, and exactly one warning is recorded. Prevents silent data loss in the schedule.

**b. Confidence**

**3 / 5.** The five tests cover the most critical paths and one key conflict scenario. The remaining two stars are withheld because the suite does not cover: overdue prioritization inside `build_plan()`, the `filter_tasks()` query logic, cross-slot time-window overlap (e.g. a 60-minute task at `08:00` blocking `08:30`), or the behavior difference between `"once"` and `"weekly"` recurrence after completion.

---

## 5. Reflection

**a. What went well**

The part I am most satisfied with is the `Scheduler` design. The decision to have `Scheduler` take only an `Owner` — and let `Owner.get_all_tasks()` be the single point that traverses all pets — made `build_plan()` very clean: fetch, sort, zip into slots. Each step is one line and immediately readable. It also meant adding a new pet or task required zero changes to `Scheduler` itself.

**b. What you would improve**

If I had another iteration I would replace the fixed `available_time_slots` list with a duration-aware slot system. Right now the scheduler assigns one task per slot without checking whether the previous task's duration has actually finished. A 30-minute walk at `08:00` and a 5-minute feeding at `08:03` get assigned as if they are independent, which is physically impossible. The `_has_overlap()` method catches this as a warning, but it would be better to generate slots dynamically based on task durations so the conflict never occurs in the first place.

**c. Key takeaway**

The most important thing I learned is that design decisions made before writing any code have more impact than any implementation choice made after. The UML refactoring rules — strip to MVP, one owner, no external systems — shaped every class in the project. When the AI suggested something that violated those rules (like a `pet` back-reference on `Task`), I had a clear reason to say no. Without that upfront design work, I would have accepted more suggestions and ended up with a system that grew in inconsistent directions.
