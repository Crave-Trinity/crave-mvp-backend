# File: app/core/use_cases/process_query.py
from typing import Optional

from app.core.use_cases.generate_craving_insights import generate_insights
from app.infrastructure.auth.auth_service import get_current_user, CurrentUser
from app.infrastructure.database.repository import User, Craving


def process_user_query(user_id: int, query: Optional[str] = None, current_user: CurrentUser = None):
    """
    Process a user's query. If no query is provided, a default summary
    is generated.
    """

    # Input Validation
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user ID provided.")

    if query is not None and not isinstance(query, str):
        raise TypeError("Query must be a string or None.")

    # Ensure current_user is properly handled
    if current_user is None or not isinstance(current_user, CurrentUser):
        raise ValueError("Invalid current_user information.")

    # Ensure current_user matches the user_id, or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise PermissionError("User does not have permission to access thisa resource.")


    # Delegate the actual insight generation.
    return generate_insights(user_id, query)