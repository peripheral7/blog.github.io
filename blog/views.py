# from django.shortcuts import render
from urllib import response
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Post, Category, Tag
from django.shortcuts import render, redirect
# sign in
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify

# Create your views here.

# ListView 상속한 PostList 클래스 선언
class PostList(ListView):
    model = Post
    # 파일명 post_list 로 수정하면 자동 반영 - 관용적으로 이름짓기
    # 또는 template_name = 'blog/index.html'
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context 

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else: 
        # url 에서 떼어줌 <str:slug>
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request, 
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,

        }
    )
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request, 
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )

# 개별 페이지
class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context 

class PostCreate(LoginRequiredMixin, UserPassesTestMixin,   CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    # author 필드를 로그인한 사용자로 채워줌
    # form_valid 함수 내장 , 유효한 정보로 포스트 생성, 고유경로로 보내줌(redirect)
    def form_valid(self, form):
        # visitor
        current_user = self.request.user
        # if signed in:
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            # author of the form is current_user
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list: 
                    t = t.strip()
                    if t != '':
                        tag, is_tag_created = Tag.objects.get_or_create(name=t)
                        if is_tag_created:
                            tag.slug = slugify(t, allow_unicode=True)
                            tag.save()
                        self.object.tags.add(tag)
                
            # send form as argument of form_valid()
            return response
        else: 
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context 

    # only writer can approach
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list: 
                t = t.strip()
                if t != '':
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            
        # send form as argument of form_valid()
        return response


"""Function Based View
def index(request):
    # send query to database, bring record as dictionary
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'blog/index.html',
        {
            'posts': posts,
        }
    )

def single_post_page(request, pk):
    # get - 괄호 안의 조건을 만족하는 post 레코드 가져오라
    post = Post.objects.get(pk=pk)

    return render(
        request, 
        'blog/single_post_page.html',
        {
            'post': post,
        }
    )
"""