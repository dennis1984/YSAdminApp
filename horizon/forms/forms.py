# -*- encoding: utf-8 -*-
from django import forms
from django.forms import ChoiceField
from django.utils.encoding import force_text


class Form(forms.Form):
    def is_valid(self):
        verify_result = super(Form, self).is_valid()
        if verify_result:
            self.cleaned_data_filter(self.cleaned_data)
        return verify_result

    def cleaned_data_filter(self, cld):
        for key in cld.keys():
            if isinstance(cld[key], basestring):
                if not cld[key]:
                    cld.pop(key)
            else:
                if cld[key] is None:
                    cld.pop(key)
        return cld

    @property
    def cleaned_data(self):
        cld = super(Form, self).cleaned_data
        for key, value in self.declared_fields.items():
            if isinstance(value, ChoiceField):
                for key2, value2 in value.choices:
                    if key2 == cld[key] or force_text(key2) == cld[key]:
                        if isinstance(key2, int):
                            cld[key] = int(key2)
                        elif isinstance(key, float):
                            cld[key] = float(key2)
        return cld
