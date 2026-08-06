#!/usr/bin/env python
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.settings_manager.models import SiteSetting
from apps.media_library.models import MediaCategory  # Add this import

User = get_user_model()

class Command(BaseCommand):
    help = 'Clean database setup for client - Only categories, tags, settings, and essential users'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Setting up clean client database...')
        
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
        # 2. CREATE ARTICLE CATEGORIES - ALL NAVIGATION SECTIONS
        # ============================================
        self.stdout.write('📂 Creating article categories...')
        
        categories = [
            # Main Navigation Categories
            {'name': 'Community & National News', 'slug': 'community-national', 'description': 'Community and national news coverage', 'is_active': True},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental news, climate action, and conservation', 'is_active': True},
            {'name': 'Education & Research', 'slug': 'education', 'description': 'Education news, research, and academic developments', 'is_active': True},
            {'name': 'Agriculture', 'slug': 'agriculture', 'description': 'Agricultural news, farming, and food security', 'is_active': True},
            {'name': 'Health', 'slug': 'health', 'description': 'Health news, wellness, and healthcare', 'is_active': True},
            {'name': 'Business & Directory', 'slug': 'business', 'description': 'Business news, economy, and directory', 'is_active': True},
            
            # More Dropdown Categories
            {'name': 'Photos', 'slug': 'photos', 'description': 'Photo galleries and visual stories', 'is_active': True},
            {'name': 'Opinion', 'slug': 'opinion', 'description': 'Opinion pieces, editorials, and commentary', 'is_active': True},
            {'name': 'Technology', 'slug': 'technology', 'description': 'Technology news, innovation, and digital trends', 'is_active': True},
            {'name': 'Society', 'slug': 'society', 'description': 'Society news, community, and social issues', 'is_active': True},
            {'name': 'Careers', 'slug': 'careers', 'description': 'Career news, job opportunities, and employment', 'is_active': True},
            {'name': 'Arts & Culture', 'slug': 'arts-culture', 'description': 'Arts, culture, music, literature, and creative expressions', 'is_active': True},
            {'name': 'Videos', 'slug': 'videos', 'description': 'Video content and multimedia stories', 'is_active': True},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'   ✅ Created article category: {category.name}')
            else:
                self.stdout.write(f'   ⚠️ Article category already exists: {category.name}')
        
        # ============================================
        # 3. CREATE MEDIA LIBRARY CATEGORIES
        # ============================================
        self.stdout.write('📸 Creating media library categories...')
        
        media_categories = [
            {'name': 'Events', 'slug': 'events', 'description': 'Event photography and media coverage', 'parent': None},
            {'name': 'News', 'slug': 'news', 'description': 'News coverage and journalism', 'parent': None},
            {'name': 'Sports', 'slug': 'sports', 'description': 'Sports events and activities', 'parent': None},
            {'name': 'Education', 'slug': 'education', 'description': 'Educational content and programs', 'parent': None},
            {'name': 'Agriculture', 'slug': 'agriculture', 'description': 'Farming and agricultural content', 'parent': None},
            {'name': 'Technology', 'slug': 'technology', 'description': 'Technology and innovation', 'parent': None},
            {'name': 'Community', 'slug': 'community', 'description': 'Community events and stories', 'parent': None},
            {'name': 'Business', 'slug': 'business', 'description': 'Business and economic news', 'parent': None},
            {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness content', 'parent': None},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental and sustainability', 'parent': None},
            {'name': 'Politics', 'slug': 'politics', 'description': 'Political news and events', 'parent': None},
            {'name': 'Entertainment', 'slug': 'entertainment', 'description': 'Entertainment and culture', 'parent': None},
        ]
        
        for cat_data in media_categories:
            category, created = MediaCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'   ✅ Created media category: {category.name}')
            else:
                self.stdout.write(f'   ⚠️ Media category already exists: {category.name}')
        
        # ============================================
        # 4. CREATE MEDIA CATEGORY HIERARCHY (Optional Sub-Categories)
        # ============================================
        self.stdout.write('📸 Creating media sub-categories...')
        
        sub_categories = [
            {'name': 'Local News', 'slug': 'local-news', 'description': 'Local news and community stories', 'parent_slug': 'news'},
            {'name': 'International News', 'slug': 'international-news', 'description': 'International news coverage', 'parent_slug': 'news'},
            {'name': 'Business News', 'slug': 'business-news', 'description': 'Business and economic news', 'parent_slug': 'news'},
            {'name': 'Football', 'slug': 'football', 'description': 'Football matches and events', 'parent_slug': 'sports'},
            {'name': 'Basketball', 'slug': 'basketball', 'description': 'Basketball games and tournaments', 'parent_slug': 'sports'},
            {'name': 'Crop Farming', 'slug': 'crop-farming', 'description': 'Crop farming and agricultural practices', 'parent_slug': 'agriculture'},
            {'name': 'Livestock', 'slug': 'livestock', 'description': 'Livestock farming and animal husbandry', 'parent_slug': 'agriculture'},
            {'name': 'Artificial Intelligence', 'slug': 'ai', 'description': 'AI technology and applications', 'parent_slug': 'technology'},
            {'name': 'Web Development', 'slug': 'web-dev', 'description': 'Web development and design', 'parent_slug': 'technology'},
            {'name': 'Mobile Apps', 'slug': 'mobile-apps', 'description': 'Mobile application development', 'parent_slug': 'technology'},
            {'name': 'Climate Action', 'slug': 'climate-action', 'description': 'Climate change and environmental action', 'parent_slug': 'environment'},
            {'name': 'Conservation', 'slug': 'conservation', 'description': 'Wildlife and nature conservation', 'parent_slug': 'environment'},
        ]
        
        for cat_data in sub_categories:
            try:
                parent = MediaCategory.objects.get(slug=cat_data['parent_slug'])
                category, created = MediaCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults={
                        'name': cat_data['name'],
                        'description': cat_data['description'],
                        'parent': parent
                    }
                )
                if created:
                    self.stdout.write(f'   ✅ Created media sub-category: {category.name} (parent: {parent.name})')
                else:
                    self.stdout.write(f'   ⚠️ Media sub-category already exists: {category.name}')
            except MediaCategory.DoesNotExist:
                self.stdout.write(f'   ❌ Parent category not found for: {cat_data["name"]} (parent: {cat_data["parent_slug"]})')
        
        # ============================================
        # 5. CREATE TAGS
        # ============================================
        self.stdout.write('🏷️ Creating tags...')
        
        tags = [
            {'name': 'Breaking News', 'slug': 'breaking-news', 'is_active': True},
            {'name': 'Featured', 'slug': 'featured', 'is_active': True},
            {'name': 'Opinion', 'slug': 'opinion-tag', 'is_active': True},
            {'name': 'Environment', 'slug': 'environment-tag', 'is_active': True},
            {'name': 'Community', 'slug': 'community', 'is_active': True},
            {'name': 'National', 'slug': 'national', 'is_active': True},
            {'name': 'Business', 'slug': 'business-tag', 'is_active': True},
            {'name': 'Health', 'slug': 'health-tag', 'is_active': True},
            {'name': 'Education', 'slug': 'education-tag', 'is_active': True},
            {'name': 'Agriculture', 'slug': 'agriculture-tag', 'is_active': True},
            {'name': 'Technology', 'slug': 'technology-tag', 'is_active': True},
            {'name': 'Innovation', 'slug': 'innovation', 'is_active': True},
            {'name': 'Arts', 'slug': 'arts-tag', 'is_active': True},
            {'name': 'Culture', 'slug': 'culture-tag', 'is_active': True},
            {'name': 'Careers', 'slug': 'careers-tag', 'is_active': True},
            {'name': 'Sustainability', 'slug': 'sustainability', 'is_active': True},
            {'name': 'Society', 'slug': 'society-tag', 'is_active': True},
        ]
        
        for tag_data in tags:
            Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
        
        # ============================================
        # 6. CREATE ESSENTIAL USERS
        # ============================================
        self.stdout.write('👤 Creating essential users...')
        
        users_data = [
            # Super Admin
            {
                'username': 'admin',
                'email': 'admin@theegertonadvertiser.com',
                'first_name': 'John',
                'last_name': 'Admin',
                'role': 'super_admin',
                'is_active': True,
                'is_verified': True,
                'is_superuser': True,
                'is_staff': True,
                'password': 'Admin@123!'
            },
            # Admin
            {
                'username': 'adminuser',
                'email': 'adminuser@theegertonadvertiser.com',
                'first_name': 'Jane',
                'last_name': 'Admin',
                'role': 'admin',
                'is_active': True,
                'is_verified': True,
                'is_superuser': False,
                'is_staff': True,
                'password': 'Admin@123!'
            },
            # Editor
            {
                'username': 'editor',
                'email': 'editor@theegertonadvertiser.com',
                'first_name': 'Sarah',
                'last_name': 'Editor',
                'role': 'editor',
                'is_active': True,
                'is_verified': True,
                'is_superuser': False,
                'is_staff': True,
                'password': 'Editor@123!'
            },
            # Journalist
            {
                'username': 'journalist',
                'email': 'journalist@theegertonadvertiser.com',
                'first_name': 'Michael',
                'last_name': 'Journalist',
                'role': 'journalist',
                'is_active': True,
                'is_verified': True,
                'is_superuser': False,
                'is_staff': False,
                'password': 'Journalist@123!'
            },
            # Subscriber
            {
                'username': 'subscriber',
                'email': 'subscriber@theegertonadvertiser.com',
                'first_name': 'Lucy',
                'last_name': 'Subscriber',
                'role': 'subscriber',
                'is_active': True,
                'is_verified': True,
                'is_superuser': False,
                'is_staff': False,
                'password': 'Subscriber@123!'
            },
            # Advertiser
            {
                'username': 'advertiser',
                'email': 'advertiser@theegertonadvertiser.com',
                'first_name': 'James',
                'last_name': 'Advertiser',
                'role': 'advertiser',
                'is_active': True,
                'is_verified': True,
                'is_superuser': False,
                'is_staff': False,
                'password': 'Advertiser@123!'
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
                    'is_superuser': user_data['is_superuser'],
                    'is_staff': user_data['is_staff'],
                    'password': make_password(user_data['password'])
                }
            )
            if created:
                self.stdout.write(f'   ✅ Created user: {user.username} (Password: {user_data["password"]})')
            else:
                self.stdout.write(f'   ⚠️ User already exists: {user.username}')
        
        # ============================================
        # SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS('\n🎉 Client database setup complete!'))
        self.stdout.write('=' * 60)
        self.stdout.write('📊 SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(f'   Article Categories: {Category.objects.count()}')
        self.stdout.write(f'   Media Categories: {MediaCategory.objects.count()}')
        self.stdout.write(f'   Tags: {Tag.objects.count()}')
        self.stdout.write(f'   Users: {User.objects.count()}')
        self.stdout.write(f'   Settings: {SiteSetting.objects.count()}')
        
        self.stdout.write('\n📂 ARTICLE CATEGORIES:')
        for cat in Category.objects.all().order_by('name'):
            self.stdout.write(f'   • {cat.name} (slug: {cat.slug})')
        
        self.stdout.write('\n📸 MEDIA CATEGORIES:')
        # Show parent categories
        for cat in MediaCategory.objects.filter(parent__isnull=True).order_by('name'):
            self.stdout.write(f'   • {cat.name} (slug: {cat.slug})')
            # Show sub-categories
            subcats = MediaCategory.objects.filter(parent=cat).order_by('name')
            for sub in subcats:
                self.stdout.write(f'      └─ {sub.name} (slug: {sub.slug})')
        
        self.stdout.write('\n👤 USERS CREATED:')
        self.stdout.write('   ' + '=' * 55)
        self.stdout.write('   | Username    | Role          | Password           |')
        self.stdout.write('   |-------------|---------------|--------------------|')
        self.stdout.write('   | admin       | Super Admin   | Admin@123!         |')
        self.stdout.write('   | adminuser   | Admin         | Admin@123!         |')
        self.stdout.write('   | editor      | Editor        | Editor@123!        |')
        self.stdout.write('   | journalist  | Journalist    | Journalist@123!    |')
        self.stdout.write('   | subscriber  | Subscriber    | Subscriber@123!    |')
        self.stdout.write('   | advertiser  | Advertiser    | Advertiser@123!    |')
        self.stdout.write('   ' + '=' * 55)
        
        self.stdout.write('\n🔑 SUPERUSER LOGIN:')
        self.stdout.write(f'   Username: admin')
        self.stdout.write(f'   Password: Admin@123!')
        self.stdout.write(f'   URL: http://localhost:8000/admin/')
        
        self.stdout.write('\n📸 MEDIA LIBRARY ACCESS:')
        self.stdout.write(f'   URL: http://localhost:8000/media-library/')
        self.stdout.write(f'   Login with any user account above')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Database is clean and ready for client use!'))
        self.stdout.write('   • No articles, comments, or other content created')
        self.stdout.write('   • All categories, tags, and settings are pre-configured')
        self.stdout.write('   • The client can start creating content immediately')
        self.stdout.write('=' * 60)