from django.http import HttpResponseForbidden

class BlockStaticFilesMiddleware:
    """ Middleware to block access to static files """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.path)
        if request.path.endswith(('.jpg', '.png', '.gif')) or request.path.startswith('/static/'):
            return redirect("/dashboard")
        response = self.get_response(request)
        return response
