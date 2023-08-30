from django.db import models
from django.contrib.auth.models import User
from markdownx.utils import markdownify
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # slug : 고유 url
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'
    class Meta:
        # 아니면 category + s로 만듦.
        verbose_name_plural = "Categories"
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # slug : 고유 url
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True)
    file_upload = models.FileField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # Null 은 삭제시, blank는 입력시 빈칸 대비
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    # 태그 삭제시 포스트 태그는 자동 blank
    tags = models.ManyToManyField(Tag, blank=True)
    

    def __str__(self):
        return f"[{self.pk}] {self.title} :: {self.author}"

    # url 생성 규칙
    def get_absolute_url(self):
        return f"/blog/{self.pk}/"

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split(".")[-1]
    
    # content field to HTML 
    def get_content_markdown(self):
        return markdown(self.content)

class About_post(models.Model):
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    head_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True)
    file_upload = models.FileField(upload_to="blog/files/%Y/%m/%d/", blank=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content = models.TextField()

    def __str__(self):
        return f'{self.author}::{self.content}'