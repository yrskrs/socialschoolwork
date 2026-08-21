"""
Моделі Django для шкільної мікро-соціальної мережі SchoolNet.

Структура:
    - Subject      — навчальний предмет
    - ClassGroup   — клас (наприклад: 9А, 10Б)
    - Teacher      — профіль вчителя (пов'язаний з Django User)
    - Assignment   — навчальне завдання з файлами, статусами, фільтрами
    - AssignmentFile — прикріплені файли до завдання
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ─── Предмет ──────────────────────────────────────────────────────────────────
class Subject(models.Model):
    """Навчальний предмет (Математика, Фізика тощо)."""
    name = models.CharField('Назва предмету', max_length=100, unique=True)
    icon = models.CharField(
        'Емодзі-іконка',
        max_length=10,
        default='📚',
        help_text='Емодзі для відображення поруч із назвою'
    )
    color = models.CharField(
        'Колір (HEX)',
        max_length=7,
        default='#6366f1',
        help_text='Колір мітки предмету, наприклад #6366f1'
    )
    created_by = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_subjects',
        verbose_name='Створено вчителем'
    )

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предмети'
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"


# ─── Клас ─────────────────────────────────────────────────────────────────────
class ClassGroup(models.Model):
    """Клас або група учнів (наприклад: 9А, 10Б, 11В)."""
    name = models.CharField('Назва класу', max_length=20, unique=True)
    grade = models.PositiveSmallIntegerField('Паралель (цифра)', default=9)
    letter = models.CharField('Літера класу', max_length=3, default='А')
    created_by = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_classes',
        verbose_name='Створено вчителем'
    )

    class Meta:
        verbose_name = 'Клас'
        verbose_name_plural = 'Класи'
        ordering = ['grade', 'letter']

    def __str__(self):
        return self.name



# ─── Профіль вчителя ──────────────────────────────────────────────────────────
class Teacher(models.Model):
    """Профіль вчителя, прив'язаний до облікового запису Django."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name='Обліковий запис'
    )
    full_name = models.CharField('ПІБ вчителя', max_length=200)
    subjects = models.ManyToManyField(
        Subject,
        verbose_name='Предмети',
        blank=True
    )
    classes = models.ManyToManyField(
        ClassGroup,
        verbose_name='Класи',
        blank=True
    )
    avatar_color = models.CharField(
        'Колір аватара',
        max_length=7,
        default='#6366f1'
    )
    avatar_image = models.ImageField(
        'Фото аватара',
        upload_to='teacher_avatars/',
        null=True,
        blank=True,
        help_text='Завантажте квадратне фото або зображення для аватара'
    )

    class Meta:
        verbose_name = 'Вчитель'
        verbose_name_plural = 'Вчителі'

    def __str__(self):
        return self.full_name

    def get_initials(self):
        """Повертає ініціали для відображення в аватарі."""
        parts = self.full_name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.full_name[:2].upper()

    def get_default_subject(self):
        """Повертає предмет, якщо він один — для автопідстановки."""
        subjects = self.subjects.all()
        if subjects.count() == 1:
            return subjects.first()
        return None


# ─── Завдання ─────────────────────────────────────────────────────────────────
class Assignment(models.Model):
    """
    Навчальне завдання з підтримкою:
    - кількох статусів (чернетка / відкладена публікація / опубліковано)
    - індивідуальних завдань для конкретного учня
    - прикріплення файлів та посилань
    """

    # Статуси завдання
    STATUS_PUBLISHED = 'published'
    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_PUBLISHED, '✅ Опубліковано'),
        (STATUS_DRAFT, '📝 Чернетка'),
        (STATUS_SCHEDULED, '⏰ Відкладена публікація'),
        (STATUS_ARCHIVED, '📦 Архів'),
    ]

    # ── Основні поля ─────────────────────────────────────────────────────────
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Вчитель'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Предмет'
    )
    title = models.CharField('Тема завдання', max_length=300)
    description = models.TextField('Опис / умова завдання', blank=True)

    # ── Адресація (клас або індивідуально) ──────────────────────────────────
    classes = models.ManyToManyField(
        ClassGroup,
        blank=True,
        verbose_name='Призначено класам'
    )
    is_individual = models.BooleanField(
        'Індивідуальне завдання',
        default=False,
        help_text='Якщо True — завдання для конкретного учня'
    )
    student_name = models.CharField(
        "Ім'я учня",
        max_length=200,
        blank=True,
        help_text="Повне ім'я учня для індивідуального завдання"
    )

    # ── Посилання (опціонально) ───────────────────────────────────────────────
    link_url = models.URLField(
        'Посилання',
        blank=True,
        help_text='Зовнішнє або внутрішнє посилання на матеріал'
    )
    link_label = models.CharField(
        'Підпис посилання',
        max_length=200,
        blank=True,
        help_text='Текст кнопки/посилання (якщо порожньо — URL)'
    )
    youtube_url = models.URLField(
        'Посилання на YouTube відео',
        blank=True,
        help_text='Відео буде вбудовано безпосередньо на сторінці завдання'
    )

    # ── Статус та публікація ───────────────────────────────────────────────────
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    scheduled_at = models.DateTimeField(
        'Час відкладеної публікації',
        null=True,
        blank=True
    )
    due_date = models.DateField(
        'Термін виконання',
        null=True,
        blank=True
    )

    # ── Метадані ──────────────────────────────────────────────────────────────
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)
    published_at = models.DateTimeField('Опубліковано', null=True, blank=True)
    unarchived_at = models.DateTimeField('Час розархівації', null=True, blank=True)
    views_count = models.PositiveIntegerField('Кількість переглядів', default=0)

    # ── Зв'язок з оригіналом (для дублювання) ────────────────────────────────
    duplicated_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates',
        verbose_name='Дубліковано з'
    )

    class Meta:
        verbose_name = 'Завдання'
        verbose_name_plural = 'Завдання'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"

    def is_visible(self):
        """Чи видиме завдання для учнів (опубліковане або час настав)."""
        if self.status == self.STATUS_PUBLISHED:
            return True
        if self.status == self.STATUS_SCHEDULED and self.scheduled_at:
            return timezone.now() >= self.scheduled_at
        return False

    @property
    def youtube_video_id(self):
        """Витягує 11-значний ID відео YouTube з будь-якого формату посилання."""
        if not self.youtube_url:
            return ""
        import re
        patterns = [
            r'(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|shorts\/|live\/|watch\?(?:.*&)?v=))([\w-]{11})',
            r'youtube\.com\/[^\/]+\/.*[?&]v=([\w-]{11})',
        ]
        for p in patterns:
            m = re.search(p, self.youtube_url)
            if m:
                return m.group(1)
        return ""

    @property
    def youtube_embed_url(self):
        """Конвертує посилання на YouTube у захищений формат для вбудовування (youtube-nocookie)."""
        vid = self.youtube_video_id
        if vid:
            return f"https://www.youtube-nocookie.com/embed/{vid}?rel=0"
        return ""

    @property
    def youtube_watch_url(self):
        """Пряме посилання на YouTube для відкриття у новій вкладці (якщо автор обмежив вбудовування)."""
        vid = self.youtube_video_id
        if vid:
            return f"https://www.youtube.com/watch?v={vid}"
        return self.youtube_url or ""

    @property
    def all_youtube_videos(self):
        """Повертає список усіх відео YouTube до завдання (основне + додаткові)."""
        videos = []
        if self.youtube_url and self.youtube_embed_url:
            videos.append({
                'title': 'YouTube відео',
                'embed_url': self.youtube_embed_url,
                'watch_url': self.youtube_watch_url or self.youtube_url,
            })
        for ylink in self.youtube_links.all():
            if ylink.embed_url:
                videos.append({
                    'title': ylink.title or f"Відео {len(videos) + 1}",
                    'embed_url': ylink.embed_url,
                    'watch_url': ylink.watch_url or ylink.url,
                })
        return videos

    @property
    def days_ago(self):
        """Кількість днів з моменту публікації завдання."""
        if not self.published_at:
            return 0
        from django.utils import timezone
        pub_date = timezone.localtime(self.published_at).date()
        today = timezone.localtime(timezone.now()).date()
        delta = (today - pub_date).days
        return max(0, delta)

    @property
    def age_card_class(self):
        """CSS-клас візуального затемнення / старіння картки завдання."""
        days = self.days_ago
        if days == 0:
            return "card-age-today"
        elif days == 1:
            return "card-age-yesterday"
        elif days == 2:
            return "card-age-2days"
        elif days == 3:
            return "card-age-3days"
        else:
            return "card-age-older"

    @property
    def relative_published_display(self):
        """
        Форматування дати публікації відповідно до вимог:
        - Сьогодні -> "Сьогодні, 21.08"
        - Вчора -> "Вчора, 20.08"
        - Раніше -> День тижня + дата, наприклад "Понеділок, 17.08"
        """
        if not self.published_at:
            return ""
        from django.utils import timezone
        local_dt = timezone.localtime(self.published_at)
        pub_date = local_dt.date()
        today = timezone.localtime(timezone.now()).date()
        delta = (today - pub_date).days

        day_month = local_dt.strftime('%d.%m')

        uk_weekdays = {
            0: 'Понеділок',
            1: 'Вівторок',
            2: 'Середа',
            3: 'Четвер',
            4: 'Пʼятниця',
            5: 'Субота',
            6: 'Неділя',
        }

        if delta == 0:
            return f"Сьогодні, {day_month}"
        elif delta == 1:
            return f"Вчора, {day_month}"
        else:
            weekday = uk_weekdays.get(pub_date.weekday(), '')
            return f"{weekday}, {day_month}"

    @property
    def is_published_today(self):
        """Чи опубліковано сьогодні."""
        return self.days_ago == 0

    @property
    def is_published_yesterday(self):
        """Чи опубліковано вчора."""
        return self.days_ago == 1

    @property
    def unarchived_display(self):
        """Форматований підпис розархівації."""
        if not self.unarchived_at:
            return ""
        from django.utils import timezone
        local_dt = timezone.localtime(self.unarchived_at)
        return f"Розархівовано {local_dt.strftime('%d.%m')}"

    @property
    def student_display(self):
        """
        Генерує коректне та ввічливе звернення з урахуванням роду:
        - "Для учениці: Марія Коваль"
        - "Для учня: Тарас Шевченко"
        - "Для учня / учениці: ..." (якщо не визначено однозначно)
        """
        if not self.student_name:
            return ""

        name = self.student_name.strip()
        parts = [p.lower().strip(',.!') for p in name.split()]

        female_names = {
            'анна', 'ганна', 'марія', 'марічка', 'софія', 'дарина', 'дарʼя', 'дарья', 'дарія', 'даша',
            'єва', 'вікторія', 'віка', 'поліна', 'анастасія', 'настя', 'мілана', 'соломія', 'соломійка',
            'вероніка', 'злата', 'ярина', 'олена', 'катерина', 'катя', 'ірина', 'іра', 'оксана',
            'тетяна', 'таня', 'юлія', 'юля', 'наталія', 'наталя', 'наташа', 'ольга', 'оля', 'світлана',
            'надія', 'любов', 'діана', 'аліна', 'христина', 'марʼяна', 'маряна', 'інна', 'владислава',
            'валерія', 'олександра', 'саша', 'євгенія', 'богдана', 'ярослава', 'мирослава', 'лілія',
            'ліля', 'маргарита', 'евеліна', 'альона', 'кіра', 'уляна', 'ангеліна', 'каріна', 'владлена',
            'людмила', 'галина', 'віталіна', 'меланія', 'ема', 'емма', 'міла', 'стефанія', 'стефа', 'аліса'
        }

        male_names = {
            'олександр', 'іван', 'тарас', 'максим', 'богдан', 'дмитро', 'артем', 'матвій', 'тимур',
            'владислав', 'назар', 'денис', 'данило', 'марко', 'роман', 'святослав', 'андрій',
            'ярослав', 'михайло', 'євген', 'олег', 'ігор', 'сергій', 'павло', 'василь', 'юрій',
            'вадим', 'володимир', 'віталій', 'микола', 'віктор', 'степан', 'петро', 'антон',
            'ілля', 'гліб', 'кирило', 'костянтин', 'леонід', 'тимофій', 'ростислав', 'лука', 'лев'
        }

        is_female = False
        is_male = False

        for p in parts:
            if p in female_names or p.endswith(('івна', 'ївна', 'ська', 'цька', 'зька', 'ова', 'єва', 'ина', 'іна')):
                is_female = True
            if p in male_names or p.endswith(('ович', 'евич', 'євич', 'ський', 'цький', 'зький', 'ов', 'єв', 'ин', 'ін')):
                is_male = True

        if is_female and not is_male:
            return f"Для учениці: {name}"
        elif is_male and not is_female:
            return f"Для учня: {name}"
        else:
            return f"Для учня / учениці: {name}"

    def record_view(self, request):
        """
        Фіксує перегляд завдання:
        - 1 комп'ютер (IP / сесія) = 1 перегляд на 1 годину.
        - Перегляди вчителів та адміністраторів НЕ враховуються.
        """
        if not request:
            return False

        # Якщо користувач авторизований вчитель або суперкористувач — НЕ рахуємо
        if request.user.is_authenticated:
            if hasattr(request.user, 'teacher_profile') or request.user.is_superuser or request.user.is_staff:
                return False

        # Отримуємо IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Отримуємо ключ сесії безпечно
        session_obj = getattr(request, 'session', None)
        session_key = ''
        if session_obj is not None:
            if hasattr(session_obj, 'session_key'):
                session_key = session_obj.session_key or ''
                if not session_key:
                    try:
                        session_obj.save()
                        session_key = session_obj.session_key or ''
                    except Exception:
                        session_key = ''
            elif isinstance(session_obj, str):
                session_key = session_obj

        from datetime import timedelta
        one_hour_ago = timezone.now() - timedelta(hours=1)

        # Перевіряємо чи був перегляд з цього комп'ютера за останню годину
        device_q = models.Q()
        if ip:
            device_q |= models.Q(ip_address=ip)
        if session_key:
            device_q |= models.Q(session_key=session_key)

        if not device_q:
            return False

        existing_log = AssignmentViewLog.objects.filter(
            models.Q(assignment=self) & device_q & models.Q(viewed_at__gte=one_hour_ago)
        ).first()

        if existing_log:
            return False  # Вже переглядав за останню годину

        # Оновлюємо старий лог або створюємо новий
        log_to_update = AssignmentViewLog.objects.filter(
            models.Q(assignment=self) & device_q
        ).first()

        if log_to_update:
            log_to_update.save()  # auto_now оновлює viewed_at на поточний час
        else:
            AssignmentViewLog.objects.create(
                assignment=self,
                ip_address=ip,
                session_key=session_key or ''
            )

        # Атомарно збільшуємо лічильник переглядів
        Assignment.objects.filter(pk=self.pk).update(views_count=models.F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])
        return True

    def save(self, *args, **kwargs):
        """Автоматично встановлює час публікації та перевіряє відкладені."""
        # Якщо статус змінився на "опубліковано" — фіксуємо час
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        # Якщо відкладений час настав — автоматично публікуємо
        if self.status == self.STATUS_SCHEDULED and self.scheduled_at:
            if timezone.now() >= self.scheduled_at:
                self.status = self.STATUS_PUBLISHED
                self.published_at = self.scheduled_at
        super().save(*args, **kwargs)


class AssignmentViewLog(models.Model):
    """Лог переглядів завдань (1 запис на комп'ютер раз на годину)."""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='view_logs',
        verbose_name='Завдання'
    )
    ip_address = models.GenericIPAddressField('IP адреса', null=True, blank=True)
    session_key = models.CharField('Ключ сесії / пристрою', max_length=64, blank=True)
    viewed_at = models.DateTimeField('Час останнього перегляду', auto_now=True)

    class Meta:
        verbose_name = 'Лог перегляду завдання'
        verbose_name_plural = 'Логи переглядів завдань'
        indexes = [
            models.Index(fields=['assignment', 'ip_address', 'viewed_at']),
            models.Index(fields=['assignment', 'session_key', 'viewed_at']),
        ]

    def __str__(self):
        return f"View of #{self.assignment_id} from {self.ip_address or self.session_key} at {self.viewed_at}"


class AssignmentLink(models.Model):
    """Додаткові посилання до завдання."""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='additional_links',
        verbose_name='Завдання'
    )
    url = models.URLField('Посилання')
    label = models.CharField('Підпис посилання', max_length=200, blank=True)

    def __str__(self):
        return self.label or self.url


class AssignmentYouTubeLink(models.Model):
    """Додаткові YouTube відео до завдання."""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='youtube_links',
        verbose_name='Завдання'
    )
    url = models.URLField('Посилання на YouTube')
    title = models.CharField('Назва / підпис відео', max_length=200, blank=True)

    def __str__(self):
        return self.title or self.url

    @property
    def video_id(self):
        """Витягує 11-значний ID відео YouTube."""
        if not self.url:
            return ""
        import re
        patterns = [
            r'(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|shorts\/|live\/|watch\?(?:.*&)?v=))([\w-]{11})',
            r'youtube\.com\/[^\/]+\/.*[?&]v=([\w-]{11})',
        ]
        for p in patterns:
            m = re.search(p, self.url)
            if m:
                return m.group(1)
        return ""

    @property
    def embed_url(self):
        """Конвертує у формат для вбудовування."""
        vid = self.video_id
        if vid:
            return f"https://www.youtube-nocookie.com/embed/{vid}?rel=0"
        return ""

    @property
    def watch_url(self):
        """Пряме посилання для перегляду на YouTube."""
        vid = self.video_id
        if vid:
            return f"https://www.youtube.com/watch?v={vid}"
        return self.url or ""



# ─── Файли до завдання ────────────────────────────────────────────────────────
def assignment_upload_path(instance, filename):
    """Динамічний шлях для завантаження файлів: media/assignments/<id>/<file>."""
    return f"assignments/{instance.assignment.id}/{filename}"


class AssignmentFile(models.Model):
    """Файл, прикріплений до завдання (зображення, PDF, Word, відео тощо)."""

    # Типи файлів для відображення у браузері
    BROWSER_VIEWABLE_EXTENSIONS = {
        # Зображення
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp',
        # Документи (MS Office, PDF)
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
        # Текст / код
        '.txt', '.md', '.html', '.htm', '.xml', '.csv', '.py', '.js', '.css', '.json', '.sh', '.cpp', '.h', '.c', '.java',
        # Аудіо
        '.mp3', '.wav', '.ogg', '.flac', '.aac',
        # Відео
        '.mp4', '.webm', '.ogv',
    }

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Завдання'
    )
    file = models.FileField(
        'Файл',
        upload_to=assignment_upload_path
    )
    original_name = models.CharField(
        'Оригінальна назва файлу',
        max_length=500,
        blank=True
    )
    uploaded_at = models.DateTimeField('Завантажено', auto_now_add=True)

    class Meta:
        verbose_name = 'Файл завдання'
        verbose_name_plural = 'Файли завдань'
        ordering = ['uploaded_at']

    def __str__(self):
        return self.original_name or self.file.name

    def save(self, *args, **kwargs):
        """Зберігає оригінальну назву файлу."""
        if self.file and not self.original_name:
            self.original_name = self.file.name.split('/')[-1]
        super().save(*args, **kwargs)

    def get_extension(self):
        """Повертає розширення файлу в нижньому регістрі."""
        import os
        _, ext = os.path.splitext(self.original_name or self.file.name)
        return ext.lower()

    def is_browser_viewable(self):
        """Чи можна відкрити файл прямо в браузері."""
        return self.get_extension() in self.BROWSER_VIEWABLE_EXTENSIONS

    def get_file_type(self):
        """Повертає тип файлу для іконки та відображення."""
        ext = self.get_extension()
        if ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}:
            return 'image'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in {'.mp4', '.webm', '.ogv'}:
            return 'video'
        elif ext in {'.mp3', '.wav', '.ogg', '.flac', '.aac'}:
            return 'audio'
        elif ext in {'.doc', '.docx'}:
            return 'word'
        elif ext in {'.xls', '.xlsx'}:
            return 'excel'
        elif ext in {'.ppt', '.pptx'}:
            return 'powerpoint'
        elif ext in {'.zip', '.rar', '.7z', '.tar', '.gz'}:
            return 'archive'
        elif ext in {'.txt', '.md', '.csv', '.html', '.htm', '.xml', '.py', '.js', '.css', '.json', '.sh', '.cpp', '.h', '.c', '.java'}:
            return 'text'
        else:
            return 'file'

    def get_file_icon(self):
        """Повертає емодзі-іконку відповідно до типу файлу."""
        icons = {
            'image': '🖼️',
            'pdf': '📄',
            'video': '🎬',
            'audio': '🎵',
            'word': '📝',
            'excel': '📊',
            'powerpoint': '📑',
            'archive': '🗜️',
            'text': '📃',
            'file': '📎',
        }
        return icons.get(self.get_file_type(), '📎')

    def get_size_display(self):
        """Повертає розмір файлу у зручному форматі."""
        try:
            size = self.file.size
            if size < 1024:
                return f"{size} Б"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} КБ"
            else:
                return f"{size / (1024 * 1024):.1f} МБ"
        except Exception:
            return ''
