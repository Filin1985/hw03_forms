from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post, Group, User


def paginate_posts(request, posts):
    """Вспомогательная функция для создания объекта Paginator"""
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Отображение всех последних 10 постов"""
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = paginate_posts(request, post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Отображение постов конкретной группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    page_obj = paginate_posts(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отображение профиля конкретного пользователя"""
    if not User.objects.filter(username=username).exists():
        messages.error(request, 'Автора с данным именем не существует!')
        return redirect('posts:index')
    author = User.objects.get(username=username)
    posts_list = (
        Post.objects.select_related('author')
        .filter(author__username=username)
    )    
    page_obj = paginate_posts(request, posts_list)
    context = {
        'page_obj': page_obj,
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отображение информации конкретного поста"""
    post = get_object_or_404(Post, id=post_id)
    posts_list = (
        Post.objects.select_related('author')
        .filter(author__username=post.author)
    )
    context = {
        'post': post,
        'posts_list': posts_list,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required(login_url='login')
def post_create(request):
    """Создание нового поста"""
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user.username)
   

@login_required(login_url='login')
def post_edit(request, post_id):
    """Изменение поста"""
    is_edit = True
    if not Post.objects.filter(id=post_id).exists():
        messages.error(request, 'Данного поста не существует!')
        return redirect('posts:index')
    post = Post.objects.get(id=post_id)
    if request.user != post.author:
        messages.error(request, 'Только автор может редактировать пост')
        return redirect('posts:index')
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        context = {
            'form': form, 
            'is_edit': is_edit
        }
        return render(request, 'posts/create_post.html', context)
    post = form.save()
    return redirect('posts:post_detail', post_id)
