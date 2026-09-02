from django.shortcuts import render


def ayurvedic_approach_pcod_pcos(request):
    return render(
        request,
        "ayurvedic-approach-pcod-pcos.html"
    )


def pcod_irregular_periods(request):
    return render(
        request,
        "pcod-irregular-periods.html"
    )


def pcod_weight_management(request):
    return render(
        request,
        "pcod-weight-management.html"
    )


def pcod_fertility(request):
    return render(
        request,
        "pcod-fertility.html"
    )


def panchakarma_for_pcod(request):
    return render(
        request,
        "panchakarma-for-pcod.html"
    )