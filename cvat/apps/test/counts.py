# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from collections import Counter

from django.db.models import Count

from cvat.apps.engine.models import JobType, LabeledImage, LabeledShape, LabeledTrack, Task


def get_annotation_counts(task: Task) -> list[dict]:
    """
    Counts annotations per label for a task, grouped in the database.
    A track counts once (not per frame), a skeleton counts once (its points are skipped).
    Ground truth and consensus jobs are left out so nothing is counted twice.
    """
    counts = Counter()
    for model in (LabeledShape, LabeledTrack, LabeledImage):
        queryset = model.objects.filter(
            job__segment__task_id=task.id, job__type=JobType.ANNOTATION
        )
        if model is not LabeledImage:
            queryset = queryset.filter(parent__isnull=True)

        for row in queryset.values("label_id").annotate(count=Count("id")).order_by():
            counts[row["label_id"]] += row["count"]

    labels = [
        {"id": label.id, "name": label.name, "color": label.color, "count": counts[label.id]}
        for label in task.get_labels()
    ]
    return sorted(labels, key=lambda label: (-label["count"], label["name"]))
