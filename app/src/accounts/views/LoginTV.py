from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from accounts.models import CustomUserModel


# /accounts/login/
class LoginTV(TemplateView):
    template_name = 'pages/login.html'

    def get(self, request, *args, **kwargs):
        page_data = {
            'title_page': 'Inicio Sesion',
            'module_name': 'Accounts',
            'show_message': False,
        }
        if request.user.is_authenticated:
            page_data['status'] = 'logged_in'
            page_data['message'] = 'Ya has iniciado sesion'
            url = reverse_lazy('accounts:home')
            return HttpResponseRedirect(url)

        context = self.get_context_data(**kwargs)
        return self.render_to_response({**context, **page_data})

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            url = reverse_lazy('home')
            return HttpResponseRedirect(url)
        else:
            page_data = {
                'title_page': 'Inicio Sesion',
                'module_name': 'Accounts',
                'show_message': True,
            }
            context = self.get_context_data(**kwargs)
            return self.render_to_response({**context, **page_data})