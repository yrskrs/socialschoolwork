"""
Форми Django для SchoolNet.

Включає:
    - AssignmentForm      — створення та редагування завдань
    - TeacherLoginForm    — вхід вчителя
    - ClassSelectForm     — вибір класу для учня
    - TeacherProfileForm  — редагування профілю вчителя
"""

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Assignment, Teacher, ClassGroup, Subject


# ─── Кастомний widget для множинного завантаження файлів (Django 6+) ───────────
class MultipleFileInput(forms.FileInput):
    """HTML5 FileInput з атрибутом multiple для вибору кількох файлів."""
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {'multiple': 'multiple'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def value_from_datadict(self, data, files, name):
        """Повертає список завантажених файлів."""
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class MultipleFileField(forms.FileField):
    """Поле форми що приймає кілька файлів одночасно."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={
            'class': 'form-file-input',
            'accept': '*/*',
            'id': 'id_files',
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Якщо порожньо — повертаємо пустий список
        if not data:
            return []
        if not isinstance(data, list):
            data = [data]
        result = []
        for item in data:
            result.append(super().clean(item, initial))
        return result


# ─── Форма авторизації вчителя ─────────────────────────────────────────────────

class TeacherLoginForm(forms.Form):
    """Форма входу вчителя (username + password)."""

    username = forms.CharField(
        label='Логін',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введіть логін',
            'autocomplete': 'username',
            'class': 'form-input',
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введіть пароль',
            'autocomplete': 'current-password',
            'class': 'form-input',
        })
    )


# ─── Форма вибору класу учнем ─────────────────────────────────────────────────
class ClassSelectForm(forms.Form):
    """Форма вибору класу учнем при вході до стрічки."""

    class_group = forms.ModelChoiceField(
        queryset=ClassGroup.objects.all().order_by('grade', 'letter'),
        label='Ваш клас',
        empty_label='— Всі класи —',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


# ─── Форма профілю вчителя ────────────────────────────────────────────────────
class TeacherProfileForm(forms.ModelForm):
    """Форма редагування профілю вчителя."""

    class Meta:
        model = Teacher
        fields = ['full_name', 'avatar_color', 'avatar_image']
        labels = {
            'full_name': 'ПІБ вчителя',
            'avatar_color': 'Колір фону аватара',
            'avatar_image': 'Фото аватара',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Шевченко Тарас Григорович',
            }),
            'avatar_color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-color-input',
            }),
            'avatar_image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
                'id': 'avatar-file-input',
            }),
        }


# ─── Форми створення Предметів та Класів ────────────────────────────────────────
class SubjectForm(forms.ModelForm):
    """Форма створення новий предмету."""

    class Meta:
        model = Subject
        fields = ['name', 'icon', 'color']
        labels = {
            'name': 'Назва предмету',
            'icon': 'Іконка (емодзі)',
            'color': 'Колір (HEX)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Наприклад: Астрономія'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '🌌'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color-input'}),
        }


class ClassGroupForm(forms.ModelForm):
    """Форма створення нового класу."""

    class Meta:
        model = ClassGroup
        fields = ['name', 'grade', 'letter']
        labels = {
            'name': 'Назва класу',
            'grade': 'Паралель (номер)',
            'letter': 'Літера',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Наприклад: 9А'}),
            'grade': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '9'}),
            'letter': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'А'}),
        }


# ─── Форми супер-адміністратора ───────────────────────────────────────────────
class TeacherCreateForm(forms.Form):
    """Форма створення нового облікового запису вчителя (для Супер-Адміна)."""

    username = forms.CharField(
        label='Логін вчителя',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'teacher_ivanov'})
    )
    password = forms.CharField(
        label='Початковий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'})
    )
    full_name = forms.CharField(
        label='ПІБ вчителя',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Іванов Іван Іванович'})
    )
    is_superuser = forms.BooleanField(
        label='Надати права Супер-Адміністратора',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Користувач з таким логіном вже існує.')
        return username


class PasswordResetForm(forms.Form):
    """Форма скидання пароля вчителя."""

    user_id = forms.IntegerField(widget=forms.HiddenInput())
    new_password = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Введіть новий пароль'})
    )




# ─── Форма завдання ────────────────────────────────────────────────────────────
class AssignmentForm(forms.ModelForm):
    """
    Форма створення та редагування завдання.

    Валідація: обов'язкова наявність хоча б одного з:
        - опис (description)
        - файл (файли додаються через AssignmentFileFormSet)
        - посилання (link_url)
    """

    # Поле для вибору типу публікації (замінює поле status напряму)
    PUBLISH_CHOICE_NOW = 'now'
    PUBLISH_CHOICE_SCHEDULED = 'scheduled'
    PUBLISH_CHOICE_DRAFT = 'draft'

    PUBLISH_CHOICES = [
        (PUBLISH_CHOICE_NOW, '✅ Опублікувати зараз'),
        (PUBLISH_CHOICE_SCHEDULED, '⏰ Відкласти публікацію'),
        (PUBLISH_CHOICE_DRAFT, '📝 Зберегти як чернетку'),
    ]

    publish_choice = forms.ChoiceField(
        choices=PUBLISH_CHOICES,
        initial=PUBLISH_CHOICE_NOW,
        label='Публікація',
        widget=forms.RadioSelect(attrs={'class': 'publish-radio'}),
    )

    scheduled_at = forms.DateTimeField(
        required=False,
        label='Дата та час публікації',
        input_formats=['%Y-%m-%dT%H:%M', '%d.%m.%Y %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-input',
            },
            format='%Y-%m-%dT%H:%M'
        )
    )

    due_date = forms.DateField(
        required=False,
        label='Термін виконання',
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-input',
            },
            format='%Y-%m-%d'
        )
    )

    # Файли завантажуються через MultipleFileField (підтримує кілька файлів)
    files = MultipleFileField(
        required=False,
        label='Прикріпити файли',
    )


    class Meta:
        model = Assignment
        fields = [
            'subject', 'title', 'description',
            'classes', 'is_individual', 'student_name',
            'link_url', 'link_label', 'youtube_url',
            'due_date', 'scheduled_at',
        ]
        labels = {
            'subject': 'Предмет',
            'title': 'Тема / Заголовок',
            'description': 'Опис завдання',
            'classes': 'Призначити класам',
            'is_individual': 'Індивідуальне завдання (для конкретного учня / учениці)',
            'student_name': "Прізвище та ім'я учня / учениці",
            'link_url': 'Посилання (URL)',
            'link_label': 'Текст посилання',
            'youtube_url': 'Посилання на YouTube',
        }
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Наприклад: Параграф 12, вправа 5',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 5,
                'placeholder': 'Детальний опис завдання, умова задачі...',
            }),
            'classes': forms.CheckboxSelectMultiple(attrs={'class': 'class-checkbox-group'}),
            'is_individual': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
                'id': 'id_is_individual',
            }),
            'student_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': "Прізвище та ім'я учня або учениці",
            }),
            'link_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://...',
            }),
            'link_label': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Відкрити підручник, Переглянути відео...',
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://www.youtube.com/watch?v=... або https://youtu.be/...',
            }),
        }

    def __init__(self, teacher=None, *args, **kwargs):
        """Ініціалізація: відображає класи та предмети даного вчителя (або всі, якщо не вказані)."""
        super().__init__(*args, **kwargs)

        if teacher:
            if teacher.subjects.exists():
                self.fields['subject'].queryset = teacher.subjects.all()
            else:
                self.fields['subject'].queryset = Subject.objects.all()

            if teacher.classes.exists():
                self.fields['classes'].queryset = teacher.classes.all().order_by('grade', 'letter')
            else:
                self.fields['classes'].queryset = ClassGroup.objects.all().order_by('grade', 'letter')

            default_subject = teacher.get_default_subject()
            if default_subject and not self.initial.get('subject'):
                self.initial['subject'] = default_subject.pk
        else:
            self.fields['subject'].queryset = Subject.objects.all()
            self.fields['classes'].queryset = ClassGroup.objects.all().order_by('grade', 'letter')



        # Заповнення publish_choice з існуючого об'єкта (при редагуванні)
        if self.instance and self.instance.pk:
            if self.instance.status == Assignment.STATUS_DRAFT:
                self.initial['publish_choice'] = self.PUBLISH_CHOICE_DRAFT
            elif self.instance.status == Assignment.STATUS_SCHEDULED:
                self.initial['publish_choice'] = self.PUBLISH_CHOICE_SCHEDULED
            else:
                self.initial['publish_choice'] = self.PUBLISH_CHOICE_NOW

    def clean(self):
        """Валідація: перевіряємо наявність хоча б одного вмісту."""
        cleaned_data = super().clean()
        description = cleaned_data.get('description', '').strip()
        link_url = cleaned_data.get('link_url', '').strip()
        files_uploaded = cleaned_data.get('files', [])

        # Перевіряємо що є хоча б щось
        if not description and not link_url and not files_uploaded:

            raise ValidationError(
                'Додайте хоча б одне з: опис завдання, посилання або файл.'
            )

        # Валідація відкладеної публікації
        publish_choice = cleaned_data.get('publish_choice')
        scheduled_at = cleaned_data.get('scheduled_at')

        if publish_choice == self.PUBLISH_CHOICE_SCHEDULED and not scheduled_at:
            self.add_error(
                'scheduled_at',
                'Вкажіть дату та час відкладеної публікації.'
            )

        # Валідація адресації (Кому призначено: обов'язково клас або індивідуально)
        is_individual = cleaned_data.get('is_individual')
        student_name = cleaned_data.get('student_name', '').strip()
        classes = cleaned_data.get('classes')

        if is_individual:
            if not student_name:
                self.add_error(
                    'student_name',
                    "Обов'язково вкажіть прізвище та ім'я учня або учениці для індивідуального завдання."
                )
        else:
            if not classes or classes.count() == 0:
                self.add_error(
                    'classes',
                    'Обовʼязково оберіть хоча б один клас або позначте як індивідуальне завдання.'
                )

        return cleaned_data

    def save_with_status(self, teacher, commit=True):
        """Зберігає завдання з правильним статусом на основі publish_choice."""
        instance = super().save(commit=False)
        instance.teacher = teacher

        publish_choice = self.cleaned_data.get('publish_choice')

        if publish_choice == self.PUBLISH_CHOICE_DRAFT:
            instance.status = Assignment.STATUS_DRAFT
        elif publish_choice == self.PUBLISH_CHOICE_SCHEDULED:
            instance.status = Assignment.STATUS_SCHEDULED
            instance.scheduled_at = self.cleaned_data.get('scheduled_at')
        else:
            instance.status = Assignment.STATUS_PUBLISHED

        if commit:
            instance.save()
            self.save_m2m()

        return instance
