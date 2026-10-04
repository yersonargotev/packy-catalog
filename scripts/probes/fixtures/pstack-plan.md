# Verify the sample command

Exercise one command change with observable evidence.

## How to read this

One box is one unit of work and names the evidence.
Check a box only when its evidence exists.
Use `playbooks/autopilot-full.md`.
Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] Read the execution playbook with `git show origin/main:pstack/skills/poteto-mode/playbooks/autopilot-full.md`.
- [ ] Schedule @AUDIT@ and record a status message.

### Spawn owners

- [ ] Assign the sample change to one owner.

### PR mechanics

- [ ] Open the sample change for review.

### Verdict and merge

- [ ] Verify the exact committed candidate before integration.

### Boot recipe

- [ ] Start the sample command in a temporary workspace.

## Add the sample command

**Depends on.** None.

**Files.**

- [ ] Edit `sample.js`.

**Build.**

- [ ] Print the sample result.

**You see.**

- [ ] The command prints `ready`.

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Run `node --test sample.test.js` and record success.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes on `inherit-parent` at the PR head.

- [ ] Lane 1. Run the sample. Save `lane-1.png`. Pass when it prints ready.
- [ ] Lane 2. Run the sample. Save `lane-2.png`. Pass when it prints ready.
- [ ] Lane 3. Run the sample. Save `lane-3.png`. Pass when it prints ready.
- [ ] Lane 4. Run the sample. Save `lane-4.png`. Pass when it prints ready.
- [ ] Lane 5. Run the sample. Save `lane-5.png`. Pass when it prints ready.
- [ ] Lane 6. Run the sample. Save `lane-6.png`. Pass when it prints ready.
- [ ] Lane 7. Run the sample. Save `lane-7.png`. Pass when it prints ready.
- [ ] Lane 8. Run the sample. Save `lane-8.png`. Pass when it prints ready.
- [ ] Lane 9. Run the sample. Save `lane-9.png`. Pass when it prints ready.
- [ ] Lane 10. Run the sample. Save `lane-10.png`. Pass when it prints ready.

**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Metric. Measure startup milliseconds.
- [ ] Probe. Alternate the same command on trunk and candidate.
- [ ] Baseline. Record trunk's median startup time.
- [ ] Rule. Fail if startup exceeds the agreed budget.

**Review gate.** None. This fixture exercises the checker only.

**Merge.**

- [ ] Require the verified candidate and passing checks.

## Close the program

- [ ] Record the result and remove temporary state.

## Appendix A. Prototype evidence

This fictional plan is an independently specified input fixture, not evidence of executing its tasks.
