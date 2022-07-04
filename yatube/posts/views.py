from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post, Group, User


def paginate_posts(request, posts):
    """Вспомогательная функция для создания объекта Paginator"""
    return Paginator(posts, 10).get_page(request.GET.get('page'))


def index(request):
    """Отображение всех последних 10 постов"""
    return render(
        request,
        'posts/index.html',
        {'page_obj': paginate_posts(request, Post.objects.all())}
    )


def group_posts(request, slug):
    """Отображение постов конкретной группы"""
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginate_posts(request, group.posts.all()),
    })


def profile(request, username):
    """Отображение профиля конкретного пользователя"""
    author = get_object_or_404(User, username=username)
    return render(request, 'posts/profile.html', {
        'page_obj': paginate_posts(request, author.posts.all()),
        'author': author,
    })


def post_detail(request, post_id):
    """Отображение информации конкретного поста"""
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание нового поста"""
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    """Изменение поста"""
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail')
    form = PostForm(request.POST or None, instance=post)
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': is_edit
        }
        return render(request, 'posts/create_post.html', context)
    post = form.save()
    return redirect('posts:post_detail', post_id)
