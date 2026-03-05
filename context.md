
# context.md — Codex Project Memory

This file provides persistent instructions and memory for the Codex agent.

Codex must read this file BEFORE starting any work.

---

## Project Goal

Build a Python tool that:

1. Collects job postings related to Excel / order management / reports
2. Filters relevant job posts
3. Scores leads based on keywords
4. Generates a lead list in Excel

Output:

out/leads.xlsx

---

## Codex Working Rules

Before coding:

1. Read context.md
2. Read devdoc.md
3. Understand project architecture
4. Execute development steps from sprint.md

---

## External Reference Docs

For special topics follow:

web_crawling_stability.md  
saramin_safe_collection.md

---

## Project Structure

job-lead-collector/

app/
 main.py
 collector.py
 filter.py
 scoring.py
 exporter.py

docs/
 devdoc.md
 sprint.md
 context.md
 ARCHITECTURE.md

---

## Execution

Run:

python main.py

Expected Output:

out/leads.xlsx

---

## Codex Responsibilities

1. Follow sprint.md order strictly
2. Keep functions small and readable
3. Avoid unnecessary dependencies
4. Handle errors safely
5. Ensure program runs after each sprint

---

## Development Progress

Codex updates this section after every sprint.

Sprint status:

Sprint1: done (2026-03-05)
Sprint2: done (2026-03-05)
Sprint3: done (2026-03-05)
Sprint4: done (2026-03-05)
Sprint5: done (2026-03-05)
Sprint6: done (2026-03-05)

Last run result:
python main.py -> success, out/leads.xlsx generated (70 rows, dedup+error handling+logging applied)

Next task:
Project baseline complete. Optional: add unit tests and scheduler automation.
