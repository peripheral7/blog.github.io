from turtle import update
from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from .models import Post, Category, Tag

# Create your tests here.
class TestView(TestCase):
    # test case 초기 데이터베이스 상태 정의
    # 클래스 안 다른 테스트 함수에 공통적으로 적용.
    def setUp(self):
        self.client = Client()
        self.user_Biden = User.objects.create_user(
            username="Biden", password="iamBiden"
        )
        self.user1 = User.objects.create_user(
            username="User1", password="iamTrump"
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
            content="First content it is.",
            author=self.user_Biden,
            category=self.category_study,
        )
        self.post_001.tags.add(self.tag_programming)

        self.post_002 = Post.objects.create(
            title="Second Post",
            content="Hell No world.",
            author=self.user1,
            category=self.category_daily,
        )
        self.post_002.tags.add(self.tag_photo)
        self.post_002.tags.add(self.tag_diary)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn("Home", navbar.text)
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

        # 1. 포스트 목록 페이지 가져와 response 저장, 페이지 정상 로드 확인, soup. 명령어.
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 포스트 목록 새로고침 시
        # response = self.client.get("/blog/")
        # soup = BeautifulSoup(response.content, "html.parser")
        # self.assertEqual(response.status_code, 200)

        # 게시물 확인.
        main_area = soup.find("div", id="main-area")
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
        self.assertIn(self.user1.username, main_area.text)
        self.assertIn(self.tag_photo.name, post_002_card.text)
        self.assertIn(self.tag_diary.name, post_002_card.text)
        self.assertNotIn(self.tag_programming.name, post_002_card.text)

        # If there's no Post
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get("/blog/")
        soup = BeautifulSoup(response.content, "html.parser")
        main_area = soup.find("div", id="main-area")
        self.assertIn("No content yet.", main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), "/blog/1/")

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        self.assertIn(self.post_001.title, soup.title.text)
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
    
    def test_create_post(self):
        # not logged in
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username="User1", password="iamTrump")
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # sign in as a staff
        self.client.login(username="Biden", password="iamBiden")
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")

        self.assertEqual("Create Post - Blog", soup.title.text)
        main_area = soup.find("div", id="main-area")
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Practice Post',
                'content': "Create Post Form Page",
                'tags_str': 'programming, 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 3)
        last_post = Post.objects.last()
        self.assertEqual(last_post.author.username, "Biden")
        self.assertEqual(last_post.title, "Practice Post")
        self.assertEqual(last_post.content, "Create Post Form Page")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='programming'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.get(name='python'))

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_001.pk}/'

        # not signed in 
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # logged in but not the writer
        self.assertNotEqual(self.post_001.author, self.user1)
        self.client.login(
            username=self.user1.username,
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
                'tags_str': 'programming; 한글태그'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edited', main_area.text)
        self.assertIn('Hello world', main_area.text)
        self.assertIn(self.category_study.name, main_area.text)
        
        self.assertIn('programming', main_area.text)
        self.assertIn('한글태그', main_area.text)
        self.assertNotIn('python', main_area.text)