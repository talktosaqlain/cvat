# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cvat.apps.engine.models import Task

from .counts import get_annotation_counts
from .serializers import AnnotationCountsSerializer


@extend_schema(tags=["test"])
class AnnotationCountsViewSet(viewsets.GenericViewSet):
    queryset = Task.objects.select_related("project")
    filter_backends = []
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get the number of annotations per label for a task",
        responses={"200": AnnotationCountsSerializer},
    )
    def retrieve(self, request, pk):
        task = self.get_object()
        labels = get_annotation_counts(task)
        data = {
            "task_id": task.id,
            "total": sum(label["count"] for label in labels),
            "labels": labels,
        }
        return Response(AnnotationCountsSerializer(data).data)
