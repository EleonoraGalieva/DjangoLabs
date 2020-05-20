import hashlib, sys

from django.core.mail import send_mail
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.utils import dateformat, timezone

from .models import Article, Account
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, AccountForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.conf import settings


def home(request):
    latest_articles_list = Article.objects.order_by('-pub_date')[:4]
    latest_article_1 = latest_articles_list[0]
    latest_article_2 = latest_articles_list[1]
    latest_article_3 = latest_articles_list[2]
    latest_article_4 = latest_articles_list[3]
    data = {'latest_article_1': latest_article_1, 'latest_article_2': latest_article_2,
            'latest_article_3': latest_article_3, 'latest_article_4': latest_article_4}
    return render(request, 'articles/home.html', context=data)


def articles_list(request, type_of_article):
    news_list = Article.objects.filter(type=type_of_article)
    data = {'latest_articles_list': news_list, 'type_of_article': type_of_article}
    return render(request, 'articles/list.html', context=data)


def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user)
            login(request, user)
            sha = hashlib.md5(request.user.username.encode())
            send_mail(
                'Email verification',
                render_to_string('message/email_message.txt', {
                    'name': request.user.username,
                    'email': request.user.email,
                    'text': 'http://mynewsappp.herokuapp.com/articles/confirmation/' + sha.hexdigest(),
                    'time': str(dateformat.format(timezone.now(), 'Y-m-d H:i:s')),
                }), settings.EMAIL_HOST_USER, [request.user.email])
            #messages.success(request, 'An account was created! Check your email for verification.')
            return redirect('articles:home')
    data = {'form': form}
    return render(request, 'articles/register.html', context=data)


def login_method(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('articles:home')
        else:
            messages.info(request, 'Username or password is incorrect')
    data = {}
    return render(request, 'articles/login.html', context=data)


def logout_method(request):
    logout(request)
    return redirect('articles:home')


def show_article(request, article_id):
    try:
        a = Article.objects.get(id=article_id)
    except:
        raise Http404('Article not found')
    comments_list = a.comment_set.all()
    data = {'article': a, 'comments_list': comments_list}
    return render(request, 'articles/single-post.html', context=data)


def my_profile(request):
    if request.user.is_authenticated:
        user = request.user.account
        form = AccountForm(instance=user)
        if request.method == 'POST':
            form = AccountForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
        data = {'form': form}
        return render(request, 'articles/profile_page.html', context=data)
    else:
        return redirect('articles:login')


def leave_comment(request, article_id):
    if request.user.is_authenticated:
        try:
            article = Article.objects.get(id=article_id)
        except:
            raise Http404("Article not found")
        article.comment_set.create(author_name=request.user.account, comment_text=request.POST.get('comment_text'))
        return HttpResponseRedirect(reverse('articles:article', args=(article.id,)))
    else:
        return redirect('articles:login')


def confirmation(request, name):
    accounts = Account.objects.all()
    data = {"information": "Congrats! Your account is verified!"}
    for account in accounts:
        sha = hashlib.md5(account.user.username.encode())
        if sha.hexdigest() == name:
            account.verified = True
            account.save()
            break
    return render(request, 'articles/confirmation_page.html', context=data)
