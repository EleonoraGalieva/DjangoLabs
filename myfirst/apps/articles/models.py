from django.db import models
import datetime
from django.utils import timezone
from .apps import ArticlesConfig
from django.contrib.auth.models import User


class Author(models.Model):
    author_name = models.CharField("Author's name", max_length=60)
    author_organisation = models.CharField("Author's organisation", max_length=80)

    def __str__(self):
        return self.author_name


class Article(models.Model):
    TYPE = (
        ("BUSINESS", "BUSINESS"),
        ("HEALTH", "HEALTH"),
        ("TECH", "TECH"),
        ("SCIENCE", "SCIENCE"),
        ("OTHER", "OTHER")
    )
    article_title = models.CharField("Article name", max_length=200)
    article_text = models.TextField("Article text")
    pub_date = models.DateTimeField("Publication date")
    type = models.CharField("Type of article", max_length=30, choices=TYPE)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING, null=True, blank=True)
    article_pic = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.article_title

    def was_published_recently(self):
        return self.pub_date >= (timezone.now() - datetime.timedelta(days=7))


class Ad(models.Model):
    # ad_photo = models.ImageField()
    ad_title = models.CharField("Ad title", max_length=30)
    ad_text = models.CharField("Ad text", max_length=60)
    ad_duration = models.DurationField()


class Account(models.Model):
    name = models.CharField("Author's name", max_length=60, default="Anonymous")
    email = models.EmailField("Author's email", max_length=100)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, default='prof_pic1.png')
    verified = models.BooleanField(default=False)


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author_name = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    comment_text = models.CharField("Comment text", max_length=200, null=True)

    def __str__(self):
        return self.author_name.name
