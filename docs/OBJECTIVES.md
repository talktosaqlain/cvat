# Objectives

## My machine

- CPU: Intel Core i5-10310U @ 1.70GHz (laptop)
- RAM: 16 GB
- OS: Windows 10 Pro 22H2, Docker Desktop (WSL 2)
- CVAT commit: `0482c4793e291bc4a48808cf153fae9e88e7b8d7`
- Data: COCO 2017 val, all 5000 images, `instances_val2017.json` imported as COCO 1.0

## MO-1: count endpoint speed

| Field | Entry |
|---|---|
| What is measured | Response time of `GET /api/test/tasks/<id>/annotation-counts` for the COCO task |
| How | `curl -w "%{time_total}"` from my machine with a login token (same as the page). 1 warm-up request, then 5 timed runs. Script: `docs/measurements/mo1.sh` |
| Target | Median of 5 runs at or below 150 ms |
| Conditions | Local Docker stack, the COCO task (41,866 shapes), nothing else running |
| Not included | First request after restarting containers, browser rendering time |

Why 150 ms: the page calls this as soon as it opens, and anything under ~200 ms feels instant.
Loading all shapes into Python and counting there should miss this, a `GROUP BY` in Postgres should hit it.
I'll try the slow way once too, to check that.

## Result

Target met. Median 77 ms, spread 40 ms (73 to 113 ms).

| Run | Plain | `?group_by=shape_type` |
|---|---|---|
| 1 | 92 ms | 132 ms |
| 2 | 77 ms | 134 ms |
| 3 | 113 ms | 132 ms |
| 4 | 74 ms | 132 ms |
| 5 | 73 ms | 113 ms |
| Median | 77 ms | 132 ms |
| Spread | 40 ms | 21 ms |

Task 2, 5000 images, 41,866 shapes. Raw output: `measurements/mo1-token.txt`, `measurements/mo1-token-shape-type.txt`.

### What I got wrong first

My first run used basic auth (`curl -u`) and got a median of 765 ms, way over target
(`measurements/mo1-basic-auth.txt`). Even CVAT's own `/api/users/self` took ~730 ms that way, so it
wasn't my code. Basic auth hashes the password on every request. The page doesn't do that, it uses a
token, so I changed the method to use a token. The SQL alone runs in 44 to 80 ms
(`measurements/mo1-explain.txt`).

### Slow way vs my way

Timed inside the server container, 5 runs each (`measurements/mo1-baseline.txt`):

- Loading every shape into Python and counting: median 1171 ms
- `GROUP BY` in Postgres (what the endpoint does): median 55 ms

So doing it in the DB is about 20x faster, and the slow way would have missed the target.
