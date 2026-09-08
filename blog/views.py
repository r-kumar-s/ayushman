from django.shortcuts import render
from django.http import Http404


BLOG_ARTICLES = {

    "pcod-pcos": {

        "ayurvedic-approach-pcod-pcos":
            "pcod-pcos/ayurvedic-approach-pcod-pcos.html",

        "pcod-irregular-periods":
            "pcod-pcos/pcod-irregular-periods.html",

        "pcod-weight-management":
            "pcod-pcos/pcod-weight-management.html",

        "pcod-fertility":
            "pcod-pcos/pcod-fertility.html",

        "panchakarma-for-pcod":
            "pcod-pcos/panchakarma-for-pcod.html",
    },


    "thyroid": {

        "ayurveda-thyroid-health":
            "thyroid/ayurveda-thyroid-health.html",

        "thyroid-symptoms-ayurvedic-perspective":
            "thyroid/thyroid-symptoms-ayurvedic-perspective.html",

        "thyroid-diet-lifestyle":
            "thyroid/thyroid-diet-lifestyle.html",

        "ayurveda-hypothyroidism":
            "thyroid/ayurveda-hypothyroidism.html",

        "panchakarma-thyroid-care":
            "thyroid/panchakarma-thyroid-care.html",
    },


    "arthritis": {

        "ayurvedic-approach-arthritis":
            "arthritis/ayurvedic-approach-arthritis.html",

        "arthritis-joint-stiffness":
            "arthritis/arthritis-joint-stiffness.html",

        "ayurveda-knee-joint-pain":
            "arthritis/ayurveda-knee-joint-pain.html",

        "diet-lifestyle-joint-health":
            "arthritis/diet-lifestyle-joint-health.html",

        "panchakarma-arthritis":
            "arthritis/panchakarma-arthritis.html",
    },


    "acidity-gastritis": {

        "ayurvedic-approach-acidity":
            "acidity-gastritis/ayurvedic-approach-acidity.html",

        "gastritis-digestive-health":
            "acidity-gastritis/gastritis-digestive-health.html",

        "acidity-diet-lifestyle":
            "acidity-gastritis/acidity-diet-lifestyle.html",

        "heartburn-indigestion-ayurveda":
            "acidity-gastritis/heartburn-indigestion-ayurveda.html",

        "panchakarma-digestive-concerns":
            "acidity-gastritis/panchakarma-digestive-concerns.html",
    },


    "ibs-constipation": {

        "ayurvedic-approach-ibs":
            "ibs-constipation/ayurvedic-approach-ibs.html",

        "constipation-gut-health":
            "ibs-constipation/constipation-gut-health.html",

        "ibs-diet-lifestyle":
            "ibs-constipation/ibs-diet-lifestyle.html",

        "bloating-irregular-bowel":
            "ibs-constipation/bloating-irregular-bowel.html",

        "ayurvedic-digestive-care":
            "ibs-constipation/ayurvedic-digestive-care.html",
    },


    "piles": {

        "ayurvedic-approach-piles":
            "piles/ayurvedic-approach-piles.html",

        "piles-constipation-ayurveda":
            "piles/piles-constipation-ayurveda.html",

        "diet-lifestyle-piles":
            "piles/diet-lifestyle-piles.html",

        "bleeding-pain-bowel-movements":
            "piles/bleeding-pain-bowel-movements.html",

        "ayurvedic-care-piles":
            "piles/ayurvedic-care-piles.html",
    },


    "kidney-stone": {

        "ayurvedic-approach-kidney-stones":
            "kidney-stone/ayurvedic-approach-kidney-stones.html",

        "kidney-stone-symptoms":
            "kidney-stone/kidney-stone-symptoms.html",

        "hydration-diet-kidney-stones":
            "kidney-stone/hydration-diet-kidney-stones.html",

        "kidney-stones-lifestyle":
            "kidney-stone/kidney-stones-lifestyle.html",

        "ayurveda-kidney-stone-care":
            "kidney-stone/ayurveda-kidney-stone-care.html",
    },


    "migraine": {

        "ayurvedic-approach-migraine":
            "migraine/ayurvedic-approach-migraine.html",

        "migraine-triggers-ayurveda":
            "migraine/migraine-triggers-ayurveda.html",

        "migraine-sleep-lifestyle":
            "migraine/migraine-sleep-lifestyle.html",

        "diet-headache-patterns":
            "migraine/diet-headache-patterns.html",

        "shirodhara-migraine":
            "migraine/shirodhara-migraine.html",
    },


    "skin-disease": {

        "ayurvedic-approach-skin-health":
            "skin-disease/ayurvedic-approach-skin-health.html",

        "eczema-ayurvedic-perspective":
            "skin-disease/eczema-ayurvedic-perspective.html",

        "psoriasis-ayurvedic-lifestyle":
            "skin-disease/psoriasis-ayurvedic-lifestyle.html",

        "skin-diet-digestion":
            "skin-disease/skin-diet-digestion.html",

        "panchakarma-skin-concerns":
            "skin-disease/panchakarma-skin-concerns.html",
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