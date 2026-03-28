from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Drug


class DrugListView(LoginRequiredMixin, ListView):
    model = Drug
    template_name = 'drugs/drug_list.html'
    context_object_name = 'drugs'
    paginate_by = 30

    def get_queryset(self):
        qs = Drug.objects.filter(is_active=True)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(generic_name__icontains=q) | qs.filter(category__icontains=q)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        # Use the already-evaluated paginator queryset count — no extra DB hit
        ctx['total_count'] = self.get_queryset().count()
        ctx['categories'] = (
            Drug.objects
            .filter(is_active=True)
            .exclude(category='')
            .values_list('category', flat=True)
            .distinct()
        )
        return ctx


class DrugDetailView(LoginRequiredMixin, DetailView):
    model = Drug
    template_name = 'drugs/drug_detail.html'
    context_object_name = 'drug'
