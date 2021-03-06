from django.conf import settings
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey    
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.core.exceptions import ValidationError

from taggit.managers import TaggableManager

from astorcore.decorators import register_page
from astorcore.utils import clone_page, user_directory_path, get_client_ip


class Page(models.Model):
    verbose_name = "page"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="pages"
    )

    content_type = models.ForeignKey(
        ContentType, related_name="pages", null=True,
        on_delete=models.SET_NULL
    )

    created_date = models.DateTimeField(default=timezone.now)
    first_published_date = models.DateTimeField(
        null=True, editable=False, db_index=True
    )
    published_page = models.OneToOneField(
        "self", related_name="base_page",
        blank=True, null=True,
        on_delete=models.SET_NULL
    )

    tags = TaggableManager(blank=True)

    # Distinction between drafts and published pages
    editable = models.BooleanField(default=True, editable=False)
    live = models.BooleanField(default=False, editable=False)


    has_unpublished_changes = models.BooleanField(
        default=False,
        editable=False
    )
    latest_changes_date = models.DateTimeField(
        null=True,
        editable=False
    )

    comments_on = models.BooleanField(default=True)


    def __init__(self, *args, **kwargs):
        # Set content type only once
        super(Page, self).__init__(*args, **kwargs)
        if not self.id and not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self)

    @property
    def specific(self):
        '''Casts Page to specific type stored in content_type.''' 
        content_type = ContentType.objects.get_for_id(self.content_type_id)
        model_class = content_type.model_class()
        if model_class is None or isinstance(self, model_class):
            return self
        return content_type.get_object_for_this_type(id=self.id)

    def get_absolute_url(self):
        '''Returns url to specific page.'''
        if not self.user:
            raise NoReverseMatch("Undefined owner of the page.")
        return reverse("astormain:page", 
                       kwargs={"slug": self.user.slug, "pk": self.pk})  

    def register_visit(self, request=None, user=None):
        '''Register page visit.'''
        return PageVisit.create(self, request, user)

    def __repr__(self):
        return "{!r} ({:d})".format(self.specific.__class__.__name__, self.pk)

    def save(self, *args, **kwargs):
        '''Saves the page. Sets unpublished changes to True.'''
        self.has_unpublished_changes = True
        self.latest_changes_date = timezone.now()
        super(Page, self).save(*args, **kwargs)

    '''Add more informative name for save.'''
    save_draft = save

    def publish(self):
        '''Publish the page.'''
        if not self.published_page:
            self.first_published_date = timezone.now()
        else:
            self.published_page.delete()
            self.published_page = None

        pub_page = clone_page(self)
        pub_page.live = True
        pub_page.editable = False
        pub_page.save()

        self.published_page = pub_page
        self.has_unpublished_changes = False
        self.save()

        return pub_page

    def unpublish(self):
        '''Unpublish the page.'''
        if self.published_page:
            self.published_page.delete()
            self.published_page = None
            self.save()

    def add_comment(self, comment=None, **kwargs):
        '''Add comment to the page.'''
        if comment:
            if not isinstance(comment, Comment):
                raise TypeError("comment must be a Commend type")
            if not comment.pk:
                comment.save()
        else:
            comment = Comment(**kwargs)
            comment.save()

        self.comments.add(comment)

        return comment


class PageVisit(models.Model):
    '''Register who and when visit a page.'''
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, 
        related_name="visits"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="+")

    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    request_method = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        unique_together = ("page", "ip_address")

    @classmethod
    def create(cls, page, request=None, user=None):
        '''Create PageVisit object.'''
        http_headers = getattr(request, "META", dict())
        visit = cls(
            page = page,
            user = user or (
                getattr(request, "user", None) 
                and (request.user.is_authenticated() or None) 
                and request.user
            ),
            ip_address = get_client_ip(request),
            user_agent = http_headers.get("HTTP_USER_AGENT"),
            request_method = http_headers.get("REQUEST_METHOD")
        )

        try:
            visit.full_clean()
        except ValidationError:
            return None
        else:
            visit.save()
            return visit


class Comment(models.Model):
    verbose_name = "comment"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="comments"           
    )
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, blank=True, null=True,
        related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True,
        related_name="replies"
    )

    body = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def reply(self, comment=None, **kwargs):
        '''Reply to the commend.'''
        if comment:
            if not isinstance(comment, Comment):
                raise TypeError("comment must be a Commend type")
            if not comment.pk:
                comment.save()
        else:
            comment = Comment(**kwargs)
            comment.save()

        self.replies.add(comment)

        return comment


class BasePage(Page):
    '''BasePage for creating other pages.'''
    verbose_name = "basepage"

    class Meta:
        abstract=True

    title = models.CharField(max_length=255)
    abstract = models.TextField(default="", blank=True) 
    img_url = models.CharField(max_length=1024, blank=True)


@register_page
class ContentPage(BasePage):
    verbose_name = "content page"
    template_name = "astormain/pages/content.html"
    help_text = "Provide some content and I will be happy."

    body = models.TextField(blank=True)


class AbstractUploadPage(BasePage):
    verbose_name = "base file page"

    class Meta:
        abstract = True

    file = models.FileField(upload_to=user_directory_path)


@register_page
class HTMLUploadPage(AbstractUploadPage):
    verbose_name = "HTML upload page"
    help_text = "Upload HTML file and I will render it for you."
    template_name = "astormain/pages/html_file.html"