from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, RedirectView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from .forms import ClientForm, EntryForm, ProjectForm
from .models import Client, Entry, Project

class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

def clients(request):
    """
    Deprecated by ClientCreateView below
    """
    if request.method == 'POST':
        # Create our form object with our POST data
        form = ClientForm(request.POST)
        if form.is_valid():
            # If the form is valid, create a client with submitted data
            # Below is the shortcut equivalent of:
            #
            #   client = Client()
            #   client.name = form.cleaned_data['name']
            #   client.save()
            #
            # A shorter way to do create an object, including saving, is:
            #
            #   Client.objects.create(name=form.cleaned_data['name'])
            #
            # Sometimes you don't want to save the object until the end,
            # sometimes you don't care!
            #
            # Since the form is a ModelForm, you can just call `save()`.
            form.save()
            return redirect('client-list')
    else:
        form = ClientForm()

    client_list = Client.objects.all()
    return render(request, 'clients.html', {
        'client_list': client_list,
        'form': form,
    })


class ClientCreateView(CreateView):
    """
    CBV version of above "clients" view function

    This view has a form for creating new clients. It also displays a list of
    clients. We could have used ListView for the latter part but then we
    wouldn't have the form handling of CreateView. It could be possible to mix
    in the functionality of CreateView and ListView classes with a combination
    of the mixin classes they comprise of but for the sake of simplicity we'll
    just pass the client queryset into the template context via
    get_context_data().
    """
    model = Client
    form_class = ClientForm
    template_name = 'clients.html'
    # Alternately to defining a get_success_url method returning
    # reverse('client-list'), reverse_lazy allows us to provide a url reversal
    # before the project's URLConf is loaded
    success_url = reverse_lazy('client-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ClientCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ClientCreateView, self).get_context_data(**kwargs)
        context['client_list'] = Client.objects.all()
        return context


def client_detail(request, pk):
    """
    Deprecated by ClientUpdateView below
    """
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            # Update client details
            client.name = form.cleaned_data['name']
            client.save()
            return redirect('client-list')
    else:
        # Initialise form with client data
        form = ClientForm(initial={'name': client.name})

    return render(request, 'client_detail.html', {
        'client': client,
        'form': form,
    })


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """
    CBV version of above "client_detail" view function
    """
    model = Client
    form_class = ClientForm
    template_name = 'client_detail.html'
    success_url = reverse_lazy('client-list')

    def get_queryset(self):
        qs = super(ClientUpdateView, self).get_queryset()
        qs = qs.filter(author=self.request.user)
        return qs


def entries(request):
    """
    Deprecated by EntryCreateView below
    """
    if request.method == 'POST':
        # Create our form object with our POST data
        entry_form = EntryForm(request.POST)
        if entry_form.is_valid():
            # If the form is valid, let's create and Entry with the submitted
            # data
            entry = Entry()
            entry.start = entry_form.cleaned_data['start']
            entry.stop = entry_form.cleaned_data['stop']
            entry.project = entry_form.cleaned_data['project']
            entry.description = entry_form.cleaned_data['description']
            entry.save()
            return redirect('entry-list')
    else:
        entry_form = EntryForm()

    entry_list = Entry.objects.all()
    return render(request, 'entries.html', {
        'entry_list': entry_list,
        'entry_form': entry_form,
    })


class EntryCreateView(LoginRequiredMixin, CreateView):
    """
    CBV version of above "entries" view function
    """
    model = Entry
    form_class = EntryForm
    success_url = reverse_lazy('entry-list')
    template_name = 'entries.html'

    def get_context_data(self, **kwargs):
        context = super(EntryCreateView, self).get_context_data(**kwargs)
        context['entry_list'] = Entry.objects.all()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(EntryCreateView, self).form_valid(form)

    def get_queryset(self):
        qs = super(EntryCreateView, self).get_queryset()
        qs = qs.filter(author=self.request.user)
        return qs


def projects(request):
    """
    Deprecated by ProjectCreateView below
    """
    if request.method == 'POST':
        # Create our form object with our POST data
        form = ProjectForm(request.POST)
        if form.is_valid():
            Project.objects.create(
                name=form.cleaned_data['name'],
                client=form.cleaned_data['client']
            )
            return redirect('project-list')
    else:
        form = ProjectForm()

    project_list = Project.objects.all()
    return render(request, 'projects.html', {
        'project_list': project_list,
        'form': form
    })


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    CBV version of above "projects" view function
    """
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project-list')
    template_name = 'projects.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data(**kwargs)
        context['project_list'] = Project.objects.all()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ProjectCreateView, self).form_valid(form)

    def get_queryset(self):
        qs = super(ProjectCreateView, self).get_queryset()
        qs = qs.filter(author=self.request.user)
        return qs


def project_detail(request, pk):
    """
    Deprecated by ProjectUpdateView below
    """
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Update project details
            project.name = form.cleaned_data['name']
            project.client = form.cleaned_data['client']
            project.save()
            return redirect('project-list')
    else:
        # Initialise form with project data
        form = ProjectForm(initial={
            'name': project.name,
            'client': project.client
        })

    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project_detail.html', {
        'project': project,
        'form': form,
    })


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """
    CBV version of above "project_detail" view function
    """
    model = Project
    form_class = ProjectForm
    template_name = 'project_detail.html'
    success_url = reverse_lazy('project-list')

    def get_queryset(self):
        qs = super(ProjectUpdateView, self).get_queryset()
        qs = qs.filter(author=self.request.user)
        return qs


class ClientRedirectView(LoginRequiredMixin, RedirectView):
    # Set redirect non-permanent. We may want to change it later
    permanent = False
    url = reverse_lazy('client-list')

def logout(request):
    auth_logout(request)
    return redirect('/')
