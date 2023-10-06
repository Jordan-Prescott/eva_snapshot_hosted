from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse

from eva_snapshot.utils.tests import return_string

import os

@api_view(['GET'])
def getData(request):
    
       # Define the path to the image file
    image_path = 'eva.jpg' # Adjust the file path as needed

    with open(image_path, 'rb') as image_file:
        return FileResponse(image_file)