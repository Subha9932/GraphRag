# Optimization for Codebase GraphRAG - Phase 4: Safe Custom Prompt

## Goal
Recover from ingestion failures and successfully index the codebase with **Codebase Specifics** (not generic text) using a "Safe Custom Prompt".

## The Problem
- The default "Regex Parser" crashes if Entity Names contain special characters (e.g. `src/main.py` -> `src` group error).
- The "JSON Parser" is unstable with this model/setup.

## The Solution
We will use a **Hybrid Approach**:
1.  **Mechanism**: Use the robust default Regex Parser.
2.  **Prompt**: Custom prompt *strictly* formatted to output "Safe Names".
    - Entity Name: `SRC_MAIN_PY` (Uppercase, Underscores only)
    - Description: "Main file at src/main.py" (Real data goes here)

## Changes
### 1. Prompt Engineering (`extract_graph.txt`)
- Rewrite examples to demonstrate "Safe Naming".
    - `("entity", "SRC_MAIN_PY", "FILE", "File located at src/main.py")`

### 2. Verification
- **Re-index**: strictly run `python -m graphrag index`.
- **Monitor**: Watch `indexing-engine.log` for parsing errors.

## User Action
- None. I will handle the execution.
