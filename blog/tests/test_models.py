from django.test import TestCase
from ..models import Post, Comment
from django.contrib.auth.models import User
from datetime import datetime
from faker import Faker
from django.shortcuts import reverse


# Create your tests here.
class PostTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="password"
        )
        cls.post = Post.objects.create(
            article_title="Who is Deborah Harry?",
            article_slug="who-is-deborah-harry",
            article_body="Deborah Harry is Blondie.",
            article_author=cls.user,
        )
        cls.post_field_names = [
            "article_title",
            "article_slug",
            "article_body",
            "article_author",
            "article_created",
            "article_published",
            "article_updated",
            "article_status",
        ]

    def test_post_content(self):
        self.assertEqual(self.post.article_title, "Who is Deborah Harry?")
        self.assertEqual(self.post.article_slug, "who-is-deborah-harry")
        self.assertEqual(self.post.article_body, "Deborah Harry is Blondie.")
        self.assertEqual(self.post.article_status, self.post.Status.DRAFT)

    def test_attr_names(self):
        post_name = self.post._meta.verbose_name
        self.assertEqual(post_name, "post")

        post_name_plural = self.post._meta.verbose_name_plural
        self.assertEqual(post_name_plural, "posts")

        for field_name in self.post_field_names:
            verbose_name = field_name.replace("_", " ")
            self.assertEqual(
                self.post._meta.get_field(field_name).verbose_name, verbose_name
            )

    def test_attr_max_length(self):
        title_max_length = self.post._meta.get_field("article_title").max_length
        self.assertEqual(title_max_length, 100)

        slug_max_length = self.post._meta.get_field("article_slug").max_length
        self.assertEqual(slug_max_length, 100)

    def test_dunder_str(self):
        self.assertEqual(str(self.post), "Who is Deborah Harry?")

    def test_get_absolute_url(self):
        slug = "who-is-deborah-harry"
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day
        url = self.post.get_absolute_url()
        self.assertEqual(url, f"/{slug}/{year}/{month}/{day}/")

    def test_article_body_markdown_security(self):
        unsafe_post = Post.objects.create(
            article_title="Evil script!",
            article_slug="evil-script",
            article_body="Some text. <script scr='evil.com'></script> More text",
            article_author=self.user,
        )
        assert (
            "<script scr='evil.com'></script>" not in unsafe_post.article_body
        )
        assert "text" in unsafe_post.article_body


class CommentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fake_gen = Faker()
        user = User.objects.create_user(
            username=fake_gen.unique.first_name(), password=fake_gen.password()
        )
        title = fake_gen.unique.sentence(nb_words=5, variable_nb_words=True)
        cls.post = Post.objects.create(
            article_title=title,
            article_slug=fake_gen.slug(value=title),
            article_body=fake_gen.text(),
            article_author=user,
            article_status=Post.Status.PUBLISHED,
        )
        cls.name = fake_gen.unique.first_name()
        cls.email = fake_gen.unique.email()
        cls.comment_body = fake_gen.text()
        cls.comment = Comment.objects.create(
            related_post=cls.post,
            user_name=cls.name,
            user_email=cls.email,
            comment_body=cls.comment_body,
        )

        cls.comment_field_names = [
            "related_post",
            "user_name",
            "user_email",
            "comment_body",
            "comment_created",
            "comment_updated",
            "is_active",
        ]

    def test_comment_content(self):
        self.assertEqual(self.comment.user_name, self.name)
        self.assertEqual(self.comment.user_email, self.email)
        self.assertEqual(self.comment.comment_body, self.comment_body)
        self.assertTrue(self.comment.is_active)

    def test_comment_attr_names(self):
        comment_name = self.comment._meta.verbose_name
        self.assertEqual(comment_name, "comment")

        comment_name_plural = self.comment._meta.verbose_name_plural
        self.assertEqual(comment_name_plural, "comments")

        for field_name in self.comment_field_names:
            verbose_name = field_name.replace("_", " ")
            self.assertEqual(
                self.comment._meta.get_field(field_name).verbose_name,
                verbose_name,
            )

    def test_comment_attr_max_length(self):
        user_name_max_length = self.comment._meta.get_field(
            "user_name"
        ).max_length
        self.assertEqual(user_name_max_length, 80)
        text_name_max_length = self.comment._meta.get_field(
            "comment_body"
        ).max_length
        self.assertEqual(text_name_max_length, 500)

    def test_comment_dunder_str(self):
        self.assertEqual(
            str(self.comment), f"Comment by {self.name} on {self.post}"
        )

    def test_comment_body_markdown_security(self):
        fake_gen = Faker()
        name = fake_gen.unique.first_name()
        email = fake_gen.unique.email()
        comment_body = (
            "Some text. <script src='evil.com'></script> Another text."
        )
        unsafe_comment = Comment.objects.create(
            related_post=self.post,
            user_name=name,
            user_email=email,
            comment_body=comment_body,
        )

        assert (
            "<script src='evil.com'></script>"
            not in unsafe_comment.comment_body
        )
        assert "text" in unsafe_comment.comment_body
