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
# CREATE STATIC DIRECTORIES
# ============================================
echo ""
echo "📁 Creating static directories..."
mkdir -p apps/accounts/static
mkdir -p apps/articles/static
mkdir -p apps/dashboard/static

# ============================================
# FIX: Drop all tables and start fresh (SQLite compatible)
# ============================================
echo ""
echo "🗄️  Resetting database completely..."

# Delete the SQLite database file
echo "Deleting existing database..."
rm -f db.sqlite3

# Now run migrations fresh
echo ""
echo "🗄️  Applying fresh migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# ============================================
# CREATE SUPERUSER AND DEMO USERS
# ============================================
echo ""
echo "👤 Creating users..."

python manage.py shell << EOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'egerton_advertiser.settings')

from django.contrib.auth import get_user_model
from apps.accounts.models import User, UserProfile

User = get_user_model()

print("\n" + "="*50)
print("  CREATING USERS")
print("="*50)

# ============================================
# CREATE SUPERUSER (ADMIN)
# ============================================
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
print("✅ Superuser created successfully!")
print("   Username: admin")
print("   Email: admin@theegertonadvertiser.com")
print("   Password: Admin@123!")

# ============================================
# CREATE EDITOR USER
# ============================================
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
print("✅ Editor created successfully!")
print("   Username: editor")
print("   Email: editor@theegertonadvertiser.com")
print("   Password: Editor@123")

# ============================================
# CREATE JOURNALIST USER
# ============================================
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
print("✅ Journalist created successfully!")
print("   Username: journalist")
print("   Email: journalist@theegertonadvertiser.com")
print("   Password: Journalist@123")

# ============================================
# CREATE ADVERTISER USER
# ============================================
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
print("✅ Advertiser created successfully!")
print("   Username: advertiser")
print("   Email: advertiser@theegertonadvertiser.com")
print("   Password: Advertiser@123")

# ============================================
# CREATE SUBSCRIBER USER
# ============================================
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
print("✅ Subscriber created successfully!")
print("   Username: subscriber")
print("   Email: subscriber@theegertonadvertiser.com")
print("   Password: Subscriber@123")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*50)
print("  USER SUMMARY")
print("="*50)
print("")
print("🔑 ADMIN (Full System Access)")
print("   Username: admin")
print("   Password: Admin@123!")
print("")
print("📝 EDITOR (Content Management)")
print("   Username: editor")
print("   Password: Editor@123")
print("")
print("✍️  JOURNALIST (Article Writing)")
print("   Username: journalist")
print("   Password: Journalist@123")
print("")
print("📢 ADVERTISER (Ad Management)")
print("   Username: advertiser")
print("   Password: Advertiser@123")
print("")
print("👤 SUBSCRIBER (Content Reader)")
print("   Username: subscriber")
print("   Password: Subscriber@123")
print("")
print("="*50)
print("  BUILD COMPLETED SUCCESSFULLY!")
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