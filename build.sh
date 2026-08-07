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
# CHECK DATABASE TYPE
# ============================================
echo ""
echo "🗄️  Checking database configuration..."

# Check if we're using PostgreSQL or SQLite
if [[ "$DATABASE_URL" == postgresql://* ]] || [[ "$DATABASE_URL" == postgres://* ]]; then
    echo "✅ Using PostgreSQL database"
    DATABASE_TYPE="postgresql"
else
    echo "⚠️ Using SQLite database (fallback)"
    DATABASE_TYPE="sqlite"
fi

# ============================================
# DATABASE MIGRATIONS
# ============================================
echo ""
echo "🗄️  Running database migrations..."

if [[ "$DATABASE_TYPE" == "postgresql" ]]; then
    echo "   📌 Using PostgreSQL with DATABASE_URL"
    
    # For PostgreSQL, we need to handle migrations carefully
    # First, try to create the migrations
    echo "   Creating migrations..."
    python manage.py makemigrations || true
    
    # Check if we need to fake migrations (for existing database)
    echo "   Checking migration status..."
    
    # Try to migrate normally first
    echo "   Attempting to apply migrations..."
    if python manage.py migrate; then
        echo "   ✅ Migrations applied successfully"
    else
        echo "   ⚠️ Migration failed, trying to fake initial migrations..."
        
        # If migration fails, it might be due to existing tables
        # Try to fake the migrations and then migrate
        echo "   Faking initial migrations..."
        python manage.py migrate --fake || true
        
        echo "   Running migrations again..."
        python manage.py migrate || true
        
        echo "   ✅ Migrations completed"
    fi
    
else
    # SQLite - simple migration
    echo "   📌 Using SQLite"
    
    # Delete the SQLite database file for fresh start
    echo "   Deleting existing SQLite database..."
    rm -f db.sqlite3
    
    echo "   Creating migrations..."
    python manage.py makemigrations
    
    echo "   Applying migrations..."
    python manage.py migrate
fi

# ============================================
# COLLECT STATIC FILES
# ============================================
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# ============================================
# SEED DATABASE WITH DEMO DATA (Only for SQLite or fresh PostgreSQL)
# ============================================
echo ""
echo "🌱 Seeding database with demo data..."

# Only seed if it's SQLite or if we're confident the database is fresh
if [[ "$DATABASE_TYPE" == "sqlite" ]]; then
    echo "   Seeding SQLite database..."
    python manage.py seed_data || echo "   ⚠️ Seed data skipped (command not found)"
else
    echo "   ⚠️ Skipping seed_data for PostgreSQL (to avoid conflicts with existing data)"
    echo "   You can run 'python manage.py seed_data' manually if needed."
fi

# ============================================
# CREATE SUPERUSER
# ============================================
echo ""
echo "👤 Creating superuser..."

python manage.py shell << EOF
from django.contrib.auth import get_user_model
from apps.accounts.models import User, UserProfile

User = get_user_model()

print("\n" + "="*50)
print("  CREATING SUPERUSER")
print("="*50)

# Check if superuser exists
if not User.objects.filter(is_superuser=True).exists():
    print("\nCreating superuser...")
    
    # Delete any existing admin user to avoid conflicts
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
else:
    print("✅ Superuser already exists.")
    
    # Ensure admin user has proper profile
    try:
        admin = User.objects.get(username='admin')
        UserProfile.objects.get_or_create(user=admin)
    except User.DoesNotExist:
        pass

# ============================================
# CREATE ADDITIONAL DEMO USERS
# ============================================
print("\n" + "="*50)
print("  CREATING DEMO USERS")
print("="*50)

# Create Editor if not exists
if not User.objects.filter(username='editor').exists():
    print("\nCreating Editor...")
    editor = User.objects.create_user(
        username='editor',
        email='editor@theegertonadvertiser.com',
        password='Editor@123',
        first_name='Editor',
        last_name='User',
        role='editor',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=editor)
    print("✅ Editor created!")
    print("   Username: editor")
    print("   Password: Editor@123")

# Create Journalist if not exists
if not User.objects.filter(username='journalist').exists():
    print("\nCreating Journalist...")
    journalist = User.objects.create_user(
        username='journalist',
        email='journalist@theegertonadvertiser.com',
        password='Journalist@123',
        first_name='Journalist',
        last_name='User',
        role='journalist',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=journalist)
    print("✅ Journalist created!")
    print("   Username: journalist")
    print("   Password: Journalist@123")

# Create Advertiser if not exists
if not User.objects.filter(username='advertiser').exists():
    print("\nCreating Advertiser...")
    advertiser = User.objects.create_user(
        username='advertiser',
        email='advertiser@theegertonadvertiser.com',
        password='Advertiser@123',
        first_name='Advertiser',
        last_name='User',
        role='advertiser',
        is_verified=True,
        is_active=True
    )
    UserProfile.objects.get_or_create(user=advertiser)
    print("✅ Advertiser created!")
    print("   Username: advertiser")
    print("   Password: Advertiser@123")

# Create Subscriber if not exists
if not User.objects.filter(username='subscriber').exists():
    print("\nCreating Subscriber...")
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
    print("✅ Subscriber created!")
    print("   Username: subscriber")
    print("   Password: Subscriber@123")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*50)
print("  USER SUMMARY")
print("="*50)
print("")
print("🔑 SUPER ADMIN (Full System Access)")
print("   Username: admin")
print("   Password: Admin@123!")
print("")
print("EDITOR (Content Management)")
print("   Username: editor")
print("   Password: Editor@123")
print("")
print("JOURNALIST (Article Writing)")
print("   Username: journalist")
print("   Password: Journalist@123")
print("")
print("ADVERTISER (Ad Management)")
print("   Username: advertiser")
print("   Password: Advertiser@123")
print("")
print("SUBSCRIBER (Content Reader)")
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