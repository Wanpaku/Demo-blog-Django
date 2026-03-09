from django.db import models
from django.db.models.query import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse
from taggit.managers import TaggableManager
from html_sanitizer.django import get_sanitizer


class Post(models.Model):
    """Class for creating a post record in the database."""

    class Status(models.TextChoices):
        """Class for an article statuses enum."""

        DRAFT = "DF", _("draft")
        PUBLISHED = "PB", _("published")

    article_title = models.CharField(
        max_length=100, verbose_name=_("article title")
    )
    article_slug = models.SlugField(
        max_length=100,
        verbose_name=_("article slug"),
        unique_for_date="article_published",
    )
    article_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("article author"),
        related_name="blog_posts",
    )
    article_body = models.TextField(verbose_name=_("article body"))
    article_published = models.DateTimeField(
        default=timezone.now, verbose_name=_("article published")
    )
    article_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("article created")
    )
    article_updated = models.DateTimeField(
        auto_now=True, verbose_name=_("article updated")
    )
    article_status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
        verbose_name=_("article status"),
    )

    tags = TaggableManager()

    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ["-article_published"]
        indexes = [models.Index(fields=["-article_published"])]

    def __str__(self):
        return str(self.article_title)

    def get_absolute_url(self):
        return reverse(
            viewname="blog:post_detail",
            args=[
                self.article_slug,
                self.article_published.year,
                self.article_published.month,
                self.article_published.day,
            ],
        )

    def save(
        self,
        *,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        # Mandatory sanitizing post body because of enabled markdown support
        sanitizer = get_sanitizer(name="custom")
        self.article_body = sanitizer.sanitize(self.article_body)

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class Comment(models.Model):
    """Class for creating a comment in th database."""

    related_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("related post"),
    )
    user_name = models.CharField(max_length=80, verbose_name=_("user name"))
    user_email = models.EmailField(verbose_name=_("user email"))
    comment_body = models.TextField(
        max_length=500, verbose_name=_("comment body")
    )
    comment_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("comment created")
    )
    comment_updated = models.DateTimeField(
        auto_now=True, verbose_name=_("comment updated")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ["comment_created"]
        indexes = [
            models.Index(fields=["comment_created"]),
        ]

    def __str__(self):
        return str(
            _("Comment by {} on {}".format(self.user_name, self.related_post))
        )

    def save(
        self,
        *,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        # Mandatory sanitizing comment body because of enabled markdown support
        sanitizer = get_sanitizer(name="custom")
        self.comment_body = sanitizer.sanitize(self.comment_body)
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
