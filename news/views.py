# from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
# from django.shortcuts import render
# from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string


class PostList(ListView):
    model = Post
    ordering = '-public_date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10


class CategoryList(PostList):
    template_name = 'category_posts.html'
    context_object_name = 'category_posts'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-public_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


class PostSearch(ListView):
    model = Post
    ordering = '-public_date'
    template_name = 'posts_search.html'
    context_object_name = 'posts'
    paginate_by = 10

    # Переопределяем функцию получения списка
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


# функция рассылки писем, которую мы используем ниже
def mailing(post):
    # Создадим цикл, чтобы охватить все категории одного поста
    subscribers = set()
    for post_category in post.category.all():
        email_list = User.objects.filter(category=post_category).values('email')
        for email in email_list:
            subscribers.add(email['email'])

    messages = list()
    # Через цикл набиваем список сообщений, чтоб они были индивидуальны для каждого пользователя
    for subscriber in subscribers:
        html_content = render_to_string(
            'post_created.html',
            {
                'username': User.objects.get(email=subscriber),
                'post': post
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новая статья {post.author} - "{post.header}"',
            body='',
            from_email='mikhkirill@yandex.ru',
            to=[subscriber],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        messages.append(msg)

    connection = get_connection()  # uses SMTP server specified in settings.py
    connection.send_messages(messages)


# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/news/')
#
#     form = PostForm
#     return render(request, 'post_edit.html', {'form': form})
class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'post'

        if super().form_valid(form):  # делаем form_valid, чтоб статья добавилась в ДБ и образовались связи
            mailing(post)
            return super().form_valid(form)


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'news'

        if super().form_valid(form):  # делаем form_valid, чтоб статья добавилась в ДБ и образовались связи
            mailing(post)
            return super().form_valid(form)


class PostEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    # указываем форму из файла forms.py - сами сделали
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    msg = f'Вы подписались на рассылку категории "{category}"'
    return render(request, 'subscribe.html', {'message': msg})


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)

    msg = f'Вы отписались от рассылки категории "{category}"'
    return render(request, 'subscribe.html', {'message': msg})