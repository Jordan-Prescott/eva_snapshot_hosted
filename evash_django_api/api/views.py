from io import BytesIO
from rest_framework.decorators import api_view
from django.http import HttpResponse
import zipfile

import os

#TODO: Need a new view for authentication

@api_view(['GET'])
def getData(token, group_id):
    """ ...

    :param token: 
    :param group_id:
    """
    # this will return a zip file with snapshot output.


    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w') as zipf:
        # Add files to the zip archive, for example:
        zipf.write('./eva.jpg', 'eva.jpg')

    buffer.seek(0)

    # Create an HttpResponse with the zip file as content
    response = HttpResponse(buffer.read(), content_type='application/zip')
    
    # Set the Content-Disposition header to prompt the user to download the file
    response['Content-Disposition'] = 'attachment; filename="eva.zip"'
    
    return response