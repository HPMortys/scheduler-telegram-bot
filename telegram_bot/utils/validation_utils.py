from datetime import datetime


def is_time_format_valid(time_value: str, valid_form: str = "%H:%M") -> bool:
    try:
        datetime.strptime(time_value, valid_form)
    except ValueError:
        return False
    return True


def is_content_input_step_valid(content_value: str, size=512):
    pass

