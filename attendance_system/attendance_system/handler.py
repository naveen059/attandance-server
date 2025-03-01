from django.core.wsgi import get_wsgi_application
from serverless_wsgi import handle_request

# Initialize Django application
application = get_wsgi_application()

def handler(event, context):
    return handle_request(application, event, context)