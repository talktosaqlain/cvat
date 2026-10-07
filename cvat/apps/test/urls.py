# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from django.urls import path

from .views import AnnotationCountsViewSet

urlpatterns = [
    path(
        "test/tasks/<int:pk>/annotation-counts",
        AnnotationCountsViewSet.as_view({"get": "retrieve"}, detail=True),
        name="test-annotation-counts",
    ),
]
