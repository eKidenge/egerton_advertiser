#!/usr/bin/env bash
set -o errexit

echo "=================================================="
echo "  THE EGERTON ADVERTISER - BUILD SCRIPT"
echo "=================================================="

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 1. Apply database migrations
echo ""
echo "🗄️  Applying database migrations..."
python manage.py migrate

# 2. Load initial data (optional)
# if [ -f "load_data.py" ]; then
#     echo "📥 Loading initial data..."
#     python load_data.py
# fi

# 3. Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# 4. Create superuser and demo users
echo ""
echo "👤 Creating users..."

python manage.py shell << EOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'egerton_advertiser.settings')

from django.contrib.auth import get_user_model
from apps.accounts.models import User, UserProfile

User = get_user_model()

# ============================================
# CREATE SUPERUSER (ADMIN)
# ============================================
print("\nCreating Superuser...")

# Remove existing admin if present
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

# Create profile for admin
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
echo "  🚀 Visit your site at: http://localhost:8000/"
echo "  🔑 Admin Login: http://localhost:8000/admin/"
echo "  📊 Admin Dashboard: http://localhost:8000/dashboard/admin/"
echo "  👤 User Login: http://localhost:8000/accounts/login/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"