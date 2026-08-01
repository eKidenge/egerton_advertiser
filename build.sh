#!/usr/bin/env bash
set -o errexit

echo "=================================================="
echo "  THE EGERTON ADVERTISER - BUILD SCRIPT"
echo "=================================================="

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ============================================
# FIX: Drop all tables and start fresh
# ============================================
echo ""
echo "🗄️  Resetting database completely..."

# Drop all tables
python manage.py flush --noinput || true

# Fake all migrations to zero
echo "Faking all migrations to zero..."
python manage.py migrate --fake analytics zero || true
python manage.py migrate --fake articles zero || true
python manage.py migrate --fake accounts zero || true
python manage.py migrate --fake categories zero || true
python manage.py migrate --fake tags zero || true
python manage.py migrate --fake comments zero || true
python manage.py migrate --fake advertisements zero || true
python manage.py migrate --fake media_library zero || true
python manage.py migrate --fake newsletter zero || true
python manage.py migrate --fake contacts zero || true
python manage.py migrate --fake search zero || true
python manage.py migrate --fake notifications zero || true
python manage.py migrate --fake dashboard zero || true
python manage.py migrate --fake settings_manager zero || true

# Delete existing tables if they exist
echo "Dropping existing tables..."
python manage.py dbshell << SQL
DROP TABLE IF EXISTS articles CASCADE;
DROP TABLE IF EXISTS analytics CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS advertisements CASCADE;
DROP TABLE IF EXISTS media_library CASCADE;
DROP TABLE IF EXISTS newsletter CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS search CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS dashboard CASCADE;
DROP TABLE IF EXISTS settings_manager CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
SQL

# Now run migrations fresh
echo ""
echo "🗄️  Applying fresh migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create users
echo ""
echo "👤 Creating users..."

python manage.py shell << EOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'egerton_advertiser.settings')

from django.contrib.auth import get_user_model
from apps.accounts.models import User, UserProfile

User = get_user_model()

print("\nCreating Superuser...")
User.objects.filter(username='admin').delete()

admin = User.objects.create_superuser(
    username='admin',
    email='admin@theegertonadvertiser.com',
    password='Admin@123!',
    first_name='System',
    last_name='Admin',
    role='super_admin',
    is_verified=True,
    is_active=True
)
UserProfile.objects.get_or_create(user=admin)
print("✅ Superuser created (admin/Admin@123!)")

print("\nCreating Editor...")
User.objects.filter(username='editor').delete()
editor = User.objects.create_user(
    username='editor',
    email='editor@theegertonadvertiser.com',
    password='Editor@123',
    first_name='Editor',
    last_name='User',
    role='editor',
    is_verified=True,
    is_active=True,
    department='editorial'
)
UserProfile.objects.get_or_create(user=editor)
print("✅ Editor created (editor/Editor@123)")

print("\nCreating Journalist...")
User.objects.filter(username='journalist').delete()
journalist = User.objects.create_user(
    username='journalist',
    email='journalist@theegertonadvertiser.com',
    password='Journalist@123',
    first_name='Journalist',
    last_name='User',
    role='journalist',
    is_verified=True,
    is_active=True,
    department='news'
)
UserProfile.objects.get_or_create(user=journalist)
print("✅ Journalist created (journalist/Journalist@123)")

print("\nCreating Advertiser...")
User.objects.filter(username='advertiser').delete()
advertiser = User.objects.create_user(
    username='advertiser',
    email='advertiser@theegertonadvertiser.com',
    password='Advertiser@123',
    first_name='Advertiser',
    last_name='User',
    role='advertiser',
    is_verified=True,
    is_active=True,
    department='advertising'
)
UserProfile.objects.get_or_create(user=advertiser)
print("✅ Advertiser created (advertiser/Advertiser@123)")

print("\nCreating Subscriber...")
User.objects.filter(username='subscriber').delete()
subscriber = User.objects.create_user(
    username='subscriber',
    email='subscriber@theegertonadvertiser.com',
    password='Subscriber@123',
    first_name='Subscriber',
    last_name='User',
    role='subscriber',
    is_verified=True,
    is_active=True
)
UserProfile.objects.get_or_create(user=subscriber)
print("✅ Subscriber created (subscriber/Subscriber@123)")

print("\n" + "="*50)
print("  USER SUMMARY")
print("="*50)
print("")
print("🔑 ADMIN: admin / Admin@123!")
print("📝 EDITOR: editor / Editor@123")
print("✍️  JOURNALIST: journalist / Journalist@123")
print("📢 ADVERTISER: advertiser / Advertiser@123")
print("👤 SUBSCRIBER: subscriber / Subscriber@123")
print("")
print("="*50)
EOF

echo ""
echo "✅ The Egerton Advertiser build completed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Visit your site at: https://egerton-advertiser.onrender.com"
echo "  🔑 Admin Login: https://egerton-advertiser.onrender.com/admin/"
echo "  📊 Admin Dashboard: https://egerton-advertiser.onrender.com/dashboard/admin/"
echo "  👤 User Login: https://egerton-advertiser.onrender.com/accounts/login/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"