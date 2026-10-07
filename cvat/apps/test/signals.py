# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from cvat.apps.engine.models import Job

from .live import publish_annotations_changed


@receiver(post_save, sender=Job, dispatch_uid=__name__ + ".notify_annotations_changed")
def notify_annotations_changed(sender, instance: Job, update_fields=None, **kwargs):
    # Annotations are written with bulk_create, which sends no signals. After writing them
    # CVAT calls job.touch(), which saves only updated_date, so that save is the hook.
    if update_fields != frozenset({"updated_date"}):
        return

    task_id = instance.segment.task_id
    transaction.on_commit(lambda: publish_annotations_changed(task_id))
