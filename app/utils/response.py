def make_response(success: bool, message_key: str, data=None, errors=None):
    return {
        "success": success,
        "message_key": message_key,
        "data": data,
        "errors": errors,
    }