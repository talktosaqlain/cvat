# Definition of Done

Written before starting. I'll tick each line at the end with proof next to it.

## Must have (1-4)

- [x] Counts from the endpoint match the COCO json for person, car, chair, book, dog.
      All 80 labels match the COCO polygon part count, 41,866 total. See `evidence/counts-vs-coco.txt`
      and the note in PLAN.md on why that's parts, not objects.
- [x] Counting happens in one DB query, not a Python loop.
      `GROUP BY label_id` per annotation table in `cvat/apps/test/counts.py`. 55 ms vs 1171 ms for a
      Python loop, `measurements/mo1-baseline.txt`.
- [x] A task with no annotations returns all labels with 0, no error.
      Task 4, `evidence/auth-and-edge-cases.txt`.
- [x] Page in CVAT UI opens from the task and shows a bar chart.
      Task → Actions → Annotation counts, route `/tasks/<id>/annotation-counts`. Shown in the Loom.
- [x] Page shows a message when there's no data.
      "This task has no annotations yet" on task 4. Shown in the Loom.
- [x] Page shows an error with a retry button when the request fails (tested by stopping the server).
      Page open, `docker stop cvat_server`, flip the toggle → error box with Try again, chart comes back
      after `docker start`. Found and fixed a crash here (PLAN.md, Changes). Shown in the Loom.

## Access (5)

- [x] No login gives 401. `evidence/auth-and-edge-cases.txt`
- [x] User without access to the task gives 403. Same file (user `viewer`).
- [x] Owner/admin gives 200. Same file.

## Speed (6)

- [x] 5 runs measured, raw output saved. `measurements/mo1-token.txt`
- [x] Target met, or missed with the reason written down. Met: median 77 ms, target 150 ms. OBJECTIVES.md.

## Extra

- [x] Group by shape type works (7), and why I picked it is written down.
      `?group_by=shape_type`, 132 ms median (`measurements/mo1-token-shape-type.txt`), bad value gives 400.
      Reason in PLAN.md.
- [x] ~~8 and 9 not done~~ Done after all. Live update: `evidence/ws-check.txt` (no login rejected,
      logged in gets `annotations_changed` after a save). Reconnect: `docker restart cvat_server`,
      tag goes Reconnecting... then Live and counts reload. Shown in the Loom.

## Hand-in

- [x] Small commits, plan first, clear messages. `git log 0482c47..dev-test01`
- [x] No dead code or stray files. Dev only files (Docker mount override) kept outside the repo.
- [x] Everything unfinished is listed. PLAN.md, "Not done / known gaps".
- [ ] PR opened in my fork, link sent with Loom.
