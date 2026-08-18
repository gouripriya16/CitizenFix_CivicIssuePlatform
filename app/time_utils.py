from datetime import timedelta, timezone


INDIA_TIMEZONE = timezone(
    timedelta(hours=5, minutes=30)
)


def format_india_time(value):

    if value is None:
        return ""

    utc_time = value.replace(
        tzinfo=timezone.utc
    )

    india_time = utc_time.astimezone(
        INDIA_TIMEZONE
    )

    return india_time.strftime(
        "%d %B %Y, %I:%M %p"
    )