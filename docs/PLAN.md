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

- 8 and 9 (WebSocket live updates and reconnect). Not enough time to do it properly. (Changed, see below.) CVAT saves shapes
  with `bulk_create` so normal Django signals won't fire, and there's no Channels setup at this commit.
  I'd rather not leave half of it in the code.
- Project level totals. Task only.
- Frontend tests. I'll check backend numbers against the COCO json directly.

## Changes

- **Did 8 and 9 after all.** At 22:35 items 1 to 7 were done and measured, so I gave WebSocket a hard cutoff
  of 23:20. It worked by 22:55 because I didn't need Channels: the server already runs on uvicorn with the
  `websockets` package, and nginx already forwards upgrade headers. So it's a small ASGI wrapper in
  `cvat/asgi.py`, no new dependency and no image rebuild.
- **Hook for changes.** I was right that `bulk_create` sends no signals, but CVAT calls `job.touch()` after
  every annotation save, which is a normal `save(update_fields=["updated_date"])`. I listen for that save
  and publish to Redis, so changes made in the import worker also reach the socket.
- **Measuring method.** Changed from basic auth to token auth, reason in OBJECTIVES.md.
- **Counting shapes, not COCO objects.** CVAT's COCO import stores each polygon part as its own shape
  (linked by `group`). So the endpoint says 41,866 and the COCO file has 36,781 objects. Every label matches
  the COCO polygon part count exactly (`evidence/counts-vs-coco.txt`). I kept counting shapes because that's
  what's stored and what CVAT shows elsewhere.
- **Item 7: group by shape type.** COCO import makes polygons for normal objects and masks for crowd
  regions. One number per class hides that, and it matters if you train detection vs segmentation.
  It's the same query with `type` added to the `GROUP BY`, so it costs ~55 ms extra.
- **Bug found while testing the error state.** With `cvat_server` stopped, Traefik sends `/api/...` to the
  UI container, which answers 200 with an HTML page. The page read `labels` from that and crashed.
  Now anything that isn't the expected JSON is shown as the normal error with Try again.
- **Dev UI on port 3000 can't POST** (Django CSRF origin check, production settings). Only affects my
  local dev setup, the page itself only does GET. I tested live updates by saving in the normal UI on 8080.

## Not done / known gaps

- The WebSocket only checks that you're logged in, not task access. It never sends data, only
  "task N changed", and the page then refetches over REST which does check access (403). A logged in user
  without access could learn that a task changed, nothing more. Fixing it needs CVAT's IAM context built
  outside a DRF request, which I didn't have time to do safely.
- The page is in cvat-ui, so the production UI image (port 8080) needs a rebuild to show it.
  I tested on the webpack dev server (port 3000).
- No automated tests. Checks are scripts with saved output in `docs/evidence/` and `docs/measurements/`.

## Decision record

**Took:** WebSocket only says "something changed", the page then calls the REST endpoint again.

**Rejected:** sending the new counts over the WebSocket.

**What rejecting it cost:** one extra HTTP request (~77 ms) after each change, and a short delay before
the chart updates. In return the counting code and the permission check live in one place (the REST
endpoint), and the socket can't leak counts to someone without access. Pushing counts would have
meant running the count query on every save for every open page, and checking task access inside
the socket handler.
