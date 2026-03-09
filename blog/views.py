from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    View,
)
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import reverse
from django.http import HttpResponseForbidden
from .models import Post
from .forms import CommentForm
from taggit.models import Tag
from django.db.models import Count

# Create your views here.


class PostListView(ListView):
    """Class for creating posts list view."""

    model = Post
    context_object_name = "posts_list"
    template_name = "post/list.html"
    paginate_by = 5
    tag = None

    def get_queryset(self):
        tag_slug = self.kwargs.get("tag_slug", None)
        published_articles = Post.objects.filter(
            article_status=Post.Status.PUBLISHED
        )
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            tagged_articles = published_articles.filter(tags__in=[self.tag])
            return tagged_articles

        return published_articles

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.tag:
            context["tag"] = self.tag
        return context


class PostDetailDisplayView(DetailView):
    """Class for displaying detailed post view with comment form."""

    model = Post
    context_object_name = "post_detail"
    template_name = "post/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur_post = self.get_object()
        active_comments = cur_post.comments.filter(is_active=True)
        context["active_comments"] = active_comments
        context["form"] = CommentForm()
        post_tags_ids = cur_post.tags.values_list("id", flat=True)
        published_articles = Post.objects.filter(
            article_status=Post.Status.PUBLISHED
        )

        similar_posts = published_articles.filter(
            tags__in=post_tags_ids
        ).exclude(id=cur_post.id)
        similar_posts = similar_posts.annotate(
            same_tags=Count("tags")
        ).order_by("-same_tags", "-article_published")[:5]
        context["similar_posts"] = similar_posts
        return context

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        day = self.kwargs.get("day")
        return get_object_or_404(
            Post,
            article_status=Post.Status.PUBLISHED,
            article_slug=slug,
            article_published__year=year,
            article_published__month=month,
            article_published__day=day,
        )


class PostComment(SingleObjectMixin, FormView):
    """Class for postin comment through the form."""

    template_name = "post/detail.html"
    form_class = CommentForm
    model = Post
    slug_field = "article_slug"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        # Get commented Post object
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Get valid comment
        comment = form.save(commit=False)
        # Connect the comment to the related post
        comment.related_post = self.object
        # Save current authenticated user and email to the comment
        comment.user_name = self.request.user
        comment.user_email = self.request.user.email
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={
                "slug": self.object.article_slug,
                "year": self.object.article_published.year,
                "month": self.object.article_published.month,
                "day": self.object.article_published.day,
            },
        )


class PostDetailView(View):
    """Class for combining displaying and posting a comment in a single view."""

    def get(self, request, *args, **kwargs):
        view = PostDetailDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostComment.as_view()
        return view(request, *args, **kwargs)
