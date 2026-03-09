from faker import Faker
from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User
from datetime import datetime
from ..models import Post


class PostListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        articles_amount = 8
        fake_gen = Faker()
        for _ in range(articles_amount):
            cls.user = User.objects.create_user(
                username=fake_gen.unique.first_name(),
                password=fake_gen.last_name(),
            )
            title = fake_gen.unique.sentence(nb_words=5, variable_nb_words=True)
            cls.post = Post.objects.create(
                article_title=title,
                article_slug=fake_gen.slug(value=title),
                article_body=fake_gen.text(),
                article_author=cls.user,
                article_status=Post.Status.PUBLISHED,
            )

    def test_home_url(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_name_url_and_template(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "post/list.html")

    def test_pagination_is_five(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["posts_list"]), 5)

    def test_posts_at_separate_page(self):
        response = self.client.get(reverse("blog:home") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["posts_list"]), 3)


class PostDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.slug = "who-is-deborah-harry"
        cls.year, cls.month, cls.day = (
            datetime.now().year,
            datetime.now().month,
            datetime.now().day,
        )

        cls.user = User.objects.create_user(
            username="testuser", password="password"
        )
        cls.post = Post.objects.create(
            article_title="Who is Deborah Harry?",
            article_slug="who-is-deborah-harry",
            article_body="Deborah Harry is Blondie.",
            article_author=cls.user,
            article_status=Post.Status.PUBLISHED,
        )

    def test_post_detail_url(self):
        url = f"/{self.slug}/{self.year}/{self.month}/{self.day}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_url_name_and_template(self):
        url = reverse(
            "blog:post_detail",
            args=[
                self.post.article_slug,
                self.post.article_published.year,
                self.post.article_published.month,
                self.post.article_published.day,
            ],
        )
        self.assertEqual(
            url, f"/{self.slug}/{self.year}/{self.month}/{self.day}/"
        )
        response = self.client.get(url)
        # Test post with the Published status.
        self.assertEqual(response.status_code, 200)

        # Test post with the Draft status. Must not be found
        # because only posts with the Published status are allowed to display.
        self.post.article_status = Post.Status.DRAFT
        self.post.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
