from io import BytesIO
from rest_framework.decorators import api_view
from django.http import HttpResponse

import zipfile
import os
from datetime import date

from eva_snapshot.main import main as es
from eva_snapshot.utils.files import remove_folder


#TODO: Need a new view for authentication

@api_view(['GET'])
def getData(request):
    """ ...
    """
    # this will return a zip file with snapshot output.
    account_id = request.GET.get('account_id', None)
    project_id = request.GET.get('project_id', None)
    group_id = request.GET.get('group_id', None)
    region = request.GET.get('region', None)
    customer_email = request.GET.get('customer_email', None)

    # check params
    if account_id == None or account_id == '':
        return HttpResponse('Error: no account_id specified')
    elif project_id == None or project_id == '':
        return HttpResponse('Error: no project_id specified')
    elif group_id == None or group_id == '':
            return HttpResponse('Error: no group_id specified')
    elif region == None or region == '':
            return HttpResponse('Error: no region specified')
    elif customer_email == None or customer_email == '':
            return HttpResponse('Error: no customer_email specified')
    
    #TODO: add auth here

    
    # run eva snapshot script
    es(account_id, project_id, group_id, region, customer_email)

    buffer = BytesIO()
    folder_path = f'./eva_snapshot/output/{group_id.lower()}/'

    with zipfile.ZipFile(buffer, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
 
    buffer.seek(0)

    # Create an HttpResponse with the zip file as content
    response = HttpResponse(buffer.read(), content_type='application/zip')
    
    # Set the Content-Disposition header to prompt the user to download the file
    response['Content-Disposition'] = f'attachment; filename="{group_id}_{date.today()}.zip"'
    
    remove_folder(folder_path)

    return response