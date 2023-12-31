from django.urls import path
# 폴더 있는 views.py 가져오기
from . import views

# blog/로 끝아면 임포트한 views.py 에 정의된 index 함수 실행
urlpatterns = [
    path('search/<str:q>/', views.PostSearch.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('delete_post/<int:pk>/', views.delete_post, name="delete_post"),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/new_comment/', views.new_comment),
    # 파일명은 post_list.html
    path('', views.PostList.as_view()),
    # 파일명을 post_detail.html 로 바꿔주거나 template_name = "blog/file_name.html"
    path('<int:pk>/', views.PostDetail.as_view()),


    # path('/<int:pk>/', views.single_post_page),
    # path('/', views.index), # FBV
]
