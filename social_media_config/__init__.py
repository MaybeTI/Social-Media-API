# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celary import app as celary_app

__all__ = ("celary_app",)
