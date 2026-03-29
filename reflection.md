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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
