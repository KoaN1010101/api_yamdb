from csv import DictReader

from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User

ALREDY_LOADED_ERROR_MESSAGE = """
Data already loaded. If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""

CATEGORY_CSV = './static/data/category.csv'
GENRE_CSV = './static/data/genre.csv'
USER_CSV = './static/data/users.csv'
TITLE_CSV = './static/data/titles.csv'
REVIEW_CSV = './static/data/review.csv'
COMMENT_CSV = './static/data/comments.csv'
GENRE_TITLE_CSV = './static/data/genre_title.csv'


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.download_category_csv()
        self.download_genre_csv()
        self.download_user_csv()
        self.download_title_csv()
        self.download_review_csv()
        self.download_comment_csv()
        self.download_genre_title_csv()

    def download_category_csv(self):
        if Category.objects.exists():
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading category data")
        with open(CATEGORY_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                category = Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
                category.save()

    def download_genre_csv(self):
        if Genre.objects.exists():
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading genre data")
        with open(GENRE_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                genre = Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
                genre.save()

    def download_user_csv(self):
        if User.objects.exists():
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading user data")
        with open(USER_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                user = User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                user.save()

    def download_title_csv(self):
        if Title.objects.exists():
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading title data")
        with open(TITLE_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                title = Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category']
                )
                title.save()

    def download_review_csv(self):
        if Review.objects.exists():
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading review data")
        with open(REVIEW_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                review = Review(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                )
                review.save()

    def download_comment_csv(self):
        if Comment.objects.exists():
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading comments data")
        with open(COMMENT_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                comment = Comment(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date']
                )
                comment.save()

    def download_genre_title_csv(self):
        print("Loading title genre data")
        with open(GENRE_TITLE_CSV, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = DictReader(csv_file)
            for row in csv_reader:
                title = Title.objects.get(id=row['title_id'])
                title.genres.add(row['genre_id'])
