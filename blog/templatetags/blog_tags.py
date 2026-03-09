from django import template
from ..models import Post
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag
def total_posts_amount():
    return Post.objects.filter(article_status=Post.Status.PUBLISHED).count()


@register.inclusion_tag("post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = (
        Post.objects.all()
        .filter(article_status=Post.Status.PUBLISHED)
        .order_by("-article_updated")[:count]
    )
    return {"latest_posts": latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return (
        Post.objects.all()
        .filter(article_status=Post.Status.PUBLISHED)
        .annotate(total_comments=Count("comments"))
        .order_by("-total_comments")[:count]
    )


@register.filter
@stringfilter
def convert_markdown(value):
    md = markdown.markdown(
        value,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
        ],
    )
    return mark_safe(md)
