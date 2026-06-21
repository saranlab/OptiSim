"""Dashboard URL routes."""

from __future__ import annotations

from django.urls import path

from dashboard.views import ExperimentDashboardView, ExperimentRigorReportView

app_name = "dashboard"

urlpatterns = [
    path("", ExperimentDashboardView.as_view(), name="experiment-dashboard"),
    path("report/", ExperimentRigorReportView.as_view(), name="experiment-report"),
]
