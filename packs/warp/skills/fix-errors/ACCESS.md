---
name: fix-errors
description: Fix compilation errors, linting issues, and test failures in the warp Rust codebase. Covers presubmit checks, WASM-specific errors, and running specific tests. Use when the user hits build errors, clippy or fmt failures, test failures, or needs to run or interpret presubmit before a PR.
---

## On-demand context

Use the initiating descriptor's `surface` and `snapshot_id` for this procedure
and every nested request, including requests made by a delegate:

```sh
packy get skill warp:<skill> --surface <initiating-surface> --snapshot <initiating-snapshot-id> --json
```

Read and follow prepared Warp entries at the authored links below. Native skill
registrations and installed sibling copies are unnecessary. Carry the same host,
snapshot, target project, and writable scratch/output context in delegate briefs.
Selection changes affect new independent requests only. Keep previously returned
paths; if retained content is missing, stop and restore that exact revision.
Never substitute a newer revision or another Pack's similarly named workflow.

Resolve supporting files relative to this entry and `resource_root`, reading
only the active branch's references. Resolve repository paths, specs, review
inputs and generated files against the intended target project. Select writable
scratch/output separately from immutable resource trees. Retrieval supplies
instructions only: model, worker, MCP, credential, repository, scheduler, runtime
and validation prerequisites remain unverified until checked in the active host.
Honor the source's approvals, domain boundaries, stopping rules and fallbacks.

Use only controls actually exposed by the initiating host. On Codex, use its
available local subagent launch, message/resume and wait controls; on Claude Code,
use its available Agent control and supported original-author follow-up. Check
available model identifiers and whether model selection is per child or per run.
Use separate launches when only run-wide model selection exists. If a required
control is absent, report the limitation and stop that branch unless its source
explicitly provides a fallback. A lifecycle success is not validation evidence.
Use the host's question control (with the source's choices and free-text option),
or ask in conversation and wait for the actual reply when no question tool exists.
Use available host file, shell, search and computer-use controls where applicable;
access does not provision Warp/Oz tools or remote execution. Remote-only checks
require an actual authorized remote capability; otherwise report the gap and use
only the source-defined fallback. Retrieval is content access, not invocation of any workflow or proactive feedback
trigger. It grants no approval to launch workers, access credentials, post external
content, commit, push or schedule anything. Execute only the requested procedure
under its preserved source contract and the active host/user authorization.

## Reviewed execution context

Select the actual Warp Rust checkout explicitly before running commands. Git,
Rust/Cargo, nextest, platform toolchains and repository scripts remain unverified
prerequisites. These commands are repository-specific; retrieval does not run
presubmit, install toolchains, or repair the project.

# fix-errors

Fix compilation errors, linting issues, and test failures in the warp Rust codebase.

## Overview

This skill helps resolve common issues encountered during development, including:
- Compilation errors (unused imports, type mismatches, etc.)
- Linting failures (clippy warnings)
- Formatting violations
- WASM-specific errors
- Test failures

Fix the reported failure with the narrowest useful command. Do not turn a targeted repair into repeated full-workspace validation.

## Full Presubmit

Run the full presubmit only when the user, task, or approved spec explicitly requires it:

```bash
./script/presubmit
```

This runs formatting checks, linting, and all tests. It is intentionally broader and more expensive than the default implementation workflow.

### Individual Checks

Run checks separately when debugging specific issues:

**Rust formatting:**
```bash
cargo fmt -- --check
```

**Clippy (full workspace):**
```bash
cargo clippy --workspace --all-targets --tests -- -D warnings
```

**WASM Clippy:**
```bash
cargo clippy --target wasm32-unknown-unknown --profile release-wasm-debug_assertions --no-deps
```

**Objective-C/C/C++ formatting:**
```bash
./script/run-clang-format.py -r --extensions 'c,h,cpp,m' ./crates/warpui/src/ ./app/src/
```

**All tests:**
```bash
cargo nextest run --no-fail-fast --workspace --exclude command-signatures-v2
cargo nextest run -p warp_completer --features v2
```

**Doc tests:**
```bash
cargo test --doc
```

## Running Specific Tests

**Single package:**
```bash
cargo nextest run -p <package_name>
```

**Filter by test name:**
```bash
cargo nextest run -E 'test(<substring>)'
```

**Specific package with filter:**
```bash
cargo nextest run -p <package_name> -E 'test(<substring>)'
```

**With output (no capture):**
```bash
cargo nextest run -p <package> --nocapture
```

## Common Error Types

### Unused Imports
Remove unused `use` statements identified by the compiler.

### Unused Constants
Remove constants that are defined but never used.

### Unknown Imports
Add the correct `use` statement for undefined types. Search the codebase to find the correct module path.

### Type Mismatches
Update function calls to pass arguments of the correct type. Common fixes:
- Use `.as_str()` instead of `.clone()` when a `&str` is expected
- Use `&value` when a reference is needed
- Use `.to_string()` when `String` is expected but `&str` is provided

### Struct Field Changes
When a struct adds/removes fields, update all places where it's constructed or destructured:
- Struct initialization
- Pattern matching (`match`, `if let`)
- Destructuring assignments

### Function Signature Changes
When a function adds a new parameter, update all call sites to provide the new argument:
- For `bool` params: pass `true` or `false` based on context
- For `Option<T>` params: pass `None` as default or `Some(value)` if needed

### Enum Variant Changes
When adding a new enum variant, update exhaustive `match` statements:
- Add a new match arm with appropriate handling
- Mirror the implementation pattern of similar variants

### Incorrect Trait Implementation
Fix trait implementations that return the wrong type or don't satisfy trait bounds.

### WASM-Specific Errors

WASM builds (`wasm32-unknown-unknown` target) don't support filesystem operations. Code that uses filesystem APIs must be gated behind the `local_fs` feature flag.

**Common WASM errors:**
- Dead code warnings for code only used in non-WASM builds
- Unused code that's only relevant when `local_fs` is available
- Tests that require filesystem access

**Fixes:**

**Gate tests behind `local_fs`:**
```rust
#[test]
#[cfg(feature = "local_fs")]
fn test_find_git_repo_with_worktree() {
    // Test that uses filesystem operations
}
```

**Conditionally allow dead code for types only used when `local_fs` is enabled:**
```rust
#[cfg_attr(not(feature = "local_fs"), allow(dead_code))]
#[derive(Clone, EnumDiscriminants, Serialize)]
pub enum ExampleType {
    // Variants only used when local_fs is enabled
    Variant1,
    Variant2,
    Variant3,
}
```

WASM errors are discovered by running:

```bash
cargo clippy --target wasm32-unknown-unknown --profile release-wasm-debug_assertions --no-deps
```

## Best Practices

**Before fixing:**
- Read the full error message to understand the root cause
- Check if multiple errors are related (fixing one may resolve others)
- For trait/type errors, verify you understand the expected vs actual types
- For WASM errors, check if code needs to be gated behind `local_fs`

**When fixing:**
- Fix one error type at a time when there are multiple issues
- Run the smallest applicable `cargo check` when it helps resolve compiler errors; do not repeat broad checks without a relevant code change
- For WASM errors, run WASM clippy to verify the fix
- For complex changes, run relevant tests after fixing

**After fixing:**
- Run the relevant `cargo nextest` tests and fix the code until they pass
- Run the applicable Clippy invocation and fix its findings; return to affected tests only when a fix materially changes behavior
- Run `./script/format` once after all other code changes are complete
- Do not rerun tests or Clippy after formatting, and do not add a full presubmit run, unless explicitly required
- If you only fixed a formatting failure and made no behavioral code change, rerun only the formatter
