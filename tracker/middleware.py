from .models import Visitor, CampaignVisit, PageView


class VisitorTrackingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def get_public_url(self, request):
        """
        Build the public URL seen by visitors.

        Apache internally forwards the request to Django on port 8090,
        so request.build_absolute_uri() can incorrectly produce:
            http://ayushmaanbhavah.com:8090/...

        The public website is:
            https://ayushmaanbhavah.com/...
        """

        host = request.get_host()

        # Remove internal proxy port if Django sees it
        if ':8090' in host:
            host = host.replace(':8090', '')

        # Always use the public HTTPS URL
        return 'https://' + host + request.get_full_path()

    def __call__(self, request):

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        visitor, created = Visitor.objects.get_or_create(
            session_key=session_key,
            defaults={
                "ip_address": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT"),
            }
        )

        public_url = self.get_public_url(request)

        PageView.objects.create(
            visitor=visitor,
            url=public_url,
            referrer=request.META.get("HTTP_REFERER")
        )

        if request.GET.get("utm_source"):

            CampaignVisit.objects.create(
                visitor=visitor,
                utm_source=request.GET.get("utm_source"),
                utm_medium=request.GET.get("utm_medium"),
                utm_campaign=request.GET.get("utm_campaign"),
                utm_content=request.GET.get("utm_content"),
                utm_term=request.GET.get("utm_term"),
                landing_page=public_url
            )

        return self.get_response(request)