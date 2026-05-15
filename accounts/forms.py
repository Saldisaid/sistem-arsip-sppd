from django.contrib.auth.forms import PasswordChangeForm


class TailwindPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 outline-none transition focus:border-[#660300] focus:ring-2 focus:ring-[#660300]/30',
                'autocomplete': 'off',
            })
            field.label_suffix = ''
