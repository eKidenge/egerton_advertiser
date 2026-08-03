#!/usr/bin/env python
import random
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from faker import Faker
from apps.accounts.models import User
from apps.articles.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.comments.models import Comment
from apps.advertisements.models import Advertisement
from apps.media_library.models import MediaFile
from apps.newsletter.models import Subscriber, Newsletter
from apps.contacts.models import ContactMessage
from apps.settings_manager.models import SiteSetting
from apps.accounts.models import UserActivityLog

fake = Faker('en_US')

class Command(BaseCommand):
    help = 'Seed database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding database with test data...')
        
        # ============================================
        # 1. CREATE SETTINGS
        # ============================================
        self.stdout.write('📝 Creating site settings...')
        settings_data = [
            ('general', 'site_name', 'The Egerton Advertiser'),
            ('general', 'site_tagline', 'Your Local News Source'),
            ('general', 'site_description', 'Egerton\'s Leading Newspaper'),
            ('general', 'site_timezone', 'Africa/Nairobi'),
            ('general', 'site_language', 'en'),
            ('email', 'smtp_host', 'smtp.gmail.com'),
            ('email', 'smtp_port', '587'),
            ('email', 'smtp_username', 'admin@theegertonadvertiser.com'),
            ('email', 'use_tls', 'True'),
            ('email', 'from_email', 'admin@theegertonadvertiser.com'),
            ('email', 'from_name', 'The Egerton Advertiser'),
            ('seo', 'meta_title', 'The Egerton Advertiser - Your Local News'),
            ('seo', 'meta_description', 'Latest news from Egerton and beyond'),
            ('seo', 'enable_sitemap', 'True'),
            ('advertisement', 'enable_ads', 'True'),
            ('advertisement', 'auto_ads', 'False'),
        ]
        
        for category, key, value in settings_data:
            SiteSetting.objects.get_or_create(
                category=category,
                key=key,
                defaults={'value': value}
            )
        
        # ============================================
        # 2. CREATE CATEGORIES
        # ============================================
        self.stdout.write('📂 Creating categories...')
        
        categories = [
            {'name': 'Opinion', 'slug': 'opinion', 'description': 'Opinion pieces and editorials', 'is_active': True},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental news and conservation', 'is_active': True},
            {'name': 'Society', 'slug': 'society', 'description': 'Society and community news', 'is_active': True},
            {'name': 'Politics', 'slug': 'politics', 'description': 'Political news and analysis', 'is_active': True},
            {'name': 'Business', 'slug': 'business', 'description': 'Business and economy news', 'is_active': True},
            {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness news', 'is_active': True},
            {'name': 'Education', 'slug': 'education', 'description': 'Education news and updates', 'is_active': True},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports news and coverage', 'is_active': True},
            {'name': 'Entertainment', 'slug': 'entertainment', 'description': 'Entertainment and lifestyle', 'is_active': True},
            {'name': 'Technology', 'slug': 'technology', 'description': 'Technology and innovation', 'is_active': True},
        ]
        
        for cat_data in categories:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
        
        # ============================================
        # 3. CREATE TAGS
        # ============================================
        self.stdout.write('🏷️ Creating tags...')
        
        tags = [
            {'name': 'Breaking News', 'slug': 'breaking-news', 'is_active': True},
            {'name': 'Featured', 'slug': 'featured', 'is_active': True},
            {'name': 'Opinion', 'slug': 'opinion-tag', 'is_active': True},
            {'name': 'Analysis', 'slug': 'analysis', 'is_active': True},
            {'name': 'Interview', 'slug': 'interview', 'is_active': True},
            {'name': 'Investigation', 'slug': 'investigation', 'is_active': True},
            {'name': 'Environment', 'slug': 'environment-tag', 'is_active': True},
            {'name': 'Climate Change', 'slug': 'climate-change', 'is_active': True},
            {'name': 'Conservation', 'slug': 'conservation', 'is_active': True},
            {'name': 'Community', 'slug': 'community', 'is_active': True},
            {'name': 'Politics', 'slug': 'politics-tag', 'is_active': True},
            {'name': 'Elections', 'slug': 'elections', 'is_active': True},
            {'name': 'Business', 'slug': 'business-tag', 'is_active': True},
            {'name': 'Economy', 'slug': 'economy', 'is_active': True},
            {'name': 'Health', 'slug': 'health-tag', 'is_active': True},
            {'name': 'Education', 'slug': 'education-tag', 'is_active': True},
            {'name': 'Sports', 'slug': 'sports-tag', 'is_active': True},
            {'name': 'Entertainment', 'slug': 'entertainment-tag', 'is_active': True},
            {'name': 'Technology', 'slug': 'technology-tag', 'is_active': True},
            {'name': 'Innovation', 'slug': 'innovation', 'is_active': True},
        ]
        
        for tag_data in tags:
            Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
        
        # ============================================
        # 4. CREATE USERS
        # ============================================
        self.stdout.write('👤 Creating users...')
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@theegertonadvertiser.com',
                'first_name': 'John',
                'last_name': 'Admin',
                'role': 'admin',
                'is_active': True,
                'is_verified': True,
                'password': 'Admin@2026'
            },
            {
                'username': 'editor',
                'email': 'editor@theegertonadvertiser.com',
                'first_name': 'Sarah',
                'last_name': 'Editor',
                'role': 'editor',
                'is_active': True,
                'is_verified': True,
                'password': 'Editor@2026'
            },
            {
                'username': 'journalist1',
                'email': 'journalist1@theegertonadvertiser.com',
                'first_name': 'Michael',
                'last_name': 'Journalist',
                'role': 'journalist',
                'is_active': True,
                'is_verified': True,
                'password': 'Journalist@2026'
            },
            {
                'username': 'journalist2',
                'email': 'journalist2@theegertonadvertiser.com',
                'first_name': 'Emily',
                'last_name': 'Reporter',
                'role': 'journalist',
                'is_active': True,
                'is_verified': True,
                'password': 'Journalist@2026'
            },
            {
                'username': 'advertiser',
                'email': 'advertiser@theegertonadvertiser.com',
                'first_name': 'James',
                'last_name': 'Advertiser',
                'role': 'advertiser',
                'is_active': True,
                'is_verified': True,
                'password': 'Advertiser@2026'
            },
            {
                'username': 'subscriber1',
                'email': 'subscriber1@theegertonadvertiser.com',
                'first_name': 'Lucy',
                'last_name': 'Subscriber',
                'role': 'subscriber',
                'is_active': True,
                'is_verified': True,
                'password': 'Subscriber@2026'
            },
            {
                'username': 'subscriber2',
                'email': 'subscriber2@theegertonadvertiser.com',
                'first_name': 'David',
                'last_name': 'Reader',
                'role': 'subscriber',
                'is_active': True,
                'is_verified': True,
                'password': 'Subscriber@2026'
            },
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'is_active': user_data['is_active'],
                    'is_verified': user_data['is_verified'],
                    'password': make_password(user_data['password'])
                }
            )
        
        # Create 50 random users
        self.stdout.write('👤 Creating 50 random users...')
        for i in range(50):
            User.objects.get_or_create(
                username=fake.user_name(),
                defaults={
                    'email': fake.email(),
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': random.choice(['subscriber', 'journalist']),
                    'is_active': True,
                    'is_verified': random.choice([True, False]),
                    'password': make_password('Password@123')
                }
            )
        
        # ============================================
        # 5. CREATE ARTICLES
        # ============================================
        self.stdout.write('📰 Creating articles...')
        
        categories = Category.objects.all()
        tags = Tag.objects.all()
        authors = User.objects.filter(role__in=['admin', 'editor', 'journalist'])
        
        opinion_cat = Category.objects.get(slug='opinion')
        environment_cat = Category.objects.get(slug='environment')
        society_cat = Category.objects.get(slug='society')
        
        articles_data = [
            # Opinion Articles
            {
                'title': 'The Future of Democracy in Kenya',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'A deep dive into the democratic future of Kenya',
                'category': opinion_cat,
                'status': 'published',
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(100, 5000),
            },
            {
                'title': 'Why Climate Action Cannot Wait',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Urgent action needed on climate change',
                'category': opinion_cat,
                'status': 'published',
                'is_featured': False,
                'is_breaking': True,
                'views_count': random.randint(50, 3000),
            },
            {
                'title': 'The Role of Media in Society',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'Media\'s responsibility in modern society',
                'category': opinion_cat,
                'status': 'published',
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(30, 2000),
            },
            # Environment Articles
            {
                'title': 'Kenya\'s Great Green Wall Initiative',
                'content': fake.paragraph(nb_sentences=35),
                'excerpt': 'Massive reforestation project in Kenya',
                'category': environment_cat,
                'status': 'published',
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(100, 4000),
            },
            {
                'title': 'Plastic Pollution Crisis in Nairobi',
                'content': fake.paragraph(nb_sentences=28),
                'excerpt': 'The growing plastic waste problem',
                'category': environment_cat,
                'status': 'published',
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(50, 2500),
            },
            {
                'title': 'Conservation Success Stories from Maasai Mara',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'Wildlife conservation achievements',
                'category': environment_cat,
                'status': 'published',
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(80, 3500),
            },
            # Society Articles
            {
                'title': 'Education Reform in Kenya',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'New education reforms taking shape',
                'category': society_cat,
                'status': 'published',
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(40, 1800),
            },
            {
                'title': 'Healthcare Access in Rural Communities',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'Challenges in rural healthcare delivery',
                'category': society_cat,
                'status': 'published',
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(60, 2800),
            },
            {
                'title': 'Youth Unemployment and Solutions',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Addressing youth unemployment crisis',
                'category': society_cat,
                'status': 'published',
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(30, 1500),
            },
            # Additional Random Articles
            {
                'title': 'Tech Innovation Hub Opens in Egerton',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'New technology innovation center launched',
                'category': Category.objects.filter(slug='technology').first(),
                'status': 'published',
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(20, 1000),
            },
            {
                'title': 'Sports: Egerton United Wins Championship',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'Local football team triumphs',
                'category': Category.objects.filter(slug='sports').first(),
                'status': 'published',
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(40, 2000),
            },
        ]
        
        for i, article_data in enumerate(articles_data):
            author = random.choice(authors)
            article = Article.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                category=article_data['category'],
                author=author,
                status=article_data['status'],
                is_featured=article_data.get('is_featured', False),
                is_breaking=article_data.get('is_breaking', False),
                views_count=article_data.get('views_count', 0),
                published_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
            
            # Add random tags
            for tag in random.sample(list(tags), random.randint(2, 5)):
                article.tags.add(tag)
        
        # Create 50 more random articles
        self.stdout.write('📰 Creating 50 random articles...')
        categories_list = list(Category.objects.all())
        tags_list = list(Tag.objects.all())
        
        for i in range(50):
            cat = random.choice(categories_list)
            author = random.choice(authors)
            status = random.choice(['published', 'draft', 'pending'])
            article = Article.objects.create(
                title=fake.sentence(nb_words=10),
                content=fake.paragraph(nb_sentences=20),
                excerpt=fake.sentence(nb_words=15),
                category=cat,
                author=author,
                status=status,
                is_featured=random.choice([True, False]),
                is_breaking=random.choice([True, False]),
                views_count=random.randint(0, 5000),
                published_at=timezone.now() - timedelta(days=random.randint(1, 90)) if status == 'published' else None,
                created_at=timezone.now() - timedelta(days=random.randint(1, 120)),
            )
            for tag in random.sample(tags_list, random.randint(1, 4)):
                article.tags.add(tag)
        
        # ============================================
        # 6. CREATE COMMENTS
        # ============================================
        self.stdout.write('💬 Creating comments...')
        
        articles = Article.objects.filter(status='published')
        users = User.objects.all()
        
        for article in articles:
            num_comments = random.randint(0, 20)
            for i in range(num_comments):
                user = random.choice(users)
                Comment.objects.create(
                    article=article,
                    user=user,
                    content=fake.paragraph(nb_sentences=3),
                    status=random.choice(['approved', 'pending', 'spam']),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                )
        
        # ============================================
        # 7. CREATE ADVERTISEMENTS
        # ============================================
        self.stdout.write('📢 Creating advertisements...')
        
        advertisers = User.objects.filter(role='advertiser')
        
        ad_positions = ['header', 'sidebar', 'footer', 'in_article', 'popup']
        
        for i in range(20):
            advertiser = random.choice(advertisers) if advertisers.exists() else User.objects.first()
            ad = Advertisement.objects.create(
                advertiser=advertiser,
                title=fake.company() + ' - Ad ' + str(i+1),
                description=fake.paragraph(nb_sentences=3),
                link_url=fake.url(),
                position=random.choice(ad_positions),
                status=random.choice(['active', 'pending', 'expired', 'paused']),
                views_count=random.randint(0, 10000),
                clicks_count=random.randint(0, 500),
                budget=random.randint(100, 5000),
                cost_per_click=random.uniform(0.5, 5.0),
                cost_per_impression=random.uniform(0.01, 0.5),
                start_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(1, 90)),
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
        
        # ============================================
        # 8. CREATE SUBSCRIBERS
        # ============================================
        self.stdout.write('📧 Creating subscribers...')
        
        for i in range(30):
            Subscriber.objects.get_or_create(
                email=fake.email(),
                defaults={
                    'name': fake.name(),
                    'status': random.choice(['active', 'inactive']),
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 180)),
                }
            )
        
        # ============================================
        # 9. CREATE NEWSLETTERS
        # ============================================
        self.stdout.write('📰 Creating newsletters...')
        
        for i in range(5):
            Newsletter.objects.create(
                subject=fake.sentence(nb_words=5),
                content=fake.paragraph(nb_sentences=10),
                status=random.choice(['draft', 'sent', 'scheduled']),
                created_by=User.objects.filter(role='admin').first(),
                sent_at=timezone.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
        
        # ============================================
        # 10. CREATE CONTACT MESSAGES
        # ============================================
        self.stdout.write('📩 Creating contact messages...')
        
        for i in range(20):
            ContactMessage.objects.create(
                name=fake.name(),
                email=fake.email(),
                subject=fake.sentence(nb_words=4),
                message=fake.paragraph(nb_sentences=5),
                status=random.choice(['new', 'read', 'replied', 'spam']),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
            )
        
        # ============================================
        # 11. CREATE MEDIA FILES (FIXED - with required fields)
        # ============================================
        self.stdout.write('🖼️ Creating media files...')
        
        uploaders = User.objects.all()
        
        # Create 30 image files
        for i in range(30):
            try:
                MediaFile.objects.create(
                    title=f'Image {i+1} - {fake.word()}',
                    description=fake.sentence(nb_words=5),
                    file_type='image',
                    uploaded_by=random.choice(uploaders),
                    file_size=random.randint(100000, 5000000),  # 100KB to 5MB
                    width=random.randint(800, 1920),
                    height=random.randint(600, 1080),
                    mime_type=random.choice(['image/jpeg', 'image/png', 'image/webp']),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                )
            except Exception as e:
                # Skip if there's an error with specific fields
                self.stdout.write(f'   ⚠️ Skipped image {i+1}: {str(e)[:50]}')
        
        # Create 10 video files
        for i in range(10):
            try:
                MediaFile.objects.create(
                    title=f'Video {i+1} - {fake.word()}',
                    description=fake.sentence(nb_words=5),
                    file_type='video',
                    uploaded_by=random.choice(uploaders),
                    file_size=random.randint(10000000, 100000000),  # 10MB to 100MB
                    width=random.randint(1280, 3840),
                    height=random.randint(720, 2160),
                    duration=random.randint(30, 600),
                    mime_type=random.choice(['video/mp4', 'video/webm', 'video/quicktime']),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                )
            except Exception as e:
                self.stdout.write(f'   ⚠️ Skipped video {i+1}: {str(e)[:50]}')
        
        # ============================================
        # 12. CREATE USER ACTIVITY LOGS
        # ============================================
        self.stdout.write('📋 Creating activity logs...')
        
        actions = ['create', 'update', 'delete', 'login', 'view']
        
        for i in range(100):
            user = random.choice(users)
            UserActivityLog.objects.create(
                user=user,
                action=random.choice(actions),
                model_name=random.choice(['Article', 'Comment', 'Advertisement', 'User', 'Category']),
                description=fake.sentence(nb_words=6),
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30)),
                ip_address=fake.ipv4(),
            )
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
        self.stdout.write(f'📊 Summary:')
        self.stdout.write(f'   Users: {User.objects.count()}')
        self.stdout.write(f'   Articles: {Article.objects.count()}')
        self.stdout.write(f'   Categories: {Category.objects.count()}')
        self.stdout.write(f'   Tags: {Tag.objects.count()}')
        self.stdout.write(f'   Comments: {Comment.objects.count()}')
        self.stdout.write(f'   Advertisements: {Advertisement.objects.count()}')
        self.stdout.write(f'   Subscribers: {Subscriber.objects.count()}')
        self.stdout.write(f'   Newsletters: {Newsletter.objects.count()}')
        self.stdout.write(f'   Contact Messages: {ContactMessage.objects.count()}')
        self.stdout.write(f'   Media Files: {MediaFile.objects.count()}')
        self.stdout.write(f'   Activity Logs: {UserActivityLog.objects.count()}')