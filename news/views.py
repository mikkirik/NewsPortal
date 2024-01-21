# from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import  reverse_lazy
# from django.shortcuts import render
# from django.http import HttpResponseRedirect
from .models import Post
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string


class PostList(ListView):
    model = Post
    ordering = '-public_date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10


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
        return super().form_valid(form)


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'news'

        # получаем наш html
        html_content = render_to_string(
            'post_created.html',
            {
                'post': post,
                'post_short': post.content[:49] + '...'
            }
        )

        # в конструкторе уже знакомые нам параметры, да? Называются правда немного по-другому, но суть та же.
        msg = EmailMultiAlternatives(
            subject=f'Новая статья {post.author} - "{post.header}"',
            body='',
            from_email='mikhkirill@yandex.ru',
            to=['mikhkirill@yandex.ru', 'mikkirik@gmail.com'],
        )
        msg.attach_alternative(html_content, "text/html")  # добавляем html
        msg.send()  # отсылаем

        return super().form_valid(form)


class PostEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    # указываем форму из файла forms.py - сами сделали
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin ,DeleteView):
    permission_required = 'news.delete_post'
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
