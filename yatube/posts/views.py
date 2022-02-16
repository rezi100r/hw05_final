from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


NUMBER_OF_POSTS = 10


def index(request):
    """Функция главной страницы с выводом всех постов"""

    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Функция вывода всех постов группы"""

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Функция профиля пользователя с выводом всех его постов"""

    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    paginator = Paginator(user_posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'page_obj': page_obj,
    }
    if request.user.username == username:
        return render(request, template, context)
    elif request.user.is_authenticated:
        following = True if Follow.objects.filter(
            user=request.user
        ).filter(author=user) else False
        context = {
            'author': user,
            'page_obj': page_obj,
            'following': following,
        }
        return render(request, template, context)
    else:
        return render(request, template, context)


def post_detail(request, post_id):
    """Функция просмотра отдельного поста"""

    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    posts_count = post.author.posts.all().count()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """
     Функция редактирования поста
     GET: если пользователь не автор форвардит
     на функцию post_detail иначе рендерит форму для редактирования.
     """

    template = 'posts/post_create.html'
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'GET':
        if not post.author == request.user:
            return redirect('posts:post_detail', post.id)
        form = PostForm(instance=post)
        context = {
            'form': form,
            'post': post,
        }
        return render(request, template, context)

    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None,)
    if form.is_valid():
        form.save()
    return redirect('posts:post_detail', post.id)


@login_required
def post_create(request):
    """
    Функция создания поста
    GET: рендерит форму на страницу
    POST: проверяет валидность фанных и создает запись в базе.
    """

    template = 'posts/post_create.html'

    if request.method == 'GET':
        form = PostForm()
        context = {
            'form': form,
        }
        return render(request, template, context)

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, template, {'form': form})


@login_required
def add_comment(request, post_id):
    """Функция создания комментария"""

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Функция избранных авторов"""
    template = 'posts/follow.html'
    faivorite_authors = Follow.objects.filter(
        user=request.user
    ).all().values_list('author')
    post_list = Post.objects.select_related(
        'author'
    ).all().filter(author_id__in=faivorite_authors)
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    if request.user.username == username:
        return redirect('posts:index')
    obj, created = Follow.objects.get_or_create(
        user=request.user,
        author=User.objects.get(username=username)
    )
    if created:
        obj.save()
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.filter(user=request.user).filter(author=author)
    unfollow.delete()
    return redirect('posts:index')
