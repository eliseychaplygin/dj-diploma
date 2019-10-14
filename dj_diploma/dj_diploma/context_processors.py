from shop.models import Section

def menu_items(request):
    context = {'menu': Section.objects.all()}

    return context