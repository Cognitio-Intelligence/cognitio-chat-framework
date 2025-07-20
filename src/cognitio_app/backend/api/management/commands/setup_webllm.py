"""
WebLLM Framework Setup Command

This command helps users set up the Cognitio Chat Framework quickly and easily.
"""

import os
import subprocess
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Set up the Cognitio Chat Framework for development or production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['dev', 'prod'],
            default='dev',
            help='Setup mode: dev for development, prod for production'
        )
        parser.add_argument(
            '--skip-frontend',
            action='store_true',
            help='Skip frontend build process'
        )
        parser.add_argument(
            '--create-env',
            action='store_true',
            help='Create .env file from .env.example'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Cognitio Chat Framework...\n')
        )

        mode = options['mode']
        skip_frontend = options['skip_frontend']
        create_env = options['create_env']

        # Step 1: Create .env file if requested
        if create_env:
            self.create_env_file()

        # Step 2: Check Python dependencies
        self.check_python_dependencies()

        # Step 3: Run database migrations
        self.run_migrations()

        # Step 4: Set up frontend (unless skipped)
        if not skip_frontend:
            self.setup_frontend(mode)

        # Step 5: Create superuser for admin access
        if mode == 'dev':
            self.create_superuser()

        # Step 6: Show completion message
        self.show_completion_message(mode)

    def create_env_file(self):
        """Create .env file from .env.example if it doesn't exist"""
        base_dir = Path(settings.BASE_DIR)
        env_file = base_dir / '.env'
        env_example_file = base_dir / '.env.example'

        if env_file.exists():
            self.stdout.write(
                self.style.WARNING('⚠️  .env file already exists, skipping creation')
            )
            return

        if not env_example_file.exists():
            self.stdout.write(
                self.style.ERROR('❌ .env.example file not found')
            )
            return

        try:
            # Copy .env.example to .env
            with open(env_example_file, 'r') as example:
                content = example.read()
            
            with open(env_file, 'w') as env:
                env.write(content)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Created .env file from .env.example')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Please edit .env file with your settings')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to create .env file: {e}')
            )

    def check_python_dependencies(self):
        """Check if all Python dependencies are installed"""
        self.stdout.write('📦 Checking Python dependencies...')
        
        try:
            # Try importing key dependencies
            import django
            import rest_framework
            import corsheaders
            
            self.stdout.write(
                self.style.SUCCESS('✅ Python dependencies are installed')
            )
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Missing Python dependency: {e}')
            )
            self.stdout.write(
                self.style.WARNING('Run: pip install -r requirements.txt')
            )
            sys.exit(1)

    def run_migrations(self):
        """Run database migrations"""
        self.stdout.write('🗄️  Running database migrations...')
        
        try:
            from django.core.management import call_command
            call_command('migrate', verbosity=0)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Database migrations completed')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Migration failed: {e}')
            )

    def setup_frontend(self, mode):
        """Set up the frontend"""
        self.stdout.write('🎨 Setting up frontend...')
        
        base_dir = Path(settings.BASE_DIR)
        frontend_dir = base_dir / 'src' / 'cognitio_app' / 'backend' / 'frontend-src'
        
        if not frontend_dir.exists():
            self.stdout.write(
                self.style.ERROR('❌ Frontend directory not found')
            )
            return

        try:
            # Check if node_modules exists
            node_modules = frontend_dir / 'node_modules'
            if not node_modules.exists():
                self.stdout.write('📦 Installing npm dependencies...')
                subprocess.run(
                    ['npm', 'install'],
                    cwd=frontend_dir,
                    check=True,
                    capture_output=True
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ NPM dependencies installed')
                )

            # Build frontend
            self.stdout.write('🔨 Building frontend...')
            build_command = 'build' if mode == 'prod' else 'build'
            subprocess.run(
                ['npm', 'run', build_command],
                cwd=frontend_dir,
                check=True,
                capture_output=True
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Frontend built successfully')
            )
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Frontend setup failed: {e}')
            )
            self.stdout.write(
                self.style.WARNING('You may need to install Node.js and npm')
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('❌ npm not found. Please install Node.js and npm')
            )

    def create_superuser(self):
        """Create a superuser for development"""
        self.stdout.write('👤 Setting up admin user...')
        
        from django.contrib.auth.models import User
        
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('⚠️  Admin user already exists')
            )
            return

        try:
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Created admin user (admin/admin123)')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Change the admin password in production!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to create admin user: {e}')
            )

    def show_completion_message(self, mode):
        """Show completion message with next steps"""
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Cognitio Chat Framework setup complete!')
        )
        
        self.stdout.write('\n📋 Next steps:')
        
        if mode == 'dev':
            self.stdout.write('   1. Run: python manage.py runserver')
            self.stdout.write('   2. Open: http://127.0.0.1:3927')
            self.stdout.write('   3. Admin: http://127.0.0.1:3927/admin (admin/admin123)')
            self.stdout.write('   4. For standalone app: briefcase dev')
        else:
            self.stdout.write('   1. Configure your web server')
            self.stdout.write('   2. Set up SSL certificates')
            self.stdout.write('   3. Configure your domain in ALLOWED_HOSTS')
            self.stdout.write('   4. Run: python manage.py collectstatic')

        self.stdout.write('\n📚 Documentation: https://github.com/yourusername/django-react-webllm-application')
        self.stdout.write('🆘 Support: Create an issue on GitHub')
        
        self.stdout.write(
            self.style.SUCCESS('\nHappy chatting with WebLLM! 🤖')
        )
