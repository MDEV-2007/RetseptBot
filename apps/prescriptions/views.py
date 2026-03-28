import asyncio
import logging
import threading

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView

from .forms import PrescriptionForm, PrescriptionItemFormSet
from .models import Prescription
from apps.drugs.models import Drug
from apps.patients.models import Patient

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_pdf(html: str) -> bytes:
    """Render an HTML string to PDF bytes via xhtml2pdf."""
    import io
    from xhtml2pdf import pisa
    buf = io.BytesIO()
    status = pisa.CreatePDF(io.StringIO(html), dest=buf)
    if status.err:
        raise RuntimeError(f'xhtml2pdf error: {status.err}')
    return buf.getvalue()


def _prescription_pdf_response(prescription, request, disposition='attachment') -> HttpResponse:
    """Build an HttpResponse containing a rendered prescription PDF."""
    html = render_to_string('prescription_pdf.html', {
        'prescription': prescription,
        'request': request,
    })
    pdf = _build_pdf(html)
    filename = f'prescription_{prescription.prescription_number}.pdf'
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response


def _run_async(coro) -> None:
    """Run an async coroutine in a dedicated thread with its own event loop.

    Raises any exception the coroutine raised after the thread finishes.
    """
    exc_holder: list[Exception] = []

    def _target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coro)
        except Exception as exc:
            exc_holder.append(exc)
        finally:
            loop.close()

    thread = threading.Thread(target=_target)
    thread.start()
    thread.join(timeout=30)
    if exc_holder:
        raise exc_holder[0]


# ── Public share views (no auth required) ─────────────────────────────────────

def prescription_share_view(request, token):
    prescription = get_object_or_404(
        Prescription.objects.select_related('patient', 'doctor'),
        share_token=token,
    )
    return render(request, 'prescriptions/prescription_public.html', {
        'prescription': prescription,
    })


def prescription_share_pdf_view(request, token):
    prescription = get_object_or_404(Prescription, share_token=token)
    try:
        return _prescription_pdf_response(prescription, request, disposition='inline')
    except Exception as exc:
        logger.exception('Public PDF generation failed: %s', exc)
        return HttpResponse('PDF generation failed.', status=500)


# ── Dashboard ──────────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard.html'

    def get(self, request):
        today = timezone.now().date()
        user = request.user

        agg = Prescription.objects.filter(doctor=user).aggregate(
            total=Count('id'),
            today=Count('id', filter=Q(created_at__date=today)),
        )
        context = {
            'total_patients':        Patient.objects.count(),
            'my_prescriptions':     agg['total'],
            'today_prescriptions':  agg['today'],
            'total_drugs':          Drug.objects.filter(is_active=True).count(),
            'recent_prescriptions': (
                Prescription.objects
                .filter(doctor=user)
                .select_related('patient')
                .only('id', 'diagnosis', 'created_at', 'patient__full_name')
                .order_by('-created_at')[:5]
            ),
        }
        return render(request, self.template_name, context)


# ── Prescription List ──────────────────────────────────────────────────────────

class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription
    template_name = 'prescriptions/prescription_list.html'
    context_object_name = 'prescriptions'
    paginate_by = 15

    def get_queryset(self):
        qs = (
            Prescription.objects
            .filter(doctor=self.request.user)
            .select_related('patient')
        )
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(patient__full_name__icontains=query) |
                Q(diagnosis__icontains=query)
            )
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


# ── Prescription Create ────────────────────────────────────────────────────────

class PrescriptionCreateView(LoginRequiredMixin, View):
    template_name = 'prescriptions/prescription_form.html'

    def _build_context(self, form, formset):
        return {
            'form':    form,
            'formset': formset,
            'title':   'New Prescription',
            'drugs':   Drug.objects.filter(is_active=True).order_by('name'),
        }

    def get(self, request):
        form = PrescriptionForm()
        patient_pk = request.GET.get('patient')
        if patient_pk:
            form.initial['patient'] = patient_pk
        return render(request, self.template_name, self._build_context(form, PrescriptionItemFormSet()))

    def post(self, request):
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user
            prescription.save()
            formset.instance = prescription
            formset.save()
            messages.success(request, f'Prescription {prescription.prescription_number} created successfully.')
            return redirect('prescription_detail', pk=prescription.pk)

        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, self._build_context(form, formset))


# ── Prescription Detail ────────────────────────────────────────────────────────

class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = 'prescriptions/prescription_detail.html'
    context_object_name = 'prescription'

    def get_queryset(self):
        return (
            Prescription.objects
            .filter(doctor=self.request.user)
            .select_related('patient', 'doctor')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        base = settings.DJANGO_APP_URL.rstrip('/')
        share_path = reverse('prescription_share', args=[self.object.share_token])
        ctx['share_url'] = f'{base}{share_path}'
        return ctx


# ── Prescription Delete ────────────────────────────────────────────────────────

class PrescriptionDeleteView(LoginRequiredMixin, DeleteView):
    model = Prescription
    template_name = 'prescriptions/prescription_confirm_delete.html'
    success_url = reverse_lazy('prescription_list')

    def get_queryset(self):
        return Prescription.objects.filter(doctor=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Prescription deleted.')
        return super().form_valid(form)


# ── PDF & Print ────────────────────────────────────────────────────────────────

@login_required
def prescription_pdf_view(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    try:
        return _prescription_pdf_response(prescription, request, disposition='attachment')
    except Exception as exc:
        logger.exception('PDF generation failed: %s', exc)
        messages.error(request, f'PDF generation failed: {exc}')
        return redirect('prescription_detail', pk=pk)


@login_required
def prescription_print_view(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    return render(request, 'prescription_print.html', {'prescription': prescription})


# ── Send to Telegram ───────────────────────────────────────────────────────────

@login_required
def send_to_telegram_view(request, pk):
    if request.method != 'POST':
        return redirect('prescription_detail', pk=pk)

    prescription = get_object_or_404(Prescription, pk=pk, doctor=request.user)
    recipient    = request.POST.get('recipient', '').strip()
    description  = request.POST.get('description', '').strip()

    if not recipient:
        messages.error(request, 'Username yoki ID kiriting.')
        return redirect('prescription_detail', pk=pk)

    try:
        from bot.sender import send_prescription_document

        pdf = _build_pdf(render_to_string('prescription_pdf.html', {
            'prescription': prescription,
            'request': request,
        }))

        _run_async(send_prescription_document(
            token=settings.TELEGRAM_BOT_TOKEN,
            recipient=recipient,
            pdf_bytes=pdf,
            prescription_number=prescription.prescription_number,
            patient_name=prescription.patient.full_name,
            description=description,
        ))
        messages.success(request, f'Retsept {recipient} ga muvaffaqiyatli yuborildi!')

    except ImportError as exc:
        messages.error(request, f'Dependency missing: {exc}')
    except Exception as exc:
        logger.exception('Telegram send failed: %s', exc)
        err = str(exc).lower()
        if any(phrase in err for phrase in ('chat not found', 'user not found', 'bad request')):
            messages.error(request, f'❗ "{recipient}" topilmadi. Username to\'g\'ri ekanligini tekshiring.')
        else:
            messages.error(request, f'Telegram xatosi: {exc}')

    return redirect('prescription_detail', pk=pk)
