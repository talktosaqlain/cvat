# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from cvat.apps.engine.permissions import TaskPermission


class AnnotationCountsPermission:
    """
    Seeing a task's annotation counts needs the same right as viewing the task,
    so the check is handed to CVAT's own task rules instead of new ones.
    """

    @classmethod
    def create(cls, request, view, obj, iam_context):
        if obj is None:
            return []

        return [TaskPermission.create_scope_view(request, obj, iam_context)]
