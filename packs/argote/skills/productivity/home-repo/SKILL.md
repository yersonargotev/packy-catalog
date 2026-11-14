---
name: home-repo
description: Set up a Home Repo that owns your shared skills, AGENTS.md, and docs, with navigation pointers to your other repos.
disable-model-invocation: true
---

A **Home Repo** is the one repository where every agent session starts. It owns the shared skills, the steering files (`AGENTS.md`, `CLAUDE.md`), and the agent-facing docs. Its steering file carries a **navigation pointer** to each other repo, so a single session can plan and change across all of them. Pattern reference: <https://www.aihero.dev/the-home-repo-pattern>.

Run this from the folder that holds the user's repos. Stay read-only until the plan in step 3 is approved. Leave `.env` and other secret files unread. Look up facts yourself; bring the user only decisions, in numbered rounds, each with your recommended answer.

## 1. Inventory the repos

Find every git repo under the working folder. Record each one's path, remote, visibility, and last commit date. Then ask:

1. Which repos the Home Repo should point to.
2. Where the Home Repo lives: an existing repo or a new one, and its path.
3. Whether it is personal or shared with a team.
4. Which steering file the harness loads: `AGENTS.md`, `CLAUDE.md`, or both.

When the inventory reaches thousands of repos, tell the user a skills marketplace fits better than a Home Repo and let them choose before continuing.

Done when every repo is marked included or excluded and all four answers are recorded.

## 2. Inventory the shared material

Across the included repos, list every skill (a folder containing `SKILL.md`), every `AGENTS.md` and `CLAUDE.md`, and every agent-facing doc. Assign each item exactly one bucket:

- **shared**: useful beyond its repo; moves to the Home Repo.
- **duplicate**: the same material in several repos; one copy moves to the Home Repo and the rest are removed.
- **repo-specific**: only meaningful inside its repo; stays.
- **installed**: placed and managed by a tool or package manager; stays under that tool's control.

Done when every listed item has a bucket.

## 3. Agree the plan

Show the user:

- A table with one row per item: current location, bucket, destination.
- The full draft of the Home Repo's steering file.

The draft carries one navigation pointer per included repo, under an `## Other Repos` heading, in this form:

```md
- <name> (<what it is>): <local path>. Clone from <remote> if missing.
```

Append a hint when a repo needs one, such as `Read its AGENTS.md before changing it.` Past about 20 repos, apply progressive disclosure: one pointer file per business area, and one line per area in the steering file:

```md
- Billing (invoices, payments, tax): see repos/billing.md
```

The draft also states the working conventions: sessions start in the Home Repo; each other repo is cloned once, and each feature gets its own worktree inside that clone.

Done when the user approves the table and the draft.

## 4. Apply the plan

1. Create the Home Repo and write the approved steering file. When the harness loads both `AGENTS.md` and `CLAUDE.md`, keep the content in `AGENTS.md` and make `CLAUDE.md` import it.
2. Copy every **shared** and **duplicate** item to its destination.
3. In each child repo, create a new local branch and remove the copies that moved.
4. Commit in the Home Repo.

Leave every push to the user. Report the Home Repo path, its commit, and the branch created in each child repo.
