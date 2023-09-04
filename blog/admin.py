from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
# Register your models here.
from .models import Post, Category, Tag, Comment

# 보안 escape 처리 해결
from django.utils.safestring import mark_safe

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'photo_tag', 'content', 'content_length', 'is_public', 'created_at', 'updated_at']
    list_display_links = ['content']
    list_filter = ['created_at', 'is_public']
    search_fields = ['content']

    def photo_tag(self, post):
        if post.head_image:
            return mark_safe(f'<img src="{post.head_image.url}" style="width:50px;" />')
        return None

    def content_length(self, post):
        return len(post.message)
    content_length.shor_description = "글자수"


class CategoryAdmin(admin.ModelAdmin):
    # name 필드 입력시 slug 자동생성
    prepopulated_fields = {"slug": ("name",)}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post)
admin.site.register(Comment)
