# Drylab task assignment — Systems Genomics 2026

> **Published copy.** Group numbers and all per-group preferences and results are removed, so nothing here can be traced back to a group, even with the final assignment at hand. The full log is kept privately by the course organiser.

Record of the discussion, decisions and runs that produced the 2026 drylab
task-to-group assignment. Started 2026-10-05.

## Revision history

| Version | Date | Change |
|---|---|---|
| v1 | 2026-10-05 | Algorithm agreed and first run |
| v2 | 2026-10-05 | Three groups updated their preferences; rerun with the same script and seed |
| v3 | 2026-10-05 | Algorithm fix approved by the course organiser: within a tier, give the winner the task fewest other groups still want (see 4.3). Same input and seed as v2. **Current.** |
| v3.1 | 2026-10-05 | Log only: corrected the first-tier count for v2 and v3 (18, not 19) |

## 1. Inputs

| File | Role | SHA-256 |
|---|---|---|
| `Systems Genomics Organisation 2026.xlsx` | Input (not published: contains student information) | `6da067f54f94bc520a9dda742a896331c4937cb1963a8b2cf797f7b9c3b43efe` |
| `assign_tasks.py` (v3, current) | Assignment pipeline | `a7b6f1f27d09a1bbc65604ed661dae640f06d5e0d86212fe19fe42cc95ec31c7` |
| `assign_tasks.py` (v1 and v2) | Pipeline before the fix | `39543fec7f19d391645e389ccdf1e263c350f955561e2a31da6be8649b7e6252` |
| `Task assignment 2026.xlsx` | Output (not published) | — |

Environment: Python 3.9.6, openpyxl 3.1.5.

If the input spreadsheet or the script is edited, its checksum changes and the
result may change too. Rerun the script and add a new version to this log.

## 2. Problem and rules (as given)

There are 26 tasks (bulk RNA-seq reanalysis, each with a difficulty rating) and
26 student groups of 2–3 students. Groups could state preferences for tasks,
topics or difficulty. Groups that stated nothing are treated as fine with any
task.

1. One group gets one task.
2. Each task goes to only one group.
3. Meet preferences as much as possible.
4. Groups listing more or fewer tasks get no advantage for their best
   preferred task.
5. Use a random draw when it is unclear which group should get a task.
6. Fix the random seed so the pipeline is reproducible.

## 3. Data observations

As of the current input (v1 in brackets):

- 23 groups gave preferences and 3 gave none. (v1: 22 and 4.)
- Five tasks are on nobody's list.
- The 23 groups with preferences list only 21 distinct tasks between them, so
  at least two of them must get a task they didn't list.
- Demand is uneven: the tasks of two papers are oversubscribed, and several
  tasks have two groups ranking them first.
- Three groups added difficulty or topic hints in brackets.
- Problems in the "Datasets" tab (still present, not fixed, they don't affect
  the assignment):
  - Task 11's sample list starts with a stray `c,`.
  - Task 20 lists `SRR21355697` twice and ends with a trailing comma.

### Preference changes v1 → v2

Three groups changed their preferences; one of them had given none before.

## 4. Discussion

### 4.1 Claude's initial analysis

Algorithms that maximise total satisfaction (minimum-cost or rank-maximal
matching) quietly favour groups with **short** lists. If two groups both want
the same task first, and only the second of them has a backup choice, the
optimiser gives the task to the first, so the second is punished for listing
more. That breaks rule 4. A rank-by-rank lottery was proposed instead: in
round r, groups compete equally for their r-th choice, contested tasks are
decided by a fresh lottery, unpreferred groups take what's left, and many seeds
are simulated to audit fairness.

Three questions were put to the user:

1. Is the preference order strict, or are some blocks (such as several
   neighbouring tasks from the same paper) equal tiers?
2. In the trade-off between rule 3 and rule 4, should rule 4 win?
3. Should the hints in brackets be used?

### 4.2 User decisions

1. **Tiers:** the Preference column can contain tiers. Neighbouring tasks from
   the same paper count as one equal tier.
2. **Rule 4 wins over rule 3:** a task picked by several groups must not go to
   a group just because it listed only that one task. "They should take their
   risk."
3. **Hints:** the difficulty and topic hints in brackets are used as a
   fallback.

### 4.3 Within-tier fix (found in v2, approved by the user, applied in v3)

**What went wrong in v2.** In round 1, a group whose tier held two equally
liked tasks was randomly given the one that another group listed as its next
choice. That other group then lost its own first-choice lottery and received a
random task, while the remaining task went to a group with no preference.
Giving the first group the other task from its tier would have left nobody
worse off.

**Cause.** The step that picks one task within a tier ignored which tasks
other groups still wanted.

**Fix.** Among the tasks in the winner's tier that keep everyone else served
this round still servable, give the winner the one wanted by the fewest other
unassigned groups. "Wanted" means listed in any tier of the group's own
preferences. Ties are broken by lottery.

**Effect.**
- It never changes who wins a lottery, and never changes how a winner feels
  about its task, since the winner ranks all tasks in its tier equally.
- It only stops an indifferent choice from needlessly taking another group's
  later choice. So it serves rule 3 without breaking rule 4.

## 5. Final algorithm (implemented in `assign_tasks.py`)

**Step 0: read the preferences.**
- Split each list into tiers: consecutive tasks with the same "Paper" value
  form one tier.
- Remove the bracketed hint and store it as a set of difficulty levels and
  topics. Difficulty scale: Low=1, Low-medium=2, Medium=3, Medium-high=4,
  High=5. Each task's level is the first word of "Task complexity".

**Step 1: explicit preferences.** For round r = 1, 2, …:
- Every unassigned group applies to the still-free tasks in its r-th tier.
  Groups with no free task in that tier wait for the next round.
- Within the round, a random order of applicants is drawn. Going down that
  order, a group is accepted if it can be served together with everyone already
  accepted. This serves as many groups as possible.
- Each accepted group then gets the task from its tier that the fewest other
  unassigned groups still want (lottery among ties). It chooses only among
  tasks that keep the other accepted groups servable. *(Added in v3; in
  v1/v2 the task within the tier was purely random.)*
- A fresh random draw is made in every round, so one unlucky draw doesn't
  follow a group through later rounds.

**Step 2: hint fallback.**
- Groups whose lists ran out but who gave hints rank the remaining free tasks
  by score: the distance to the nearest stated difficulty level, plus 1 for
  each stated topic the task doesn't match.
- Tasks with equal scores form one tier, and the Step 1 round-by-round lottery
  runs again.

**Step 3: random leftovers.**
- Groups whose lists ran out without hints, and groups with no preference, get
  the remaining tasks in a random order.
- Groups with no preference therefore never compete for a task that someone
  listed.

**Randomness.**
- One `random.Random(SEED)` drives every draw.
- `SEED = 1012705090` was drawn once with `secrets.randbelow(2**31)` and then
  fixed in the code.

**Audit.** The pipeline is rerun with seeds 0–9999, and each group's chance of
each outcome is reported in the "Fairness check" sheet.

### Choices made by Claude (not explicitly decided by the user)

- **Neuroscience tasks** (`NEURO_TASKS`), used for topic hints: all
  brain-related datasets, including the mouse cortical layer 4 and the bipolar
  disorder (post-mortem brain) datasets, whose task text doesn't say "brain".
- **Hint weighting:** one step of difficulty counts the same as one topic
  mismatch.
- **Serving as many groups as possible in each round** (decided by the random
  order) rather than resolving each task on its own lottery. Within a tier, a
  group that accepts more tasks is less likely to be blocked; this was judged
  consistent with "take their risk".
- **Measuring demand for the within-tier fix:** a simple count of other
  unassigned groups listing the task, in any tier and with equal weight.

## 6. Results (seed 1012705090)

Results per group are not published. Number of groups by outcome:

| Outcome | v1 | v2 | v3 (current) |
|---|---|---|---|
| Preference tier 1 | 17 | 18 | 18 |
| Preference tier 2 | 1 | 0 | 1 |
| Preference tier 3 | 1 | 1 | 1 |
| Hint fallback | 0 | 0 | 0 |
| Random, list exhausted | 3 | 4 | 3 |
| Random, no preference | 4 | 3 | 3 |

v3 changed the tasks of three groups compared with v2, exactly as predicted by
the analysis in 4.3. Every lottery draw was identical.

## 7. Fairness check (v3, seeds 0–9999)

- **List length gives no advantage:** seven groups compete in their first tier
  for the same five tasks. Each gets a first-tier task in about 71% of runs
  (5 out of 7), including a group that listed only a single task.
- **Head-to-head contests:** where two groups rank the same task first, the
  split is 49–51%.
- **Uncontested first choices:** ten groups always get a first-tier task.
- **Effect of the v3 fix:** one group now always gets a task from its list
  (before the fix it got a random task in about a quarter of runs). No group's
  odds of a first-tier task changed.
- **Remaining weak spots, caused by demand rather than the algorithm:** one
  group gets nothing from its list in about half of runs, because its later
  tiers are always used up in round 1, and another group's second tier is
  never available.

## 8. How to reproduce

```bash
python3 assign_tasks.py              # official run + 10,000-seed fairness check (~3 s)
python3 assign_tasks.py --simulate 0 # official run only
```

The same input file and seed always give the same assignment; this was checked
by comparing checksums of two runs, for v1, v2 and v3.

## 9. Open items

- Confirm the `NEURO_TASKS` set and the hint weighting. Neither affected the
  v1, v2 or v3 result.
- Decide whether to fix the problems in the "Datasets" tab (see section 3)
  before handing the tasks out.
