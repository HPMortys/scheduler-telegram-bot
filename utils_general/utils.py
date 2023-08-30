from typing import Union

week_days = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}


def week_data_data_transform(week_days_data: Union[list[int], list[None]]) -> list[str]:
    return [week_days[idx] for idx in week_days_data]
