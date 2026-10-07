# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from collections import Counter, defaultdict

from django.db.models import Count

from cvat.apps.engine.models import JobType, LabeledImage, LabeledShape, LabeledTrack, Task


def get_annotation_counts(task: Task, *, by_shape_type: bool = False) -> list[dict]:
    """
    Counts annotations per label for a task, grouped in the database.
    A track counts once (not per frame), a skeleton counts once (its points are skipped).
    Ground truth and consensus jobs are left out so nothing is counted twice.
    With by_shape_type, each label also gets a split by shape type
    (rectangle, polygon, mask, ...), with tracks under "track" and tags under "tag".
    """
    counts = Counter()
    type_counts = defaultdict(Counter)
    for model, kind in ((LabeledShape, None), (LabeledTrack, "track"), (LabeledImage, "tag")):
        queryset = model.objects.filter(
            job__segment__task_id=task.id, job__type=JobType.ANNOTATION
        )
        if model is not LabeledImage:
            queryset = queryset.filter(parent__isnull=True)

        fields = ["label_id"]
        if by_shape_type and model is LabeledShape:
            fields.append("type")

        for row in queryset.values(*fields).annotate(count=Count("id")).order_by():
            counts[row["label_id"]] += row["count"]
            if by_shape_type:
                type_counts[row["label_id"]][row.get("type", kind)] += row["count"]

    labels = []
    for label in task.get_labels():
        entry = {"id": label.id, "name": label.name, "color": label.color, "count": counts[label.id]}
        if by_shape_type:
            entry["by_shape_type"] = dict(type_counts[label.id])
        labels.append(entry)

    return sorted(labels, key=lambda label: (-label["count"], label["name"]))
