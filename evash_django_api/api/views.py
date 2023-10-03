from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def generate_snapshot(request):
    person = {'name': 'Jordan', 'age': '25'}
    return Response(person)