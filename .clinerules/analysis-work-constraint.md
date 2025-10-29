# Analysis Work Constraint Rule

## Rule Description

**ALL analysis work and testing MUST be confined to the `analyze/` directory and its subdirectories.**

## Purpose

This rule ensures that:
- Analysis activities don't interfere with the main Cline codebase
- Test scripts and documentation remain organized and isolated
- The main source code remains clean and unmodified during analysis
- Analysis results can be easily reviewed and discarded if needed

## Scope

This rule applies to:
- All analysis-related file creation
- All test script development
- All documentation writing
- Any code modifications for testing purposes

## Permitted Locations

- `analyze/` (root analysis directory)
- `analyze/server-client-test/` (current analysis subdirectory)
- Any future subdirectories under `analyze/`

## Prohibited Locations

- `src/` (main source code)
- `webview-ui/` (frontend code)
- `tests/` (existing test suite)
- Any other directory outside `analyze/`

## Enforcement

When working on analysis tasks:
1. Always verify the target directory starts with `analyze/`
2. Never modify files outside the analysis directory
3. Create new subdirectories under `analyze/` for different analysis topics
4. Document all findings within the analysis directory structure

## Rationale

This constraint prevents accidental modifications to the production codebase during analysis and ensures that analysis work remains organized and easily removable if needed.

## Example Usage

✅ **Allowed:**
- `analyze/server-client-test/test-script.sh`
- `analyze/performance-tests/benchmark.js`
- `analyze/documentation/findings.md`

❌ **Prohibited:**
- `src/core/terminal-fix.ts`
- `webview-ui/src/components/Terminal.tsx`
- `tests/terminal-hang.test.ts`
