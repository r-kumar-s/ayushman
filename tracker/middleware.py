from .models import Visitor, CampaignVisit, PageView


class VisitorTrackingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

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

        PageView.objects.create(
            visitor=visitor,
            url=request.build_absolute_uri(),
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
                landing_page=request.build_absolute_uri()
            )

        return self.get_response(request)