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
| How | `curl -w "%{time_total}"` from my machine with basic auth. 1 warm-up request, then 5 timed runs. Script and output saved in `docs/measurements/` |
| Target | Median of 5 runs at or below 150 ms |
| Conditions | Local Docker stack, the COCO task (~36k annotations), nothing else running |
| Not included | First request after restarting containers, browser rendering time |

Why 150 ms: the page calls this as soon as it opens, and anything under ~200 ms feels instant.
Loading all shapes into Python and counting there should miss this, a `GROUP BY` in Postgres should hit it.
I'll try the slow way once too, to check that.

## Result

(after measuring)
