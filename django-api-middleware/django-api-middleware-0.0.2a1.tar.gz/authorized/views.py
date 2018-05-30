from django.http import JsonResponse
# Create your views here.
def sample(request):
    """
    Sample request for testing purposes
    """
    return JsonResponse({'title':'Cheers!','message':'Authorized application routes included.'}, status=200)
