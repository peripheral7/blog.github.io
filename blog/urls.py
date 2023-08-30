from django.urls import path

# 폴더 있는 views.py 가져오기
from . import views

# blog/로 끝아면 임포트한 views.py 에 정의된 index 함수 실행
urlpatterns = [
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),

    # 파일명은 post_list.html
    path('', views.PostList.as_view()),
    # 파일명을 post_detail.html 로 바꿔주거나 template_name = "blog/file_name.html"
    path('<int:pk>/', views.PostDetail.as_view())

    # path('/<int:pk>/', views.single_post_page),
    # path('/', views.index), # FBV
]
