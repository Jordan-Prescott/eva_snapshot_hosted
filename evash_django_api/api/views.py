from io import BytesIO
from rest_framework.decorators import api_view
from django.http import HttpResponse
import zipfile

from eva_snapshot.eva_snapshot import main as es

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
    account_id = request.GET.get('account_id', None)
    project_id = request.GET.get('project_id', None)
    group_id = request.GET.get('group_id', None)
    region = request.GET.get('region', None)
    customer_email = request.GET.get('email', None)

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

    
    # run eva snapshot script
    es(account_id, project_id, group_id, region, customer_email)
    
    """
    AUTH first of course

    1. Run EVASnapshot
    2. Collect files and zip
    3. Send 
    4. Remove files 
    """



    # buffer = BytesIO()
    # folder_path = './eva_snapshot/output/'
    # files = os.listdir(folder_path)

    # with zipfile.ZipFile(buffer, 'w') as zipf:
    #     for file in files:
    #         if os.path.isfile(os.path.join(folder_path, file)):
    #             zipf.write(os.path.join(folder_path, file), file)
 
    # buffer.seek(0)

    # # Create an HttpResponse with the zip file as content
    # response = HttpResponse(buffer.read(), content_type='application/zip')
    
    # # Set the Content-Disposition header to prompt the user to download the file
    # #TODO: insert date in zip name
    # response['Content-Disposition'] = 'attachment; filename="eva_snaphot.zip"'
    
    # return response

    return HttpResponse(f'Group id is: {group_id}')