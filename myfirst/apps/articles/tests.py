import pytest
from mixer.backend.django import mixer
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, SimpleTestCase, Client, RequestFactory
from django.urls import reverse, resolve
from .models import Author, Article
from .views import *
from .forms import UserCreationForm, AccountForm


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(author_name="Kate", author_organisation="BBC")

    def test_author_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('author_name').verbose_name
        self.assertEquals(field_label, "Author's name")

    def test_author_organisation_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("author_organisation").verbose_name
        self.assertEquals(field_label, "Author's organisation")

    def test___str__(self):
        author = Author.objects.get(id=1)
        expected_str = author.author_name
        self.assertEqual(expected_str, author.__str__())


class ArticleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Article.objects.create(article_title="Some title", article_text="Some text", pub_date=timezone.now())

    def test_article_title(self):
        article = Article.objects.get(id=1)
        field_label = article._meta.get_field("article_title").verbose_name
        self.assertEqual(field_label, "Article name")

    def test_article_text(self):
        article = Article.objects.get(id=1)
        field_label = article._meta.get_field("article_text").verbose_name
        self.assertEqual(field_label, "Article text")

    def test_article_type(self):
        article = Article.objects.get(id=1)
        field_label = article._meta.get_field("type").verbose_name

    def test___str__(self):
        article = Article.objects.get(id=1)
        expected_str = article.article_title
        self.assertEqual(expected_str, article.__str__())

    def test_was_published_recently(self):
        article = Article.objects.get(id=1)
        self.assertEqual(True, article.was_published_recently())


# Testing views:

def test_login_url_is_resolved():
    url = reverse("articles:login")
    assert resolve(url).view_name == 'articles:login'


def test_logout_url_is_resolved():
    url = reverse("articles:logout")
    assert resolve(url).view_name == 'articles:logout'


def test_home_url_is_resolved():
    url = reverse("articles:home")
    assert resolve(url).view_name == 'articles:home'


def test_register_url_is_resolved():
    url = reverse("articles:register")
    assert resolve(url).view_name == 'articles:register'


def test_myprofile_url_is_resolved():
    url = reverse("articles:my_profile")
    assert resolve(url).view_name == 'articles:my_profile'


def test_article_url_is_resolved():
    url = reverse("articles:article", args=['1'])
    assert resolve(url).view_name == 'articles:article'


def test_comment_url_is_resolved():
    url = reverse("articles:leave_comment", args=['1'])
    assert resolve(url).view_name == 'articles:leave_comment'


# Testing views
@pytest.fixture(scope='module')
def factory():
    return RequestFactory()


@pytest.fixture()
def client(db):
    return Client()


@pytest.fixture()
def user(db):
    user = User.objects.create_user(username='Kate', email='kate@gmail.com', password='kate98')
    account = Account.objects.create(name="Kate J", email='kate@gmail.com', user=user)
    return user


@pytest.fixture()
def article(db):
    pic = "prof_pic1.png"
    a = Article.objects.create(article_title="Title", pub_date=timezone.now(), article_text="Text",
                               article_pic=pic, id=0)
    Article.objects.create(article_title="Title", pub_date=timezone.now(), article_text="Text",
                           article_pic=pic, id=1)
    return a


@pytest.mark.parametrize('amount_of_articles', [4])
def test_home_page(factory, amount_of_articles, db):
    pic = "prof_pic1.png"
    articles = mixer.cycle(amount_of_articles).blend(Article, article_title='Tile', pub_date=timezone.now(),
                                                     article_text='Text',
                                                     article_pic=pic)
    data = {'latest_article_1': articles[0],
            'latest_article_2': articles[1],
            'latest_article_3': articles[2],
            'latest_article_4': articles[3]}
    home_url = reverse("articles:home")
    request = factory.get(home_url)
    response = home(request)
    assert response.status_code == 200


def test_article_list_page(factory, db):
    pic = "prof_pic1.png"
    articles = mixer.cycle(4).blend(Article, article_title="Title", pub_date=timezone.now(),
                                    article_text="Text",
                                    article_pic=pic)
    data = {'latest_articles_list': articles, 'type_of_article': "OTHER"}
    list_url = reverse("articles:articles_list", args=["OTHER"])
    request = factory.get(list_url)
    response = articles_list(request, type_of_article="OTHER")
    assert response.status_code == 200


def test_login_page(client, db):
    login_url = reverse("articles:login")
    client.login(username='lfk', password='erj')
    response = client.post(login_url)
    assert response.status_code == 200


def test_login_with_user(factory, user, db):
    login_url = reverse("articles:login")
    request = factory.get(login_url)
    request.user = user
    response = login_method(request)
    assert response.status_code == 200


def test_logout_page(client, db):
    logout_url = reverse("articles:logout")
    client.logout()
    response = client.post(logout_url)
    assert response.status_code == 302


def test_article_page(article, factory, db):
    comments_list = {}
    article_url = reverse("articles:article", args=[0])
    data = {'article': article}
    request = factory.get(article_url)
    response = show_article(request, article_id=0)
    assert response.status_code == 200


def test_article_page_error(article, client, db):
    a = article
    Article.objects.filter(id=0).delete()
    comments_list = {}
    article_url = reverse("articles:article", args=[0])
    data = {'article': a}
    response = client.get(article_url, data=data)
    assert response.status_code == 404


def test_my_profile(client):
    my_profile_url = reverse("articles:my_profile")
    client.login(username='lfk', password='erj')
    response = client.post(my_profile_url, {'form': AccountForm()})
    assert response.status_code == 302


def test_my_profile_with_user(factory, user, db):
    my_profile_url = reverse("articles:my_profile")
    request = factory.get(my_profile_url)
    request.user = user
    response = my_profile(request)
    assert response.status_code == 200


def test_comments(factory, user, article):
    comments_url = reverse("articles:leave_comment", args=['1'])
    request = factory.get(comments_url)
    request.user = user
    response = leave_comment(request, 1)
    assert response.status_code == 302


def test_comments_error(factory, article):
    comments_url = reverse("articles:leave_comment", args=[0])
    request = factory.get(comments_url)
    request.user = AnonymousUser()
    response = leave_comment(request, 0)
    assert response.status_code == 302
