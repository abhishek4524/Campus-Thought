import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()
from blog.forms import BlogForm

data = {
    'text': 'Test autosave',
    'description': 'Hello world',
    'category': 'Programming',
    'is_draft': 'on',
    'seo_title': 'Test',
    'seo_description': 'Desc',
}
form = BlogForm(data)
print('valid', form.is_valid())
print('errors', form.errors)
for name, field in form.fields.items():
    print(name, type(field.widget).__name__, form[name].value())
