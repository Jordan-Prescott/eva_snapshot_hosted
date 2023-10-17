from io import BytesIO
from rest_framework.decorators import api_view
from django.http import HttpResponse
import zipfile

import os

#TODO: Need a new view for authentication

@api_view(['GET'])
def getData(request):
    """ ...

    This should take a token and a group id.

    :param token: 
    :param group_id:
    """
    # this will return a zip file with snapshot output.

    
    """
    AUTH first of course

    1. Run EVASnapshot
    2. Collect files and zip
    3. Send 
    """


    buffer = BytesIO()
    folder_path = './eva_snapshot/output/'
    files = os.listdir(folder_path)

    with zipfile.ZipFile(buffer, 'w') as zipf:
        for file in files:
            if os.path.isfile(os.path.join(folder_path, file)):
                zipf.write(os.path.join(folder_path, file), file)
 
    buffer.seek(0)

    # Create an HttpResponse with the zip file as content
    response = HttpResponse(buffer.read(), content_type='application/zip')
    
    # Set the Content-Disposition header to prompt the user to download the file
    response['Content-Disposition'] = 'attachment; filename="eva.zip"'
    
    return response