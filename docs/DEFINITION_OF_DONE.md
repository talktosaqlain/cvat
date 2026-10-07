# Definition of Done

Written before starting. I'll tick each line at the end with proof next to it.

## Must have (1-4)

- [ ] Counts from the endpoint match the COCO json for person, car, chair, book, dog.
- [ ] Counting happens in one DB query, not a Python loop.
- [ ] A task with no annotations returns all labels with 0, no error.
- [ ] Page in CVAT UI opens from the task and shows a bar chart.
- [ ] Page shows a message when there's no data.
- [ ] Page shows an error with a retry button when the request fails (tested by stopping the server).

## Access (5)

- [ ] No login gives 401.
- [ ] User without access to the task gives 403.
- [ ] Owner/admin gives 200.

## Speed (6)

- [ ] 5 runs measured, raw output saved.
- [ ] Target met, or missed with the reason written down.

## Extra

- [ ] Group by shape type works (7), and why I picked it is written down.
- [ ] 8 and 9 not done, reason in PLAN.md.

## Hand-in

- [ ] Small commits, plan first, clear messages.
- [ ] No dead code or stray files.
- [ ] Everything unfinished is listed.
- [ ] PR opened in my fork, link sent with Loom.
