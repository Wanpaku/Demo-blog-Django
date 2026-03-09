from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from faker import Faker
from ..models import Post, Comment


class CommentFormTest(TestCase):
    """Class for testing a comment form and view."""

    @classmethod
    def setUpTestData(cls):
        cls.fake_gen = Faker()
        cls.user = User.objects.create_user(
            username="testuser",
            password="password",
            email=cls.fake_gen.unique.email(),
        )
        title = cls.fake_gen.unique.sentence(nb_words=5, variable_nb_words=True)
        cls.post = Post.objects.create(
            article_title=title,
            article_slug=cls.fake_gen.slug(value=title),
            article_body=cls.fake_gen.text(),
            article_author=cls.user,
            article_status=Post.Status.PUBLISHED,
        )
        cls.post_detail_url = reverse(
            "blog:post_detail",
            args=[
                cls.post.article_slug,
                cls.post.article_published.year,
                cls.post.article_published.month,
                cls.post.article_published.day,
            ],
        )

    def test_comment_with_login(self):
        self.client.login(username="testuser", password="password")
        comment_body = self.fake_gen.text()
        response = self.client.post(
            self.post_detail_url, data={"comment_body": comment_body}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(Comment.objects.last().user_name, "testuser")
        self.assertEqual(Comment.objects.last().comment_body, comment_body)
        self.assertTrue(Comment.objects.last().is_active)

    def test_comment_without_login(self):
        self.client.logout()
        comment_body = self.fake_gen.text()
        response = self.client.post(
            self.post_detail_url, data={"comment_body": comment_body}
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(Comment.objects.all()), 0)

    def test_comment_with_wrong_submit(self):
        self.client.login(username="testuser", password="password")
        # Test invalid data submission
        response = self.client.post(self.post_detail_url, data={})

        # No redirection and total amount of comments didn't changed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Comment.objects.all()), 0)

        # Comment with too much letters. Current limit is 500
        comment_body = self.fake_gen.text(1000)
        response = self.client.post(
            self.post_detail_url, data={"comment_body": comment_body}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Comment.objects.all()), 0)
