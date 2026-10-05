# Systems Genomics drylab task assignment

A reproducible pipeline that assigns drylab tasks (reanalyses of published bulk
RNA-seq datasets) to student groups, one task per group, based on the groups'
stated preferences.

## How it works

The pipeline is a rank-by-rank lottery with tiers:

1. **Read the preferences.** Each group's preference list becomes a sequence
   of tiers. Consecutive tasks from the same paper form one tier, which the
   group likes equally. Hints in brackets such as `(medium / neuroscience)` are
   kept as fallback information.
2. **Assign by tier.** In round *r*, every unassigned group applies to the
   free tasks in its *r*-th tier.
   - As many applicants as possible are served, and a fresh seeded lottery
     decides who.
   - Listing more or fewer tasks gives no advantage in a given round.
   - Within its tier, a winner gets the task the fewest other unassigned groups
     still want, so an indifferent choice never blocks another group.
3. **Use the hints.** Groups whose lists ran out but who gave hints are
   matched to the remaining tasks by difficulty and topic, using the same
   lottery.
4. **Hand out the rest.** Remaining groups, including those with no
   preference, get the leftover tasks at random.

A fixed seed makes every run reproducible. A simulation over 10,000 other seeds
reports each group's chance of each outcome, as a fairness check.

[`ASSIGNMENT_LOG_masked.md`](ASSIGNMENT_LOG_masked.md) records the design
discussion, the decisions, every revision and aggregate results. This
published copy contains no group identifiers and no per-group preferences or
results, so nothing in it can be traced back to a group. The full log
(`ASSIGNMENT_LOG.md`) is kept locally only.

## Environment

- Python ≥ 3.9
- [openpyxl](https://openpyxl.readthedocs.io/)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Input

`Systems Genomics Organisation 2026.xlsx` in the working directory, with two
tabs:

- **Drylab Groups** — the group number in column A and preferences in column M
  ("Preference"). Separate tasks with `/` or new lines, and put an optional
  hint in brackets, e.g. `3 / 5 / 19 (medium)`. Leave the cell empty for no
  preference.
- **Datasets** — the task number in column A, paper in B, task description in
  D and complexity in H. The complexity must start with Low, Low-medium,
  Medium, Medium-high or High.

The input and output files and the full log contain student information. They are excluded from version control (see `.gitignore`).

## Usage

```bash
python3 assign_tasks.py               # official run + 10,000-seed fairness check (~3 s)
python3 assign_tasks.py --simulate 0  # official run only
python3 assign_tasks.py --simulate N  # fairness check over N seeds
```

The assignment is printed and written to `Task assignment 2026.xlsx`, with
three sheets:

- **Assignment** — each group's task and which tier it came from.
- **Lottery log** — every round's applicants, lottery positions and results.
- **Fairness check** — each group's chance of each outcome across the
  simulated seeds.

After updating `ASSIGNMENT_LOG.md`, regenerate the published copy with:

```bash
python3 mask_log.py   # writes ASSIGNMENT_LOG_masked.md
```

In `ASSIGNMENT_LOG.md`, wrap group-level detail in `<!-- private -->` …
`<!-- /private -->` and give the de-identified wording in a following
`<!-- public … -->` comment. The script refuses to write the published copy if
any group number, per-group table row or group-linked task number remains.

The seed (`SEED`), file names, difficulty scale and topic definitions
(`NEURO_TASKS`) are constants at the top of `assign_tasks.py`.
