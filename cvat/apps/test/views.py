# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from cvat.apps.engine.models import Task

from .counts import get_annotation_counts
from .permissions import AnnotationCountsPermission
from .serializers import AnnotationCountsSerializer


@extend_schema(tags=["test"])
class AnnotationCountsViewSet(viewsets.GenericViewSet):
    queryset = Task.objects.select_related("project")
    filter_backends = []
    iam_permission_class = AnnotationCountsPermission

    @extend_schema(
        summary="Get the number of annotations per label for a task",
        parameters=[
            OpenApiParameter(
                "group_by",
                type=OpenApiTypes.STR,
                enum=["shape_type"],
                description="Also split each label's count by shape type",
            ),
        ],
        responses={"200": AnnotationCountsSerializer},
    )
    def retrieve(self, request, pk):
        group_by = request.query_params.get("group_by")
        if group_by not in (None, "shape_type"):
            raise ValidationError({"group_by": "Only 'shape_type' is supported"})

        task = self.get_object()
        labels = get_annotation_counts(task, by_shape_type=group_by == "shape_type")
        data = {
            "task_id": task.id,
            "total": sum(label["count"] for label in labels),
            "labels": labels,
        }
        return Response(AnnotationCountsSerializer(data).data)
