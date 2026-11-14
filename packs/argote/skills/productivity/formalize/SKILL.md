---
name: formalize
description: Formalize existing local changes through an issue, a pull request, a protected merge, cleanup, and sync.
disable-model-invocation: true
---

**Formalize** the changes already made in this checkout: give them a tracked issue, deliver them through one pull request, integrate it, and leave the checkout clean on the synced integration branch.

Invoking this skill is the user's approval to create the issue, open the pull request, merge it once every gate passes, and delete the delivery branch, for exactly the changes scoped in step 1. Record that approval in the issue body. Any gate that fails ends the run: stop, leave the state as it is, and report the evidence.

## 1. Scope the change

Read the complete diff, including untracked files. The change is everything the user named, or the whole diff when they named nothing. When the diff holds work that looks unrelated to the rest, ask which part to formalize before continuing.

Done when every changed path is either in scope or explicitly left out.

## 2. Learn the repo's conventions

The repository is the source of truth for format and process. Read its steering files and delivery docs, and the most recent merged pull requests with their issues. Take from them: the issue and pull request body structure, labels, branch and commit naming, the validation command, the merge path, and any sync steps beyond the integration branch.

Done when each of those has an answer drawn from the repo, or a noted default where the repo is silent.

## 3. Validate

Run the repo's validation command on the scoped change, against a clean baseline when the repo supports one. Keep the exact command and result as evidence.

Done when validation passes.

## 4. Create the issue

Open one issue stating the problem the change solves and its scope and acceptance, in the repo's format and with its approval label when it has one.

## 5. Open the pull request

Create a branch from the current integration branch, commit only the scoped paths, and push. Open one pull request targeting the integration branch that closes exactly the new issue through the tracker's closing mechanism. Its body carries the validation evidence.

Done when every required check on the pushed head reaches a passing terminal state.

## 6. Merge

Use the repo's protected merge path and its delivery tooling when it has one, bound to the exact head that passed. Without a declared path, prefer a merge queue, then squash merge.

Done when the tracker confirms the integration commit and the issue is closed.

## 7. Clean and sync

Delete the delivery branch locally and on the remote. Switch to the integration branch and fast-forward it to the remote. Run the extra sync steps the repo declares. Changes left out in step 1 stay in the working tree untouched.

Done when the checkout sits on the integration branch at the integration commit, and any post-merge workflow on that commit has passed.

Report the issue, the pull request, the integration commit, and anything left out or left pending.
