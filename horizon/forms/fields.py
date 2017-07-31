from django import forms
from django.forms import widgets
from django.forms.widgets import force_text


class ChoiceField(forms.ChoiceField):
    def to_python(self, value):
        for key, value in self.choices:
            if key == value or force_text(key) == value:
                if isinstance(key, int):
                    return int(value)
                elif isinstance(key, float):
                    return float(value)
        return value

