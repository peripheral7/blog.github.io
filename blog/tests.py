from turtle import update
from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment

# Create your tests here.
class TestView(TestCase):
    # test case 초기 데이터베이스 상태 정의
    # 클래스 안 다른 테스트 함수에 공통적으로 적용.
    def setUp(self):
        self.client = Client()
        self.user_Trump = User.objects.create_user(
            username="Trump", password="iamTrump"
        )
        self.user_Biden = User.objects.create_user(
            username="Biden", password="iamBiden"
        )
        self.user_Biden.is_staff = True
        self.user_Biden.save()

        self.category_study = Category.objects.create(name="study", slug="study")
        self.category_daily = Category.objects.create(name="daily", slug="daily")

        self.tag_photo = Tag.objects.create(name="photo", slug="photo")
        self.tag_programming = Tag.objects.create(name="programming", slug="programming")
        self.tag_diary = Tag.objects.create(name="diary", slug="diary")

        
        self.post_001 = Post.objects.create(
            title="First Post",
            content="This is what User Biden says.",
            author=self.user_Biden,
            category=self.category_study,
        )
        self.post_002 = Post.objects.create(
            title="Second Post",
            content="This is what User Trump says.",
            author=self.user_Trump,
            category=self.category_daily,
        )

        self.post_001.tags.add(self.tag_programming)
        self.post_002.tags.add(self.tag_photo)
        self.post_002.tags.add(self.tag_diary)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_Trump,
            content='댓글1 입니다.'
        )

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn("Blog", navbar.text)
        self.assertIn("About", navbar.text)

        # logo_btn = navbar.find("a", text="Here's to Better Us")
        # self.assertEqual(logo_btn.attrs["href"], "/")

        home = navbar.find("a", text="Home")
        self.assertEqual(home.attrs["href"], "/")

        blog = navbar.find("a", text="Blog")
        self.assertEqual(blog.attrs["href"], "/blog/")

        about = navbar.find("a", text="About")
        self.assertEqual(about.attrs["href"], "/about/")

    def test_category_page(self):
        response = self.client.get(self.category_study.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_study.name, soup.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_study.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)

    def category_card_test(self, soup):
        categories_card = soup.find("div", id="categories-card")
        self.assertIn("Categories", categories_card.text)
        self.assertIn(
            f"{self.category_daily.name} ({self.category_daily.post_set.count()})",
            categories_card.text,
        )
        self.assertIn(
            f"{self.category_study.name} ({self.category_study.post_set.count()})",
            categories_card.text,
        )
        self.assertIn(f"미분류", categories_card.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_programming.name, soup.h1.text)

        main_area = soup.find('div', id="main-area")
        self.assertIn(self.tag_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 2)

        # 1.1 포스트 목록 페이지
        # 이때 열리는 웹 페이지 정보를 response에 저장
        response = self.client.get("/blog/")
        # 1.2 페이지 로드
        # response 에 저장된 status_code 200(정상적으로 열림)
        self.assertEqual(response.status_code, 200)
        # 1.3. 페이지 타이틀 Blog
        # HTML요소 쉽게 접근하게 읽어들임. parse 명령어
        soup = BeautifulSoup(response.content, "html.parser")

        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.2 아직 게시물이 없습니다
        main_area = soup.find("div", id="main-area")
        self.assertNotIn("No content yet.", main_area.text)

        # 3.2 포스트 목록 새로고침 시
        # response = self.client.get("/blog/")
        # soup = BeautifulSoup(response.content, "html.parser")
        # self.assertEqual(response.status_code, 200)

        # 3.3 메인영역 포스트 2개 타이틀 존재
        post_001_card = main_area.find("div", id="post-1")
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.user_Biden.username, main_area.text)
        self.assertIn(self.tag_programming.name, post_001_card.text)
        self.assertNotIn(self.tag_photo.name, post_001_card.text)
        self.assertNotIn(self.tag_diary.name, post_001_card.text)

        post_002_card = main_area.find("div", id="post-2")
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.user_Trump.username, main_area.text)
        self.assertIn(self.tag_photo.name, post_002_card.text)
        self.assertIn(self.tag_diary.name, post_002_card.text)
        self.assertNotIn(self.tag_programming.name, post_002_card.text)

        # if no post
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get("/blog/")
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")
        self.assertIn("No content yet.", main_area.text)

    def test_post_detail(self):
        # 1.1 포스트 하나
        # new database

        # url은 '/blog/1/'
        self.assertEqual(self.post_001.get_absolute_url(), "/blog/1/")

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상작동
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        # 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에
        self.assertIn(self.post_001.title, soup.title.text)

        # 첫 번째 포스트의 제목이 포스트 영역에
        main_area = soup.find("div", id="main-area")
        post_area = main_area.find("article", id="post-area")
        self.assertIn(self.post_001.title, post_area.text)

        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에
        # 2.6 첫 번째 포스트의 내용이 포스트 영역에
        self.assertIn(self.post_001.content, post_area.text)
        self.assertIn(self.user_Biden.username, post_area.text)
        self.assertIn(self.tag_programming.name, post_area.text)
        self.assertNotIn(self.tag_photo.name, post_area.text)
        self.assertNotIn(self.tag_diary.name, post_area.text)

        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)



    def test_create_post(self):
        # not logged in
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username="Trump", password="iamTrump")
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # sign in as a staff
        self.client.login(username="Biden", password="iamBiden")
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        # self.assertEqual("Create Post - Blog", soup.title.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Practice Post',
                'content': "Create Post Form Page",
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 3)
        last_post = Post.objects.last()
        self.assertEqual(last_post.author.username, "Biden")
        self.assertEqual(last_post.title, "Practice Post")
        self.assertEqual(last_post.content, "Create Post Form Page")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.get(name='python'))

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_001.pk}/'

        # not signed in 
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # logged in but not the writer
        self.assertNotEqual(self.post_001.author, self.user_Trump)
        self.client.login(
            username=self.user_Trump.username,
            password="iamTrump"
        )
        response=self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # writer access
        self.client.login(
            username=self.post_001.author.username,
            password="iamBiden"
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)
        
        # tag
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('programming', tag_str_input.attrs['value'])
        
        response = self.client.post(
            update_post_url,
            {
                'title': 'Edited',
                'content': 'Hello world',
                'category': self.category_study.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edited', main_area.text)
        self.assertIn('Hello world', main_area.text)
        self.assertIn(self.category_study.name, main_area.text)
        
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)