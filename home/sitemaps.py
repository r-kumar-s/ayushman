from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return [
                'index',
                'about',
                'thyroid',
                'gastrointestinal',
                'lungs',
                'hematological',
                'stone',
                'tumor',
                'arthritis',
                'skin',
                'female-genital-organ',
                'basti',
                'nasya',
                'raktamokshana',
                'vamana',
                'virechana',
                'udarshodhak',
                'contact',
                'dr_sushma_tiwary', 
                'shirodhara',
                'abhyanga'
            ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'index':
            return 1.0
        return 0.8