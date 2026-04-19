from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Field, FieldUpdate
from .forms import FieldForm, FieldUpdateForm
from functools import wraps


# ── Helpers ────────────────────────

def admin_required(view_func):
    """Blocks non-admins with a 403. Apply after @login_required."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def get_fields_for_user(user):
    """Admins see everything. Agents see only their assigned fields."""
    qs = Field.objects.select_related('assigned_agent')
    if user.is_admin:
        return qs.all()
    return qs.filter(assigned_agent=user)


# ── Dashboard ──────────────

@login_required
def dashboard(request):
    fields = get_fields_for_user(request.user)
    fields_list = list(fields)

    # Stage breakdown for the insight section
    stage_breakdown = {
        'planted': sum(1 for f in fields_list if f.stage == 'PLANTED'),
        'growing': sum(1 for f in fields_list if f.stage == 'GROWING'),
        'ready': sum(1 for f in fields_list if f.stage == 'READY'),
        'harvested': sum(1 for f in fields_list if f.stage == 'HARVESTED'),
    }

    # Fields that need attention 
    needs_attention = [f for f in fields_list if f.status == 'at_risk']

    context = {
        'fields': fields_list,
        'total': len(fields_list),
        'active_count': sum(1 for f in fields_list if f.status == 'active'),
        'at_risk_count': sum(1 for f in fields_list if f.status == 'at_risk'),
        'completed_count': sum(1 for f in fields_list if f.status == 'completed'),
        'stage_breakdown': stage_breakdown,
        'needs_attention': needs_attention,
    }
    return render(request, 'fields/dashboard.html', context)


# ── Field list ─────────────

@login_required
def field_list(request):
    fields = get_fields_for_user(request.user)
    return render(request, 'fields/field_list.html', {'fields': fields})


# ── Field detail ───────────────────────────────

@login_required
def field_detail(request, pk):
    field = get_object_or_404(Field, pk=pk)

    # Agents may only view fields assigned to them
    if request.user.is_agent and field.assigned_agent != request.user:
        raise PermissionDenied

    updates = field.updates.select_related('agent').all()
    form = FieldUpdateForm()

    return render(request, 'fields/field_detail.html', {
        'field': field,
        'updates': updates,
        'form': form,
    })


# ── Create field ──────────────────────────

@login_required
@admin_required
def field_create(request):
    form = FieldForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Field created successfully.')
        return redirect('fields:field_list')
    return render(request, 'fields/field_form.html', {
        'form': form,
        'title': 'Create Field',
    })


# ── Edit field

@login_required
@admin_required
def field_update(request, pk):
    field = get_object_or_404(Field, pk=pk)
    form = FieldForm(request.POST or None, instance=field)
    if form.is_valid():
        form.save()
        messages.success(request, 'Field updated successfully.')
        return redirect('fields:field_detail', pk=pk)
    return render(request, 'fields/field_form.html', {
        'form': form,
        'title': 'Edit Field',
        'field': field,
    })


# ── Delete field 

@login_required
@admin_required
def field_delete(request, pk):
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        field.delete()
        messages.success(request, 'Field deleted.')
        return redirect('fields:field_list')
    return render(request, 'fields/field_confirm_delete.html', {'field': field})


# ── Add field update (HTMX endpoint) 

@login_required
def add_field_update(request, pk):
    field = get_object_or_404(Field, pk=pk)

    if request.user.is_agent and field.assigned_agent != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = FieldUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.field = field
            update.agent = request.user
            update.save()

            # Keep the field's stage in sync with the latest update
            field.stage = update.stage
            field.save()

            # HTMX requests get back just the updates fragment, not a full page
            if request.headers.get('HX-Request'):
                updates = field.updates.select_related('agent').all()
                return render(request, 'fields/partials/updates_list.html', {
                    'field': field,
                    'updates': updates,
                })

    return redirect('fields:field_detail', pk=pk)