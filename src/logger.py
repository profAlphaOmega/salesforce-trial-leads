from sentry_sdk import add_breadcrumb


class Logging:
    # Insert breadcrumb into Sentry
    def __init__(self, category='default'):
        self.category = category

    def info(self, message='default'):
        add_breadcrumb(
            level='info',
            category=self.category,
            message=message,
        )

    def warning(self, message='default'):
        add_breadcrumb(
            level='warning',
            category=self.category,
            message=message,
        )

    def error(self, message='default'):
        add_breadcrumb(
            level='error',
            category=self.category,
            message=message,
        )
