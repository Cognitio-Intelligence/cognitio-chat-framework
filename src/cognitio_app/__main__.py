#!/usr/bin/env python3
"""
Main entry point for WebLLM Chat Desktop Application.

This module serves as the entry point for BeeWare Briefcase to run the desktop app.
It starts the Django backend server and opens the frontend URL in a web view.
All WebLLM processing happens locally in the browser context.
"""

import os
import sys
import threading
import time
import subprocess
import webbrowser
import socket
import signal
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"ℹ️  No .env file found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not available, skipping .env file loading")

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class WebLLMChatApp(toga.App):
    """Main application class for WebLLM Chat."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define consistent port ranges - prioritize the standard ports
        self.backend_ports = [3927]
        self.backend_port = None
        self.backend_process = None
        self.last_status_check = 0
        self._stop_event = threading.Event()
        self.browser_opened = False
        
        # Detect app bundle mode early
        self.app_bundle_mode = (
            hasattr(sys, 'frozen') or 
            'app_packages' in str(Path(__file__)) or
            '.app/Contents/Resources' in str(Path(__file__))
        )
        
        if self.app_bundle_mode:
            print("📦 Detected app bundle mode - will use production settings")
        else:
            print("🛠️  Detected development mode")

    def _set_app_icon(self):
        """Set the application icon explicitly."""
        try:
            # Get the icon path relative to the app module
            icon_base = Path(__file__).parent / "resources" / "LOGO-light-vertical"
            
            # Try different icon formats in order of preference for macOS
            icon_paths = [
                icon_base.with_suffix('.icns'),  # macOS native format
                icon_base.with_suffix('.png'),   # Fallback PNG
                icon_base.with_suffix('.ico'),   # Windows format as last resort
            ]
            
            for path in icon_paths:
                if path.exists():
                    print(f"📱 Setting app icon: {path}")
                    # Try to set the icon on the app itself
                    if hasattr(self, 'icon'):
                        self.icon = str(path)
                    # Also try to set it as a property
                    try:
                        import toga
                        if hasattr(toga, 'Icon'):
                            self.icon = toga.Icon(str(path))
                    except Exception as e:
                        print(f"⚠️  Could not create Toga Icon: {e}")
                    return
            
            print("ℹ️  No icon file found, using default app icon")
        except Exception as e:
            print(f"⚠️  Error setting app icon: {e}")

    def find_free_port(self, port_list):
        """Find the first available port from the list."""
        for port in port_list:
            print(f"\n🔍 Checking port {port} availability...")
            
            # Check if port is available
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('127.0.0.1', port))
                    print(f"✅ Port {port} is available")
                    return port
            except OSError:
                print(f"ℹ️  Port {port} is occupied, trying next...")
                continue
                
        # If we get here, return the first port anyway
        print(f"ℹ️  Using first port from list: {port_list[0]}")
        return port_list[0]

    def check_frontend_built(self):
        """Check if the React frontend has been built."""
        try:
            # Different paths for app bundle vs development
            if self.app_bundle_mode:
                # In app bundle, check relative to the app bundle location
                frontend_build_path = Path(__file__).parent / "backend" / "frontend-src"
            else:
                # In development, check the standard project structure
                frontend_build_path = Path(__file__).parent.parent.parent / "src" / "cognitio_app" / "backend" / "frontend-src"

            
            # Check if build artifacts exist
            if frontend_build_path.exists():
                print(f"✅ React frontend build detected at: {frontend_build_path}")
                return True
            else:
                print(f"❌ React frontend not built at: {frontend_build_path}")
                return False
        except Exception as e:
            print(f"⚠️  Error checking frontend build: {e}")
            return False

    def build_frontend(self):
        """Build the React frontend automatically."""
        print("\n🔧 Building React frontend...")
        
        try:
            # Different paths for app bundle vs development
            if self.app_bundle_mode:
                # In app bundle, look for frontend-src in the app bundle
                frontend_src_path = Path(__file__).parent / "backend" / "frontend-src"
                if not frontend_src_path.exists():
                    # Fallback: try looking in Resources directory
                    resources_path = Path(__file__).parent.parent.parent
                    frontend_src_path = resources_path / "cognitio_app" / "backend" / "frontend-src"
            else:
                # In development, use standard project structure
                frontend_src_path = Path(__file__).parent.parent.parent / "src" / "cognitio_app" / "backend" / "frontend-src"
            
            if not frontend_src_path.exists():
                print(f"❌ Frontend source not found at: {frontend_src_path}")
                # In app bundle mode, this might be expected if frontend is pre-built
                if self.app_bundle_mode:
                    print("ℹ️  App bundle mode: frontend source not included in bundle")
                    print("ℹ️  Frontend should be pre-built during packaging")
                return False
            
            print(f"📁 Frontend source found at: {frontend_src_path}")
            
            # Check if we have Node.js available
            try:
                result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    print("❌ Node.js not found - cannot build frontend")
                    return False
                print(f"✅ Node.js found: {result.stdout.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("❌ Node.js not available - cannot build frontend")
                return False
            
            # Change to frontend directory
            original_cwd = os.getcwd()
            os.chdir(frontend_src_path)
            
            try:
                # Check if package.json exists
                package_json = frontend_src_path / "package.json"
                if not package_json.exists():
                    print("❌ package.json not found in frontend-src")
                    return False
                
                print("📦 Installing npm dependencies...")
                
                # Install dependencies
                npm_install_process = subprocess.run([
                    "npm", "install", "--legacy-peer-deps"
                ], capture_output=True, text=True, timeout=300)
                
                if npm_install_process.returncode != 0:
                    print(f"❌ npm install failed: {npm_install_process.stderr}")
                    return False
                
                print("✅ npm dependencies installed")
                print("🏗️  Building React frontend...")
                
                # Build the frontend
                npm_build_process = subprocess.run([
                    "npm", "run", "build"
                ], capture_output=True, text=True, timeout=300)
                
                if npm_build_process.returncode != 0:
                    print(f"❌ npm run build failed: {npm_build_process.stderr}")
                    return False
                
                print("✅ React frontend built successfully")
                
                # Verify build was successful
                if self.check_frontend_built():
                    print("✅ Frontend build verification passed")
                    return True
                else:
                    print("❌ Frontend build verification failed")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("❌ Frontend build timed out")
                return False
            except FileNotFoundError:
                print("❌ npm not found - please install Node.js and npm")
                return False
            except Exception as e:
                print(f"❌ Frontend build error: {e}")
                return False
            finally:
                # Always return to original directory
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"❌ Error during frontend build: {e}")
            return False

    def ensure_frontend_ready(self):
        """Ensure the frontend is built and ready."""
        print("\n🔍 Checking frontend status...")
        
        # Check if frontend is already built
        if self.check_frontend_built():
            print("✅ Frontend is ready")
            return True
        
        # In app bundle mode, frontend should already be built during packaging
        if self.app_bundle_mode:
            print("📦 App bundle mode - attempting to build frontend if source is available")
            
            # Try to build if we have source in the bundle
            success = self.build_frontend()
            if success:
                print("✅ Frontend built successfully in app bundle mode")
                return True
            else:
                print("⚠️  Frontend source not available in app bundle")
                print("ℹ️  Frontend should be pre-built during Briefcase packaging")
                print("ℹ️  Manual build required:")
                print("   1. cd src/cognitio_app/backend/frontend-src")
                print("   2. npm install")
                print("   3. npm run build")
                print("   4. Run 'briefcase create' and 'briefcase build' again")
                return False
        
        # In development mode, try to build the frontend
        print("🛠️  Development mode - attempting to build frontend...")
        self.status_label.text = "🔧 Building frontend..."
        
        success = self.build_frontend()
        if success:
            print("✅ Frontend build completed successfully")
            return True
        else:
            print("❌ Frontend build failed")
            print("ℹ️  Manual build may be required:")
            print("   cd src/cognitio_app/backend/frontend-src")
            print("   npm install")
            print("   npm run build")
            return False

    def startup(self):
        """Initialize the application."""
        # Ensure icon is set correctly
        self._set_app_icon()
        
        self.main_window = toga.MainWindow(title="WebLLM Chat")
        
        # Set window size for a more compact, modern feel
        try:
            self.main_window.size = (400, 450)
            # Try to set resizable if supported
            if hasattr(self.main_window, 'resizable'):
                self.main_window.resizable = False
        except Exception as e:
            print(f"ℹ️  Window configuration note: {e}")
            # Fallback to just setting size
            self.main_window.size = (400, 450)
        
        # Main container with a clean, white background and overall padding
        main_box = toga.Box(style=Pack(
            direction=COLUMN, 
            background_color="#ffffff",
            padding=20
        ))
        
        # App icon/logo placeholder
        icon_label = toga.Label(
            "🤖",
            style=Pack(
                font_size=48,
                text_align="center",
                padding_top=20,
                padding_bottom=10
            )
        )
        main_box.add(icon_label)
        
        # App title
        title_label = toga.Label(
            "WebLLM Chat",
            style=Pack(
                font_size=24, 
                font_weight="bold", 
                color="#212529",
                text_align="center",
                padding_bottom=5
            )
        )
        main_box.add(title_label)
        
        # Subtitle
        subtitle_label = toga.Label(
            "Privacy-First Local AI",
            style=Pack(
                font_size=14, 
                color="#6c757d",
                text_align="center",
                padding_bottom=25
            )
        )
        main_box.add(subtitle_label)
        
        # Status with modern styling
        self.status_label = toga.Label(
            "Initializing...",
            style=Pack(
                font_size=12, 
                color="#495057",
                text_align="center",
                background_color="#f1f3f5",
                padding=(8, 12)
            )
        )
        main_box.add(self.status_label)
        
        # Flexible spacer to push content down
        main_box.add(toga.Box(style=Pack(flex=1)))
        
        # Info text with better typography
        info_text = toga.Label(
            "The app will open in your browser automatically.\n"
            "WebGPU is recommended for best performance.",
            style=Pack(
                font_size=11,
                text_align="center",
                padding_bottom=15,
                color="#6c757d"
            )
        )
        main_box.add(info_text)
        
        # Button container
        button_container = toga.Box(style=Pack(
            direction=COLUMN,
            padding=0
        ))
        
        # Primary button
        self.open_browser_button = toga.Button(
            "🌐 Open in Browser",
            on_press=self.open_in_browser,
            style=Pack(
                padding=12,
                background_color="#4C5FD5",
                color="#ffffff",
                font_size=13,
                font_weight="bold"
            )
        )
        button_container.add(self.open_browser_button)
        
        # Secondary buttons row
        secondary_buttons = toga.Box(style=Pack(
            direction=ROW,
            padding_top=8,
            alignment="center"
        ))
    
        
        button_container.add(secondary_buttons)
        main_box.add(button_container)
        
        # Flexible spacer to push footer down
        main_box.add(toga.Box(style=Pack(flex=1)))
        
        # Footer with version info
        version_label = toga.Label(
            "v1.0.0 • Local Processing",
            style=Pack(
                font_size=9,
                color="#adb5bd",
                text_align="center",
                padding_bottom=5
            )
        )
        main_box.add(version_label)
        
        # Set the main window content
        self.main_window.content = main_box
        self.main_window.show()
        
        # Store the frontend URL for later use
        self.frontend_url = None
        
        # Ensure frontend is built before starting servers
        print("🔍 Preparing frontend...")
        self.status_label.text = "🔧 Preparing frontend..."
        
        # Check and build frontend if needed
        frontend_ready = self.ensure_frontend_ready()
        if not frontend_ready:
            self.status_label.text = "⚠️ Frontend build failed"
            print("⚠️  Continuing without frontend build - server will still start")
        
        # Find available ports
        print("🔍 Looking for available ports...")
        self.backend_port = self.find_free_port(self.backend_ports)
        
        if not self.backend_port:
            self.status_label.text = "⚠️ Port Error"
            print("❌ ERROR: Could not determine backend port!")
            return
        
        print(f"✅ Using port - Backend: {self.backend_port}")
        
        # Update initial status
        self.status_label.text = "🚀 Starting server..."
        
        # Start the backend server
        self.start_servers()

        # Add a background task to check on the servers and auto-open browser
        import asyncio
        asyncio.create_task(self.poll_servers_until_ready_async())

    def check_and_run_migrations(self):
        """Check and run migrations for the backend."""
        print("\n🗄️  Checking database migrations...")
        
        # Skip all Django management commands in app bundle mode
        if self.app_bundle_mode:
            print("📦 App bundle mode detected - skipping migration check")
            print("   ℹ️  Database will be auto-initialized on first backend startup")
            print("✅ Migration check skipped\n")
            return True
        
        # Always skip migration checks to prevent infinite loops
        print("⚠️  Skipping migration check to prevent startup issues")
        print("   ℹ️  Database will be auto-initialized on first backend startup")
        print("✅ Migration check skipped\n")
        return True

    def start_servers(self):
        """Start backend server."""
        print("\n🚀 Starting Cognitio Chat Framework...")
        
        # Check migrations first (will be skipped in app bundle mode)
        try:
            if not self.check_and_run_migrations():
                print("❌ Migration check failed, but continuing anyway")
        except Exception as e:
            print(f"❌ Migration check encountered error: {e}")
            print("ℹ️  Continuing with server startup...")
        
        # Start backend server
        print("1️⃣ Starting Backend...")
        
        # Determine mode based on app bundle detection
        if self.app_bundle_mode:
            print("📦 Running in app bundle mode (production)")
            is_dev = False
        else:
            print("🛠️  Running in development mode")
            is_dev = os.getenv("APP_MODE", "dev") == "dev"

        try:
            self.backend_thread = threading.Thread(target=self.start_backend, daemon=True)
            self.backend_thread.start()
            print("✅ Backend thread started")
        except Exception as e:
            print(f"❌ Error starting backend thread: {e}")
            self.status_label.text = "Backend startup failed"
            return
        
        print("🚀 Server startup initiated successfully")

    def start_backend(self):
        """Start the Django backend server."""
        try:
            print(f"🔧 Starting Backend on http://127.0.0.1:{self.backend_port}")
            
            # Set up environment variables
            env_vars = {
                'DJANGO_SETTINGS_MODULE': 'cognitio_app.backend.settings',
                'CORS_ALLOWED_ORIGINS': f'http://127.0.0.1:{self.backend_port},http://localhost:{self.backend_port}',
                'ALLOWED_HOSTS': f'127.0.0.1,localhost',
                'WEBLLM_ENABLE_ANALYTICS': 'True',
                'WEBLLM_DEFAULT_MODEL': 'Llama-3.2-1B-Instruct'
            }
            
            # Set environment variables
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Try to start Django programmatically first (works for both modes)
            print("🚀 Starting Django backend programmatically...")
            
            try:
                import django
                from django.core.management import call_command
                from django.conf import settings
                import threading
                import sys
                
                # Increase recursion limit to handle Django initialization
                original_recursion_limit = sys.getrecursionlimit()
                sys.setrecursionlimit(3000)  # Increase the recursion limit
                
                # Initialize Django without touching settings - we already set up environment variables
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cognitio_app.backend.settings')
                if not django.conf.settings.configured:
                    django.setup()

                # Run migrations
                print("🗄️  Running database migrations...")
                try:
                    call_command('migrate', verbosity=0, interactive=False)
                    print("✅ Database migrations completed successfully")
                except Exception as e:
                        print(f"⚠️  Migration warning (continuing anyway): {e}")
                
                # Create a thread to run the server
                def run_server():
                    try:
                        print(f"📡 Django server starting on port {self.backend_port}")
                        # Reset recursion limit back to original in the new thread
                        sys.setrecursionlimit(original_recursion_limit)
                        call_command('runserver', f'127.0.0.1:{self.backend_port}', verbosity=0, use_reloader=False)
                    except Exception as e:
                        print(f"⚠️  Django server error: {e}")
                
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                
                print("✅ Django backend started successfully")
                return
                
            except Exception as e:
                print(f"⚠️  Programmatic Django start failed: {e}")
                print("ℹ️  Trying fallback approach...")
            
            # Fallback: Try subprocess approach only in development mode
            if not self.app_bundle_mode:
                print("🛠️  Trying subprocess approach (development mode only)...")
                
                try:
                    # Get the project root directory
                    project_root = Path(__file__).parent.parent.parent
                    original_cwd = os.getcwd()
                    os.chdir(project_root)
                    
                    # Check if manage.py exists
                    manage_py_path = project_root / "manage.py"
                    if manage_py_path.exists():
                        print(f"📁 Working directory: {project_root}")
                        
                        # Create environment for subprocess
                        env = os.environ.copy()
                        env.update(env_vars)
                        
                        # Start Django server via subprocess
                        self.backend_process = subprocess.Popen([
                            sys.executable,
                            str(manage_py_path), "runserver",
                            f"127.0.0.1:{self.backend_port}",
                            "--noreload",
                            "--insecure"
                        ], cwd=project_root, env=env)
                        
                        print("✅ Django backend started via subprocess")
                        return
                    else:
                        print("⚠️  manage.py not found - skipping subprocess approach")
                        
                except Exception as e:
                    print(f"⚠️  Subprocess approach failed: {e}")
                finally:
                    try:
                        os.chdir(original_cwd)
                    except:
                        pass
            
            # If all else fails, just continue - the UI will still work
            print("⚠️  Backend startup failed - continuing with UI only")
            print("ℹ️  You can manually start the backend server if needed")
            
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            print("ℹ️  Continuing without backend - UI will still load")

    def check_servers_status(self):
        """Check server status and update UI (main thread safe)."""
        try:
            import requests
        except ImportError:
            return
        
        backend_ready = False
        
        # Check backend
        try:
            backend_url = f"http://127.0.0.1:{self.backend_port}"
            response = requests.get(f'{backend_url}/', timeout=3)
            if response.status_code in [200, 404]:  # 404 is ok for Django catch-all
                backend_ready = True
        except:
            pass
        
        # Update main status and auto-open browser if ready
        if backend_ready:
            # Use the Django backend URL 
            if not self.frontend_url:
                self.frontend_url = f"http://127.0.0.1:{self.backend_port}/"
            
            # Check if frontend is actually available before marking as ready
            frontend_available = self.check_frontend_built()
            
            if frontend_available:
                self.status_label.text = "✅ Ready • Chat Available"
                
                # Auto-open browser once when ready
                if not self.browser_opened:
                    self.browser_opened = True
                    print(f"🌐 Auto-opening WebLLM Chat in browser: {self.frontend_url}")
                    webbrowser.open(self.frontend_url)
            else:
                self.status_label.text = "⚠️ Backend ready • Frontend missing"
        else:
            self.status_label.text = f"⏳ Starting on :{self.backend_port}..."

    def check_servers_now(self, widget):
        """Manual server status check with detailed output."""
        print("\n🔍 Manual server status check...")
        self.status_label.text = "🔍 Checking..."
        self.check_servers_status()
        print("✅ Status check complete!")

    def wait_for_process_termination(self, process, name, timeout=10):
        """Wait for a process to terminate properly."""
        if process is None:
            return
        
        try:
            # First try graceful termination
            process.terminate()
            print(f"🛑 Terminating {name}...")
            
            # Wait for process to finish
            try:
                process.wait(timeout=timeout)
                print(f"✅ {name} terminated gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if timeout
                print(f"⚠️  Force killing {name}...")
                process.kill()
                process.wait(timeout=5)
                print(f"✅ {name} force killed")
                
        except Exception as e:
            print(f"❌ Error terminating {name}: {e}")

    def restart_servers(self, widget):
        """Restart the backend server."""
        print("\n🔄 Restarting WebLLM Chat server...")
        self.status_label.text = "🔄 Restarting..."
        
        # Properly terminate existing processes
        if self.backend_process:
            self.wait_for_process_termination(self.backend_process, "Backend")
            self.backend_process = None
        
        # Reset browser opened flag so it opens again
        self.browser_opened = False
        self.frontend_url = None
        
        time.sleep(2)
        
        # Start servers again
        self.start_servers()
        print("✅ Restart initiated!")

    def open_in_browser(self, widget):
        """Open the frontend URL in the default browser."""
        if self.frontend_url:
            # Double-check frontend availability before opening
            if not self.check_frontend_built():
                try:
                    self.main_window.info_dialog("Frontend Not Built", 
                        "The React frontend is not built yet.\n\n"
                        f"In app bundle mode, please build manually:\n"
                        "1. cd src/cognitio_app/backend/frontend-src\n"
                        "2. npm install\n"
                        "3. npm run build\n"
                        "4. Run 'briefcase create' and 'briefcase build' again")
                except:
                    pass
                return
                
            print(f"🌐 Opening in browser: {self.frontend_url}")
            webbrowser.open(self.frontend_url)
        else:
            print("⚠️  Frontend URL not available yet")
            self.status_label.text = "⚠️ Not ready yet..."
            
            # Check if frontend build is the issue
            if not self.check_frontend_built():
                try:
                    self.main_window.info_dialog("Frontend Not Built", 
                        "The React frontend needs to be built.\n\n"
                        "Please build the frontend manually:\n"
                        "1. cd src/cognitio_app/backend/frontend-src\n"
                        "2. npm install\n"
                        "3. npm run build\n"
                        f"{'4. Run briefcase create/build again' if self.app_bundle_mode else ''}")
                except:
                    pass
                
                # Try to build frontend in the background only in development mode
                if not self.app_bundle_mode:
                    threading.Thread(target=self.build_frontend, daemon=True).start()
            else:
                try:
                    self.main_window.info_dialog("WebLLM Chat", "Server is still starting up.\nPlease wait a moment and try again.")
                except:
                    pass

    def on_exit(self):
        """Clean up when the app is closing."""
        print("\n🧹 Cleaning up processes...")
        
        # Signal background tasks to stop
        self._stop_event.set()
        
        if self.backend_process:
            self.wait_for_process_termination(self.backend_process, "Backend")
            print("✅ Backend process terminated")
        
        print("👋 Thanks for using WebLLM Chat!")
        return True

    async def poll_servers_until_ready_async(self):
        """Polls servers until they are ready, then stops."""
        import asyncio
        
        # Give servers a moment to start up before the first check
        await asyncio.sleep(3.0)

        while not self.frontend_url and not self._stop_event.is_set():
            self.check_servers_status()
            await asyncio.sleep(2)  # Wait for 2 seconds before checking again
        
        if self.frontend_url:
            print("✅ WebLLM Chat is ready. Polling task finished.")
        else:
            print("⚠️ Polling stopped before server was ready.")


def main():
    """Main entry point for the application."""
    # Create a simple placeholder icon if none exists
    icon_base = Path(__file__).parent / "resources"
    
    # Ensure resources directory exists
    icon_base.mkdir(exist_ok=True)
    
    # Try different icon formats in order of preference for macOS
    icon_paths = [
        icon_base / "LOGO-light-vertical.icns",  # macOS native format
        icon_base / "LOGO-light-vertical.png",   # Fallback PNG
        icon_base / "LOGO-light-vertical.ico",   # Windows format as last resort
    ]
    
    icon_path = None
    for path in icon_paths:
        if path.exists():
            icon_path = str(path)
            print(f"📱 Using icon: {icon_path}")
            break
    
    if not icon_path:
        print("ℹ️  No icon file found, using default")
        # Create a simple placeholder icon if none exists
        try:
            # For development, just use None to let Toga use default
            icon_path = None
        except Exception as e:
            print(f"ℹ️  Icon creation note: {e}")
            icon_path = None
    
    return WebLLMChatApp(
        'WebLLM Chat',
        'org.webllm.chat',
        description='Privacy-first local AI chat with WebLLM models',
        icon=icon_path
    )


if __name__ == '__main__':
    print("🤖 Starting WebLLM Chat Desktop Application...")
    print("💻 Debug information will be displayed in this terminal")
    print("🌐 Application will open in your default browser for WebGPU support")
    print("🔧 Use the control panel to manage the server")
    print("🧠 All AI processing happens locally with WebLLM")
    print("-" * 60)
    
    app = main()
    app.main_loop()