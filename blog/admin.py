from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
# Register your models here.
from .models import Post, Category, Tag, Comment

# 보안 escape 처리 해결
from django.utils.safestring import mark_safe

class CategoryAdmin(admin.ModelAdmin):
    # name 필드 입력시 slug 자동생성
    prepopulated_fields = {"slug": ("name",)}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, MarkdownxModelAdmin)

admin.site.register(Comment)
