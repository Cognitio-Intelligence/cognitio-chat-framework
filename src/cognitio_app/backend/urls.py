"""
URL configuration for WebLLM Chat application.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse
import os

def health_check(request):
    """Simple health check endpoint for the desktop app."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'WebLLM Chat Backend',
        'version': '1.0.0'
    })

class ReactAppView(TemplateView):
    """Serve the React application."""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['BACKEND_API_URL'] = 'http://127.0.0.1:3927/api/v1'
        context['DEBUG'] = settings.DEBUG
        return context

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API endpoints
    path('api/v1/', include('cognitio_app.backend.api.urls')),
    
    # React app routes
    path('', ReactAppView.as_view(), name='react_app_root'),
]

# Always serve static files (for both debug and production)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve frontend assets - updated paths for built application
import os
base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For built applications, the assets are in the cognitio_app/static directory
production_assets_dir = os.path.join(base_dir, 'static', 'assets')
if os.path.exists(production_assets_dir):
    urlpatterns += static('/static/assets/', document_root=production_assets_dir)
    print(f"Serving static assets from: {production_assets_dir}")
else:
    # Alternative path in backend static
    alt_assets_dir = os.path.join(base_dir, 'backend', 'static', 'assets') 
    if os.path.exists(alt_assets_dir):
        urlpatterns += static('/static/assets/', document_root=alt_assets_dir)
        print(f"Serving static assets from: {alt_assets_dir}")
    else:
        print(f"Warning: Static assets directory not found. Checked: {production_assets_dir} and {alt_assets_dir}")