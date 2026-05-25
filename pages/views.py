from django.views.generic import TemplateView

from devices.dashboard import (
    build_dashboard_summary,
    build_device_health_rows,
    get_dashboard_queryset,
    sort_rows,
)


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = sort_rows(build_device_health_rows(get_dashboard_queryset()))
        context["summary"] = build_dashboard_summary(rows)
        context["device_rows"] = rows[:10]
        return context
