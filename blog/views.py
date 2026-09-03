from django.shortcuts import render
from django.http import Http404


BLOG_ARTICLES = {

    "pcod-pcos": {

        "ayurvedic-approach-pcod-pcos":
            "ayurvedic-approach-pcod-pcos.html",

        "pcod-irregular-periods":
            "pcod-irregular-periods.html",

        "pcod-weight-management":
            "pcod-weight-management.html",

        "pcod-fertility":
            "pcod-fertility.html",

        "panchakarma-for-pcod":
            "panchakarma-for-pcod.html",
    },


    "thyroid": {

        "ayurveda-thyroid-health":
            "ayurveda-thyroid-health.html",

        "thyroid-symptoms-ayurvedic-perspective":
            "thyroid-symptoms-ayurvedic-perspective.html",

        "thyroid-diet-lifestyle":
            "thyroid-diet-lifestyle.html",

        "ayurveda-hypothyroidism":
            "ayurveda-hypothyroidism.html",

        "panchakarma-thyroid-care":
            "panchakarma-thyroid-care.html",
    },


    "arthritis": {

        "ayurvedic-approach-arthritis":
            "ayurvedic-approach-arthritis.html",

        "arthritis-joint-stiffness":
            "arthritis-joint-stiffness.html",

        "ayurveda-knee-joint-pain":
            "ayurveda-knee-joint-pain.html",

        "diet-lifestyle-joint-health":
            "diet-lifestyle-joint-health.html",

        "panchakarma-arthritis":
            "panchakarma-arthritis.html",
    },


    "acidity-gastritis": {

        "ayurvedic-approach-acidity":
            "ayurvedic-approach-acidity.html",

        "gastritis-digestive-health":
            "gastritis-digestive-health.html",

        "acidity-diet-lifestyle":
            "acidity-diet-lifestyle.html",

        "heartburn-indigestion-ayurveda":
            "heartburn-indigestion-ayurveda.html",

        "panchakarma-digestive-concerns":
            "panchakarma-digestive-concerns.html",
    },


    "ibs-constipation": {

        "ayurvedic-approach-ibs":
            "ayurvedic-approach-ibs.html",

        "constipation-gut-health":
            "constipation-gut-health.html",

        "ibs-diet-lifestyle":
            "ibs-diet-lifestyle.html",

        "bloating-irregular-bowel":
            "bloating-irregular-bowel.html",

        "ayurvedic-digestive-care":
            "ayurvedic-digestive-care.html",
    },


    "piles": {

        "ayurvedic-approach-piles":
            "ayurvedic-approach-piles.html",

        "piles-constipation-ayurveda":
            "piles-constipation-ayurveda.html",

        "diet-lifestyle-piles":
            "diet-lifestyle-piles.html",

        "bleeding-pain-bowel-movements":
            "bleeding-pain-bowel-movements.html",

        "ayurvedic-care-piles":
            "ayurvedic-care-piles.html",
    },


    "kidney-stone": {

        "ayurvedic-approach-kidney-stones":
            "ayurvedic-approach-kidney-stones.html",

        "kidney-stone-symptoms":
            "kidney-stone-symptoms.html",

        "hydration-diet-kidney-stones":
            "hydration-diet-kidney-stones.html",

        "kidney-stones-lifestyle":
            "kidney-stones-lifestyle.html",

        "ayurveda-kidney-stone-care":
            "ayurveda-kidney-stone-care.html",
    },


    "migraine": {

        "ayurvedic-approach-migraine":
            "ayurvedic-approach-migraine.html",

        "migraine-triggers-ayurveda":
            "migraine-triggers-ayurveda.html",

        "migraine-sleep-lifestyle":
            "migraine-sleep-lifestyle.html",

        "diet-headache-patterns":
            "diet-headache-patterns.html",

        "shirodhara-migraine":
            "shirodhara-migraine.html",
    },


    "skin-disease": {

        "ayurvedic-approach-skin-health":
            "ayurvedic-approach-skin-health.html",

        "eczema-ayurvedic-perspective":
            "eczema-ayurvedic-perspective.html",

        "psoriasis-ayurvedic-lifestyle":
            "psoriasis-ayurvedic-lifestyle.html",

        "skin-diet-digestion":
            "skin-diet-digestion.html",

        "panchakarma-skin-concerns":
            "panchakarma-skin-concerns.html",
    },
}


def blog_article(request, topic, slug):

    topic_articles = BLOG_ARTICLES.get(topic)

    if not topic_articles:
        raise Http404("Blog topic not found")

    template_name = topic_articles.get(slug)

    if not template_name:
        raise Http404("Blog article not found")

    return render(
        request,
        template_name,
        {
            "blog_topic": topic,
            "blog_slug": slug,
        }
    )