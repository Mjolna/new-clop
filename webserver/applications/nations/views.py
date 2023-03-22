from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, View

from misc.cached import get_all_recipes
from misc.errors import exception_to_message
from misc.views import HasNationMixin

from .forms import CreateNationForm, EditNationForm
from .models import NationRecipe


class CreateNationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'nations/create_nation.html'
    success_url = reverse_lazy('nation_overview')
    form_class = CreateNationForm

    def test_func(self):
        # Disallow users with nations from creating new ones
        return not self.request.user.has_nations

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NationOverview(HasNationMixin, UpdateView):
    template_name = 'nations/overview.html'
    form_class = EditNationForm
    success_url = reverse_lazy('nation_overview')

    def get_object(self, queryset=None):
        return self.request.user.profile.active_nation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nation'] = context['form'].instance

        return context


class BuildingActionView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        building_id = int(data['building_id'])
        action = data['action']
        amount = int(data['amount'])

        nation = request.user.profile.active_nation
        building = nation.buildings.get(id=building_id)

        with exception_to_message(request):
            if action == 'disable':
                building.disable(amount)
                messages.success(request, f'Disabled {amount} of {building.name}')
            elif action == 'enable':
                building.enable(amount)
                messages.success(request, f'Enabled {amount} of {building.name}')
            elif action == 'destroy':
                satisfaction = building.destroy(amount)
                messages.success(request, f'Destroyed {amount} of {building.name} and gained {satisfaction} satisfaction')

        return redirect('nation_overview')


class NationActionsView(HasNationMixin, TemplateView):
    template_name = 'nations/actions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nation'] = self.request.user.profile.active_nation

        return context


class RecipeBuyView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        recipe_id = int(kwargs['recipe_id'])
        amount = int(data['amount'])

        nation = request.user.profile.active_nation
        recipe = NationRecipe.no_prefetch.get(id=recipe_id)
        recipe.update_from_cache(recipe_amount=amount)

        with exception_to_message(request):
            nation.buy_recipe(recipe)

        return redirect('nation_actions')
