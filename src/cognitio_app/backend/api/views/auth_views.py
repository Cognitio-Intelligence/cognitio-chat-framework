"""
Authentication views for handling user login, signup, logout, and status.

These views handle HTTP requests and delegate business logic to the AuthService.
"""

import logging
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..services.auth_service import AuthService
from ..utils.helpers import format_api_response, validate_required_fields

logger = logging.getLogger(__name__)

# Initialize auth service
auth_service = AuthService()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_cloud_api(request):
    """
    Login user with cloud API and return both access and refresh tokens.
    
    Returns:
        JSON response with tokens and user data
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                format_api_response(False, message='Email and password are required'),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        auth_service = AuthService()
        success, access_token, refresh_token, user_data = auth_service.login(email, password)
        
        if success:
            response_data = {
                'access_token': access_token,
                'token': access_token,  # For backward compatibility
                'user': user_data
            }
            
            # Include refresh token if available
            if refresh_token:
                response_data['refresh_token'] = refresh_token
                response_data['refresh'] = refresh_token  # For backward compatibility
            
            return Response(
                format_api_response(True, message='Login successful', data=response_data),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                format_api_response(False, message='Invalid email or password'),
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return Response(
            format_api_response(False, message=f'Login failed: {str(e)}'),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def signup_with_cloud_api(request):
    """
    Register user with cloud API and create Django session.
    
    Request body:
        - email: User email address
        - password: User password
        - first_name: User first name
        - last_name: User last name
    
    Returns:
        JSON response with signup status and user data
    """
    try:
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        validation_errors = validate_required_fields(request.data, required_fields)
        if validation_errors:
            return Response(
                format_api_response(False, errors=validation_errors),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use auth service to handle signup
        success, response_data = auth_service.signup_user(request, request.data)
        
        if success:
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Signup view error: {e}")
        return Response(
            format_api_response(False, message='Signup failed', errors={'detail': str(e)}),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@csrf_exempt
def logout_user(request):
    """
    Logout user and clear Django session.
    
    Returns:
        JSON response with logout status
    """
    try:
        # Use auth service to handle logout
        success, response_data = auth_service.logout_user(request)
        
        if success:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Logout view error: {e}")
        return Response(
            format_api_response(False, message='Logout failed', errors={'detail': str(e)}),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status(request):
    """
    Check authentication status using Django session.
    
    Returns:
        JSON response with authentication status and user data
    """
    try:
        # Use auth service to get status
        response_data = auth_service.get_auth_status(request)
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Auth status view error: {e}")
        return Response(
            format_api_response(False, message='Failed to get auth status', errors={'detail': str(e)}),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Get CSRF token for frontend forms.
    
    Returns:
        JSON response with CSRF token set in cookie
    """
    return Response(
        format_api_response(True, message='CSRF token set in cookie'),
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token using refresh token.
    
    Returns:
        JSON response with new access token
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                format_api_response(False, message='Refresh token is required'),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        auth_service = AuthService()
        success, new_access_token = auth_service.cloud_api.refresh_token(refresh_token)
        
        if success:
            response_data = {
                'access': new_access_token,
                'access_token': new_access_token,  # For backward compatibility
                'token': new_access_token  # For backward compatibility
            }
            
            return Response(
                format_api_response(True, message='Token refreshed successfully', data=response_data),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                format_api_response(False, message='Invalid refresh token'),
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return Response(
            format_api_response(False, message=f'Token refresh failed: {str(e)}'),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 