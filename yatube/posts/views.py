from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required  # noqa
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Post, Group, User


def index(request):
    """Отображение всех последних 10 постов"""
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Отображение постов конкретной группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отображение профиля конкретного пользователя"""
    posts_list = (
        Post.objects.select_related('author')
        .filter(author__username=username)
    )
    author = User.objects.get(username=username)
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts_length = page_obj.object_list.count
    context = {
        'page_obj': page_obj,
        'posts_length': posts_length,
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отображение информации конкретного поста"""
    post = get_object_or_404(Post, id=post_id)
    is_author = request.user == post.author
    posts_list = (
        Post.objects.select_related('author')
        .filter(author__username=post.author)
    )
    posts_length = len(posts_list)
    context = {
        'post': post,
        'posts_length': posts_length,
        'is_author': is_author
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    """Создание нового поста"""
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user.username)
    context = {'form': form}
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    """Изменение поста"""
    is_edit = True
    post = Post.objects.get(id=post_id)
    if request.user != post.author:
        raise Http404("Вы не можете редактировать чужие посты!")
    else:
        form = PostForm(instance=post)
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save()
                return redirect('posts:post_detail', post_id)
        context = {
            'form': form,
            'is_edit': is_edit
        }
        return render(request, 'posts/create_post.html', context)
