import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post
from django.utils.translation import gettext_lazy as _


class LatestPostsFeed(Feed):
    title = _("Demo blog")
    link = reverse_lazy("blog:home")
    description = _("New posts from Demo blog.")

    def items(self):
        return Post.objects.all().filter(article_status=Post.Status.PUBLISHED)[
            :5
        ]

    def item_title(self, item):
        return item.article_title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.article_body), 30)

    def item_pubdate(self, item):
        return item.article_published
