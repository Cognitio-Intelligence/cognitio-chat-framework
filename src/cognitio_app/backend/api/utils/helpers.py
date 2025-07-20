def format_api_response(success, message=None, data=None, errors=None):
    """
    Format API response in a consistent structure.
    
    Args:
        success (bool): Indicates if the request was successful.
        message (str, optional): A message describing the result.
        data (dict, optional): Data to include in the response.
        errors (dict, optional): Errors to include in the response.
    
    Returns:
        dict: Formatted API response.
    """
    response = {
        'success': success,
        'message': message,
        'data': data or {},
        'errors': errors or {}
    }
    return response

def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the input data.

    Args:
        data (dict): The input data to validate.
        required_fields (list): A list of required field names.

    Returns:
        dict: A dictionary containing any missing fields.
    """
    missing_fields = [field for field in required_fields if field not in data]
    return {'missing_fields': missing_fields} if missing_fields else {}