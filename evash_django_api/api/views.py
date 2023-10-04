from rest_framework.response import Response
from rest_framework.decorators import api_view

from eva_snapshot.utils.tests import return_string

@api_view(['GET'])
def getData(request):
    string = return_string("This is my string")
    return Response(string)