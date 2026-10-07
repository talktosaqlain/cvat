# Plan

Branch: `dev-test01`
Base commit: `0482c4793e291bc4a48808cf153fae9e88e7b8d7` (CVAT 2.76.1-alpha)

## Time

I acknowledged the email at 16:00, so my deadline is 00:00.
Setup took most of the afternoon (low disk space, re-forking, downloading COCO), so I'm starting the
actual work around 21:00 with about 3 hours left. I've cut the scope to fit that.

I used `0482c47` instead of latest develop because the CVAT Docker image already on my machine is
built from that exact commit. That saved me a big image pull/rebuild.

## How I'll get the counts

Each box is a row in `LabeledShape` (`cvat/apps/engine/models.py`). It has a `label` (FK to `Label`,
which has the name) and a `job` (FK to `Job`). Job → Segment → Task.

So for a task: filter shapes by `job__segment__task_id`, group by label, count. One query, done in
Postgres. Tracks and tags count as 1 each. Skeleton child points are skipped so a skeleton counts once.

## Order

| # | What | Time |
|---|------|------|
| - | Docs (this commit) | 15 min |
| 1 | `test` app with endpoint `GET /api/test/tasks/<id>/annotation-counts` | 30 min |
| 5 | Use CVAT login (401) and task permissions (403) | 15 min |
| 2, 3 | Page in cvat-ui at `/tasks/<id>/analytics` with a bar chart (chart.js is already in cvat-ui) | 45 min |
| 4 | Empty state and error state | 15 min |
| 6 | Measure the endpoint, 5 runs | 20 min |
| 7 | Group by shape type, only if I'm on time by 23:20 | 10 min |
| - | Tick DoD, open PR, record Loom | 30 min |

## Skipping

- 8 and 9 (WebSocket live updates and reconnect). Not enough time to do it properly. CVAT saves shapes
  with `bulk_create` so normal Django signals won't fire, and there's no Channels setup at this commit.
  I'd rather not leave half of it in the code.
- Project level totals. Task only.
- Frontend tests. I'll check backend numbers against the COCO json directly.

## Changes

(will add here if the plan changes)

## Decision record

(at the end, if I get there)
