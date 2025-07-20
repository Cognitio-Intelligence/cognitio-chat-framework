"""
Authentication service for handling user authentication with backend API.

Contains business logic for login, signup, logout, and session management.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class CloudAPIService:
    """Service for communicating with the cloud API."""
    
    def __init__(self):
        self.base_url =  '127.0.0.1:3927'
        logger.info(f"Using cloud API: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests."""
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'Cognitio-Desktop-App/1.0'
        }

    def login(self, email: str, password: str) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
        """
        Login user with cloud API.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success, access_token, refresh_token, user_data)
        """
        try:
            response = requests.post(
                f'{self.base_url}/auth/login/',
                json={
                    'email': email,
                    'password': password
                },
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token') or data.get('token') or data.get('access')
                refresh_token = data.get('refresh_token') or data.get('refresh')
                user_data = data.get('user', {})
                
                if access_token:
                    logger.info(f"Successfully logged in user: {email}")
                    logger.info(f"Received access token: {'YES' if access_token else 'NO'}")
                    logger.info(f"Received refresh token: {'YES' if refresh_token else 'NO'}")
                    return True, access_token, refresh_token, user_data
                else:
                    logger.error("No access token in response")
                    return False, None, None, None
            else:
                logger.error(f"Login failed with status {response.status_code}: {response.text}")
                return False, None, None, None
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False, None, None, None

    def signup(self, email: str, password: str, first_name: str = "", last_name: str = "") -> Tuple[bool, Optional[str]]:
        """
        Sign up user with cloud API.
        
        Args:
            email: User's email address
            password: User's password
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.post(
                f'{self.base_url}/auth/register/',
                json={
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name
                },
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 201:
                logger.info(f"Successfully created user: {email}")
                return True, "User created successfully"
            else:
                error_msg = response.json().get('error', 'Unknown error')
                logger.error(f"Signup failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            return False, str(e)

    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate token with cloud API.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Tuple of (valid, user_data)
        """
        try:
            response = requests.get(
                f'{self.base_url}/auth/validate-token/',
                headers={
                    **self._get_headers(),
                    'Authorization': f'Bearer {token}'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, user_data
            else:
                logger.error(f"Token validation failed: {response.status_code}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False, None

    def refresh_token(self, refresh_token: str) -> Tuple[bool, Optional[str]]:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Tuple of (success, new_access_token)
        """
        try:
            response = requests.post(
                f'{self.base_url}/auth/refresh/',
                json={'refresh': refresh_token},
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get('access') or data.get('access_token') or data.get('token')
                if new_access_token:
                    logger.info("Successfully refreshed access token")
                    return True, new_access_token
                else:
                    logger.error("No access token in refresh response")
                    return False, None
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False, None

    def logout(self, refresh_token: str) -> bool:
        """
        Logout user by blacklisting refresh token.
        
        Args:
            refresh_token: Refresh token to blacklist
            
        Returns:
            Success status
        """
        try:
            response = requests.post(
                f'{self.base_url}/auth/logout/',
                json={'refresh': refresh_token},
                headers=self._get_headers(),
                timeout=30
            )
            
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False

    def get_jwt_token_for_user(self, user) -> Optional[str]:
        """
        Get JWT token for a user for API authentication.
        
        Args:
            user: Django User object
            
        Returns:
            JWT token string or None if failed
        """
        try:
            # For now, we'll create a simple token based on user data
            # In a production system, you would obtain this from the cloud API
            # or use a proper JWT library to generate tokens
            from django.contrib.auth.models import User
            from django.utils import timezone
            import base64
            import json
            
            if not isinstance(user, User):
                logger.warning(f"Invalid user object: {type(user)}")
                return None
            
            # Create a simple JWT payload
            payload = {
                'user_id': user.id,
                'email': user.email,
                'exp': int((timezone.now() + timezone.timedelta(hours=1)).timestamp()),
                'iat': int(timezone.now().timestamp()),
                'iss': 'cognitio-backend'
            }
            
            # For development, we'll use a simple base64 encoding
            # In production, use proper JWT signing
            token_data = base64.b64encode(json.dumps(payload).encode()).decode()
            
            logger.info(f"Generated JWT token for user {user.email} (ID: {user.id})")
            return f"Bearer {token_data}"
            
        except Exception as e:
            logger.error(f"Failed to generate JWT token for user {user.id}: {e}")
            return None

    def _get_user_password(self, user) -> Optional[str]:
        """
        Get stored password for a user.
        In a real implementation, this would use secure credential storage.
        
        Args:
            user: Django User object
            
        Returns:
            Password if found, None otherwise
        """
        try:
            # Create a unique key for this user
            env_key = f"USER_PASSWORD_{user.email.replace('@', '_').replace('.', '_').upper()}"
            
            # Get from environment variable
            import os
            password = os.environ.get(env_key)
            
            if password:
                logger.info(f"Found stored password for user {user.email}")
                return password
            else:
                logger.warning(f"No stored password found for user {user.email}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting password for user {user.email}: {e}")
            return None
    
    def set_user_credentials(self, user, email: str, password: str) -> bool:
        """
        Set user credentials for JWT authentication.
        This allows users to configure their own credentials for cloud API access.
        
        Args:
            user: Django User object
            email: Email for cloud API authentication
            password: Password for cloud API authentication
            
        Returns:
            True if credentials were set successfully
        """
        try:
            # Store credentials in environment variables (for development)
            # In production, use a secure credential store
            import os
            
            # Create a unique key for this user
            env_key = f"USER_PASSWORD_{email.replace('@', '_').replace('.', '_').upper()}"
            
            # Set the environment variable
            os.environ[env_key] = password
            
            logger.info(f"✅ Set credentials for user {user.email} to authenticate as {email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting credentials for user {user.email}: {e}")
            return False

class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self):
        self.cloud_api = CloudAPIService()
    
    def login_user(self, request, email: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Login user using cloud API authentication.
        
        Args:
            request: Django request object
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            # First, try to authenticate with cloud API
            success, access_token, refresh_token, user_data = self.cloud_api.login(email, password)
            
            if success and access_token and user_data:
                # Create or get local user
                username = user_data.get('username', email)
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': user_data.get('email', email),
                        'first_name': user_data.get('first_name', ''),
                        'last_name': user_data.get('last_name', ''),
                        'is_active': True
                    }
                )
                
                if created:
                    logger.info(f"Created new local user: {username}")
                else:
                    logger.info(f"Found existing local user: {username}")
                
                # Store credentials for future use
                self.cloud_api.set_user_credentials(user, email, password)
                
                # Login the user locally
                login(request, user)
                
                return True, {
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'token': access_token
                }
            else:
                return False, {
                    'success': False,
                    'message': 'Invalid credentials'
                }
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False, {
                'success': False,
                'message': 'Login failed due to server error'
            }
    
    def signup_user(self, request, user_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Sign up user using cloud API.
        
        Args:
            request: Django request object  
            user_data: Dict containing user registration data
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            email = user_data.get('email')
            password = user_data.get('password')
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            
            success, message = self.cloud_api.signup(email, password, first_name, last_name)
            
            if success:
                return True, {
                    'success': True,
                    'message': 'Account created successfully'
                }
            else:
                return False, {
                    'success': False,
                    'message': message
                }
                
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            return False, {
                'success': False,
                'message': 'Signup failed due to server error'
            }
    
    def logout_user(self, request) -> Tuple[bool, Dict[str, Any]]:
        """
        Logout user.
        
        Args:
            request: Django request object
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Logout from Django
            logout(request)
            
            return True, {
                'success': True,
                'message': 'Logged out successfully'
            }
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False, {
                'success': False,
                'message': 'Logout failed'
            }
    
    def validate_user_token(self, token: str) -> Dict[str, Any]:
        """
        Validate user token with cloud API.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            valid, user_data = self.cloud_api.validate_token(token)
            
            if valid and user_data:
                return {
                    'success': True,
                    'user': user_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid token'
                }
                
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return {
                'success': False,
                'message': 'Token validation failed'
            }
    
    def get_user_profile(self, user) -> Dict[str, Any]:
        """
        Get user profile data.
        
        Args:
            user: Django User object
            
        Returns:
            Dict containing user profile data
        """
        try:
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined,
                    'is_active': user.is_active,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {
                'success': False,
                'message': 'Failed to get user profile'
            }

    def get_auth_status(self, request) -> Dict[str, Any]:
        """
        Get authentication status for the current request.
        
        Args:
            request: Django request object
            
        Returns:
            Dict containing authentication status and user data
        """
        try:
            # Check if user is authenticated via Django session
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
                logger.info(f"User authenticated via Django session: {user.email}")
                
                return {
                    'success': True,
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_active': user.is_active,
                        'date_joined': user.date_joined.isoformat() if user.date_joined else None
                    }
                }
            
            # Check for JWT token in Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                
                # Validate token with cloud API
                result = self.validate_user_token(token)
                if result.get('success'):
                    logger.info(f"User authenticated via JWT token")
                    return {
                        'success': True,
                        'authenticated': True,
                        'user': result.get('user'),
                        'token': token
                    }
            
            # No valid authentication found
            logger.info("No authentication found")
            return {
                'success': True,
                'authenticated': False,
                'user': None
            }
            
        except Exception as e:
            logger.error(f"Error checking auth status: {e}")
            return {
                'success': False,
                'authenticated': False,
                'error': str(e)
            } 