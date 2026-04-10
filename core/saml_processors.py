"""
SAML Attribute Processors

This module contains custom processors that extract and map Django user attributes
to SAML attributes for the Identity Provider.
"""

from typing import Any


def user_attributes(user: Any, request: Any, **kwargs: Any) -> dict[str, Any]:
    """
    Process and return user attributes for SAML assertions.
    
    Maps Django user model attributes to SAML attribute names.
    """
    attributes = {
        'email': [user.email],
        'username': [user.username],
        'first_name': [user.first_name],
        'last_name': [user.last_name],
    }
    
    # Add groups if available
    if hasattr(user, 'groups'):
        attributes['groups'] = list(user.groups.values_list('name', flat=True))
    
    # Add staff/superuser status
    attributes['is_staff'] = [str(user.is_staff)]
    attributes['is_active'] = [str(user.is_active)]
    
    return attributes


def user_email(user: Any, request: Any, **kwargs: Any) -> dict[str, Any]:
    """Return only the user's email attribute."""
    return {
        'email': [user.email],
    }


def user_full_info(user: Any, request: Any, **kwargs: Any) -> dict[str, Any]:
    """Return comprehensive user information."""
    attributes = {
        'email': [user.email],
        'username': [user.username],
        'first_name': [user.first_name],
        'last_name': [user.last_name],
        'full_name': [f'{user.first_name} {user.last_name}'.strip()],
        'display_name': [user.get_full_name() or user.username],
    }
    
    if hasattr(user, 'groups'):
        attributes['groups'] = list(user.groups.values_list('name', flat=True))
    
    attributes['is_staff'] = [str(user.is_staff)]
    attributes['is_superuser'] = [str(user.is_superuser)]
    attributes['is_active'] = [str(user.is_active)]
    
    # Add date joined and last login if available
    if hasattr(user, 'date_joined') and user.date_joined:
        attributes['date_joined'] = [user.date_joined.isoformat()]
    
    if hasattr(user, 'last_login') and user.last_login:
        attributes['last_login'] = [user.last_login.isoformat()]
    
    return attributes
