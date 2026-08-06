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
            ('general', 'site_tagline', 'Informing Society · Empowering Business'),
            ('general', 'site_description', 'Official Publication of Egerton Green Movement Network (EGMN)'),
            ('general', 'site_timezone', 'Africa/Nairobi'),
            ('general', 'site_language', 'en'),
            ('email', 'smtp_host', 'smtp.gmail.com'),
            ('email', 'smtp_port', '587'),
            ('email', 'smtp_username', 'theegertonadvertiser@gmail.com'),
            ('email', 'use_tls', 'True'),
            ('email', 'from_email', 'theegertonadvertiser@gmail.com'),
            ('email', 'from_name', 'The Egerton Advertiser'),
            ('seo', 'meta_title', 'The Egerton Advertiser - Informing Society · Empowering Business'),
            ('seo', 'meta_description', 'Official Publication of Egerton Green Movement Network (EGMN) covering environment, society, business, and sustainable development in Kenya.'),
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
        # 2. CREATE CATEGORIES - ALL NAVIGATION SECTIONS
        # ============================================
        self.stdout.write('📂 Creating categories...')
        
        categories = [
            # Main Navigation Categories
            {'name': 'Community & National News', 'slug': 'community-national', 'description': 'Community and national news coverage', 'is_active': True, 'icon': 'fa-newspaper'},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental news, climate action, and conservation', 'is_active': True, 'icon': 'fa-leaf'},
            {'name': 'Education & Research', 'slug': 'education', 'description': 'Education news, research, and academic developments', 'is_active': True, 'icon': 'fa-graduation-cap'},
            {'name': 'Agriculture', 'slug': 'agriculture', 'description': 'Agricultural news, farming, and food security', 'is_active': True, 'icon': 'fa-tractor'},
            {'name': 'Health', 'slug': 'health', 'description': 'Health news, wellness, and healthcare', 'is_active': True, 'icon': 'fa-heartbeat'},
            {'name': 'Business & Directory', 'slug': 'business', 'description': 'Business news, economy, and directory', 'is_active': True, 'icon': 'fa-building'},
            
            # More Dropdown Categories
            {'name': 'Photos', 'slug': 'photos', 'description': 'Photo galleries and visual stories', 'is_active': True, 'icon': 'fa-images'},
            {'name': 'Opinion', 'slug': 'opinion', 'description': 'Opinion pieces, editorials, and commentary', 'is_active': True, 'icon': 'fa-pen-fancy'},
            {'name': 'Technology', 'slug': 'technology', 'description': 'Technology news, innovation, and digital trends', 'is_active': True, 'icon': 'fa-microchip'},
            {'name': 'Society', 'slug': 'society', 'description': 'Society news, community, and social issues', 'is_active': True, 'icon': 'fa-users'},
            {'name': 'Careers', 'slug': 'careers', 'description': 'Career news, job opportunities, and employment', 'is_active': True, 'icon': 'fa-briefcase'},
            {'name': 'Arts & Culture', 'slug': 'arts-culture', 'description': 'Arts, culture, music, literature, and creative expressions', 'is_active': True, 'icon': 'fa-palette'},
            {'name': 'Videos', 'slug': 'videos', 'description': 'Video content and multimedia stories', 'is_active': True, 'icon': 'fa-video'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'   ✅ Created category: {category.name}')
            else:
                self.stdout.write(f'   ⚠️ Category already exists: {category.name}')
        
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
            {'name': 'National', 'slug': 'national', 'is_active': True},
            {'name': 'Business', 'slug': 'business-tag', 'is_active': True},
            {'name': 'Economy', 'slug': 'economy', 'is_active': True},
            {'name': 'Health', 'slug': 'health-tag', 'is_active': True},
            {'name': 'Education', 'slug': 'education-tag', 'is_active': True},
            {'name': 'Agriculture', 'slug': 'agriculture-tag', 'is_active': True},
            {'name': 'Technology', 'slug': 'technology-tag', 'is_active': True},
            {'name': 'Innovation', 'slug': 'innovation', 'is_active': True},
            {'name': 'Arts', 'slug': 'arts-tag', 'is_active': True},
            {'name': 'Culture', 'slug': 'culture-tag', 'is_active': True},
            {'name': 'Careers', 'slug': 'careers-tag', 'is_active': True},
            {'name': 'Employment', 'slug': 'employment', 'is_active': True},
            {'name': 'Sustainability', 'slug': 'sustainability', 'is_active': True},
            {'name': 'Politics', 'slug': 'politics-tag', 'is_active': True},
            {'name': 'Society', 'slug': 'society-tag', 'is_active': True},
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
            if created:
                self.stdout.write(f'   ✅ Created user: {user.username}')
        
        # Create 30 random users
        self.stdout.write('👤 Creating 30 random users...')
        for i in range(30):
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
        # 5. CREATE ARTICLES - ALL SECTIONS
        # ============================================
        self.stdout.write('📰 Creating articles...')
        
        categories = Category.objects.all()
        tags = Tag.objects.all()
        authors = User.objects.filter(role__in=['admin', 'editor', 'journalist'])
        
        # Get categories for each section
        community_cat = Category.objects.get(slug='community-national')
        environment_cat = Category.objects.get(slug='environment')
        education_cat = Category.objects.get(slug='education')
        agriculture_cat = Category.objects.get(slug='agriculture')
        health_cat = Category.objects.get(slug='health')
        business_cat = Category.objects.get(slug='business')
        opinion_cat = Category.objects.get(slug='opinion')
        technology_cat = Category.objects.get(slug='technology')
        society_cat = Category.objects.get(slug='society')
        careers_cat = Category.objects.get(slug='careers')
        arts_cat = Category.objects.get(slug='arts-culture')
        
        articles_data = [
            # Community & National News Articles
            {
                'title': 'Community Leaders Unite for Development',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'Local leaders come together for community development initiatives',
                'category': community_cat,
                'is_featured': True,
                'is_breaking': True,
                'views_count': random.randint(100, 5000),
            },
            {
                'title': 'National Dialogue on Economic Growth',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'National stakeholders discuss economic development strategies',
                'category': community_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(50, 3000),
            },
            {
                'title': 'Community Health Initiative Launched',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'New community health program aims to improve healthcare access',
                'category': community_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(30, 2000),
            },
            
            # Environment Articles
            {
                'title': 'Kenya\'s Great Green Wall Initiative',
                'content': fake.paragraph(nb_sentences=35),
                'excerpt': 'Massive reforestation project transforming landscapes',
                'category': environment_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(100, 4000),
            },
            {
                'title': 'Plastic Pollution Crisis in Nairobi',
                'content': fake.paragraph(nb_sentences=28),
                'excerpt': 'Growing plastic waste problem demands urgent action',
                'category': environment_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(50, 2500),
            },
            {
                'title': 'Conservation Success in Maasai Mara',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'Wildlife conservation achievements celebrated',
                'category': environment_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(80, 3500),
            },
            
            # Education Articles
            {
                'title': 'Education Reform: New Curriculum Rollout',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Major education reforms taking shape in schools',
                'category': education_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(40, 1800),
            },
            {
                'title': 'University Research Breakthrough',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'Kenyan researchers make significant discovery',
                'category': education_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(30, 1500),
            },
            
            # Agriculture Articles
            {
                'title': 'Sustainable Farming Practices Transform Agriculture',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Farmers adopt sustainable practices for better yields',
                'category': agriculture_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(60, 2800),
            },
            {
                'title': 'Food Security: New Initiatives Launched',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'Government announces food security programs',
                'category': agriculture_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(30, 1500),
            },
            
            # Health Articles
            {
                'title': 'Healthcare Access in Rural Communities',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'Challenges and solutions in rural healthcare delivery',
                'category': health_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(60, 2800),
            },
            {
                'title': 'New Health Initiative Launched',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Community health program aims to improve outcomes',
                'category': health_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(30, 1500),
            },
            
            # Business Articles
            {
                'title': 'Small Business Growth in Egerton',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Local businesses thrive in growing economy',
                'category': business_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(40, 2000),
            },
            {
                'title': 'Business Directory: Top Companies in Egerton',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'Comprehensive directory of local businesses',
                'category': business_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(20, 1000),
            },
            
            # Opinion Articles
            {
                'title': 'The Future of Democracy in Kenya',
                'content': fake.paragraph(nb_sentences=30),
                'excerpt': 'A deep dive into the democratic future of Kenya',
                'category': opinion_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(100, 5000),
            },
            {
                'title': 'Why Climate Action Cannot Wait',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Urgent action needed on climate change',
                'category': opinion_cat,
                'is_featured': False,
                'is_breaking': True,
                'views_count': random.randint(50, 3000),
            },
            
            # Technology Articles
            {
                'title': 'Tech Innovation Hub Opens in Egerton',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'New technology innovation center launched',
                'category': technology_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(20, 1000),
            },
            
            # Society Articles
            {
                'title': 'Youth Unemployment and Solutions',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Addressing youth unemployment crisis in Kenya',
                'category': society_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(30, 1500),
            },
            
            # Careers Articles
            {
                'title': 'Career Opportunities in Green Economy',
                'content': fake.paragraph(nb_sentences=20),
                'excerpt': 'Growing career opportunities in sustainable sectors',
                'category': careers_cat,
                'is_featured': False,
                'is_breaking': False,
                'views_count': random.randint(20, 1000),
            },
            
            # Arts & Culture Articles
            {
                'title': 'Cultural Festival Celebrates Kenyan Heritage',
                'content': fake.paragraph(nb_sentences=25),
                'excerpt': 'Annual cultural festival showcases local talent',
                'category': arts_cat,
                'is_featured': True,
                'is_breaking': False,
                'views_count': random.randint(30, 1500),
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
                status='published',
                is_featured=article_data.get('is_featured', False),
                is_breaking=article_data.get('is_breaking', False),
                views_count=article_data.get('views_count', 0),
                published_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
            
            # Add random tags
            for tag in random.sample(list(tags), random.randint(2, 5)):
                article.tags.add(tag)
        
        # Create 30 more random articles
        self.stdout.write('📰 Creating 30 random articles...')
        categories_list = list(Category.objects.all())
        tags_list = list(Tag.objects.all())
        
        for i in range(30):
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
        if not advertisers.exists():
            advertisers = User.objects.filter(role='admin')
        
        ad_positions = ['header', 'sidebar', 'footer', 'in_article', 'popup']
        ad_titles = [
            'Reyes, Olson and Garcia - Ad 15',
            'Thomas LLC - Ad 13',
            'Thomas, Smith and Cook - Ad 6',
            'Manning Ltd - Ad 5',
            'Parker Group - Ad 2',
            'Pineda-Brown - Ad 1',
            'Jefferson, Fernandez and Barr - Ad 16',
            'Harper-Davis - Ad 5',
            'Cline, Wise and Parsons - Ad 2',
            'Roberts-Thomas - Ad 1',
        ]
        
        for i in range(20):
            advertiser = random.choice(advertisers) if advertisers.exists() else User.objects.first()
            title = ad_titles[i % len(ad_titles)] if i < len(ad_titles) else fake.company() + ' - Ad ' + str(i+1)
            ad = Advertisement.objects.create(
                advertiser=advertiser,
                title=title,
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
        
        admin_user = User.objects.filter(role='admin').first()
        
        for i in range(5):
            Newsletter.objects.create(
                subject=fake.sentence(nb_words=5),
                content=fake.paragraph(nb_sentences=10),
                status=random.choice(['draft', 'sent', 'scheduled']),
                created_by=admin_user,
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
        # 11. CREATE MEDIA FILES
        # ============================================
        self.stdout.write('🖼️ Creating media files...')
        
        uploaders = User.objects.all()
        
        image_titles = [
            'Image 30 - not', 'Image 29 - face', 'Image 28 - indeed', 
            'Image 27 - under', 'Image 26 - design', 'Image 25 - action',
            'Image 24 - produce', 'Image 23 - along', 'Image 22 - every',
            'Image 21 - work', 'Image 20 - create', 'Image 19 - nature',
            'Image 18 - people', 'Image 17 - building', 'Image 16 - landscape',
            'Image 15 - animal', 'Image 14 - plant', 'Image 13 - water',
            'Image 12 - mountain', 'Image 11 - river', 'Image 10 - forest',
            'Image 9 - flower', 'Image 8 - ocean', 'Image 7 - city',
            'Image 6 - village', 'Image 5 - market', 'Image 4 - school',
            'Image 3 - hospital', 'Image 2 - road', 'Image 1 - tree',
        ]
        
        for i in range(30):
            try:
                MediaFile.objects.create(
                    title=image_titles[i % len(image_titles)] if i < len(image_titles) else f'Image {i+1} - {fake.word()}',
                    description=fake.sentence(nb_words=5),
                    file_type='image',
                    uploaded_by=random.choice(uploaders),
                    file_size=random.randint(100000, 5000000),
                    width=random.randint(800, 1920),
                    height=random.randint(600, 1080),
                    mime_type=random.choice(['image/jpeg', 'image/png', 'image/webp']),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                    status='available',
                )
            except Exception as e:
                self.stdout.write(f'   ⚠️ Skipped image {i+1}: {str(e)[:50]}')
        
        # Create 10 video files
        video_titles = [
            'Video 10 - president', 'Video 9 - notice', 'Video 8 - central',
            'Video 7 - section', 'Video 6 - occur', 'Video 5 - truth',
            'Video 4 - window', 'Video 3 - life', 'Video 2 - which',
            'Video 1 - style',
        ]
        
        for i in range(10):
            try:
                MediaFile.objects.create(
                    title=video_titles[i % len(video_titles)] if i < len(video_titles) else f'Video {i+1} - {fake.word()}',
                    description=fake.sentence(nb_words=5),
                    file_type='video',
                    uploaded_by=random.choice(uploaders),
                    file_size=random.randint(10000000, 100000000),
                    width=random.randint(1280, 3840),
                    height=random.randint(720, 2160),
                    duration=random.randint(30, 600),
                    mime_type=random.choice(['video/mp4', 'video/webm', 'video/quicktime']),
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                    status='available',
                )
            except Exception as e:
                self.stdout.write(f'   ⚠️ Skipped video {i+1}: {str(e)[:50]}')
        
        # ============================================
        # 12. CREATE USER ACTIVITY LOGS
        # ============================================
        self.stdout.write('📋 Creating activity logs...')
        
        actions = ['create', 'update', 'delete', 'login', 'view', 'publish', 'approve', 'reject']
        
        for i in range(100):
            user = random.choice(users)
            UserActivityLog.objects.create(
                user=user,
                action=random.choice(actions),
                model_name=random.choice(['Article', 'Comment', 'Advertisement', 'User', 'Category', 'MediaFile']),
                description=fake.sentence(nb_words=6),
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30)),
                ip_address=fake.ipv4(),
            )
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
        self.stdout.write('📊 Summary:')
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
        
        self.stdout.write('\n📂 Categories Created:')
        for cat in Category.objects.all().order_by('name'):
            article_count = Article.objects.filter(category=cat).count()
            self.stdout.write(f'   ✅ {cat.name} (slug: {cat.slug}) - {article_count} articles')