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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
