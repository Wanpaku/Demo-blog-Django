from django.urls import path
from .views import PostListView, PostDetailView
from django.views.generic import TemplateView
from .feeds import LatestPostsFeed

app_name = "blog"
urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path(
        "tag/<slug:tag_slug>/", PostListView.as_view(), name="post_list_by_tag"
    ),
    path(
        "<slug:slug>/<int:year>/<int:month>/<int:day>/",
        PostDetailView.as_view(),
        name="post_detail",
    ),
    path(
        "about/",
        TemplateView.as_view(template_name="partials/about.html"),
        name="about",
    ),
    path(
        "contacts/",
        TemplateView.as_view(template_name="partials/contacts.html"),
        name="contacts",
    ),
    path("feed/", LatestPostsFeed(), name="post_feed"),
]
