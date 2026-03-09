from django.contrib import admin
from .models import Post, Comment


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "article_title",
        "article_slug",
        "article_author",
        "article_published",
        "article_updated",
        "article_status",
    ]
    list_filter = ["article_status", "article_published", "article_author"]
    search_fields = ["article_title", "article_body"]
    prepopulated_fields = {"article_slug": ("article_title",)}
    show_facets = admin.ShowFacets.ALWAYS
    inlines = [
        CommentInline,
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "user_name",
        "user_email",
        "related_post",
        "comment_created",
        "is_active",
    ]
    list_filter = ["is_active", "comment_created", "comment_updated"]
    search_fields = ["user_name", "user_email", "comment_body"]
    show_facets = admin.ShowFacets.ALWAYS
