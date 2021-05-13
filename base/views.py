from itsdangerous.exc import SignatureExpired
from django.shortcuts import render
from django.contrib import messages
from django.core.exceptions import NON_FIELD_ERRORS
from django.http.response import HttpResponseRedirect
from django.views.generic.edit import ProcessFormView


def error_403(request, exception):
    return render(request, 'errors/403.html', {'title': 'Forbidden'}, status=403)


def error_404(request, exception):
    return render(request, 'errors/404.html', {'title': 'Page Not Found'}, status=404)


class PrgView(ProcessFormView):
    def form_invalid(self, form):
        self.request.session['form-data'] = form.data
        errors = {}
        errors[NON_FIELD_ERRORS] = [_ for _ in form.non_field_errors()]

        for field in form:
            if field.errors:
                errors[field.html_name] = [_ for _ in field.errors]

        self.request.session['form-errors'] = errors
        return HttpResponseRedirect(self.request.get_full_path())

    def get_context_data(self, **kwargs):
        form_args, errors = self.get_form_kwargs(), {}

        try:
            form_args['data'] = self.request.session.pop('form-data')
            errors = self.request.session.pop('form-errors')
        except KeyError:
            pass

        if hasattr(self, 'object'):
            form_args['instance'] = self.object

        form = self.get_form_class()(**form_args)

        for field in form:
            while field.errors:
                field.errors.pop()

            if field.html_name not in errors:
                continue

            for error in errors[field.html_name]:
                if error not in field.errors:
                    form.add_error(field.html_name, error)

        while form.non_field_errors():
            form.errors[NON_FIELD_ERRORS].pop()

        if NON_FIELD_ERRORS in errors:
            for error in errors[NON_FIELD_ERRORS]:
                form.add_error(None, error)

        kwargs['form'] = form
        return super().get_context_data(**kwargs)


def perform_prg(request, cls_form, form_args, template, context, func_is_valid):
    if request.method == 'POST':
        form_args['data'] = request.POST
        form_args['files'] = request.FILES
        form = cls_form(**form_args)

        if form.is_valid():
            return func_is_valid(request, form)

        request.session['form-data'] = form.data
        errors = {}

        for field in form:
            if field.errors:
                errors[field.html_name] = [_ for _ in field.errors]

        request.session['form-errors'] = errors
        return HttpResponseRedirect(request.get_full_path())

    errors = {}

    try:
        form_args['data'] = request.session.pop('form-data')
        errors = request.session.pop('form-errors')
    except KeyError:
        pass

    form = cls_form(**form_args)

    for field in form:
        while field.errors:
            field.errors.pop()

        if field.html_name not in errors:
            continue

        for error in errors[field.html_name]:
            if error not in field.errors:
                form.add_error(field.html_name, error)

    context.update({'form': form})
    return render(request, template, context)


def load_timed_token(request, func_load):
    success = False

    try:
        func_load()
        success = True
    except SignatureExpired:
        messages.error(request, 'Expired link.')
    except ValueError as err:
        messages.error(request, err)
    except:
        messages.error(request, 'Invalid link.')

    return success
