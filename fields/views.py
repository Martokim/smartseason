from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Field, FieldUpdate
from .forms import FieldForm, FieldUpdateForm


@login_required
def dashboard(request):
    """Display dashboard with all fields."""
    fields = Field.objects.all()
    context = {'fields': fields}
    return render(request, 'fields/dashboard.html', context)


@login_required
def field_list(request):
    """List all fields."""
    fields = Field.objects.all()
    context = {'fields': fields}
    return render(request, 'fields/field_list.html', context)


@login_required
def field_create(request):
    """Create a new field."""
    if request.method == 'POST':
        form = FieldForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fields:field_list')
    else:
        form = FieldForm()
    context = {'form': form}
    return render(request, 'fields/field_form.html', context)


@login_required
def field_detail(request, pk):
    """Display field details."""
    field = get_object_or_404(Field, pk=pk)
    updates = field.updates.select_related('agent').all()
    context = {'field': field, 'updates': updates}
    return render(request, 'fields/field_detail.html', context)


@login_required
def field_update(request, pk):
    """Update a field."""
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            return redirect('fields:field_detail', pk=field.pk)
    else:
        form = FieldForm(instance=field)
    context = {'form': form, 'field': field}
    return render(request, 'fields/field_form.html', context)


@login_required
def field_delete(request, pk):
    """Delete a field."""
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        field.delete()
        return redirect('fields:field_list')
    context = {'field': field}
    return render(request, 'fields/field_confirm_delete.html', context)


@login_required
@require_http_methods(["POST"])
def add_field_update(request, pk):
    """Add an update to a field."""
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        form = FieldUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.field = field
            update.agent = request.user
            update.save()
            updates = field.fieldupdate_set.all().order_by('-created_at')
            context = {'updates': updates}
            return render(request, 'fields/updates_list.html', context)
    return redirect('fields:field_detail', pk=field.pk)
