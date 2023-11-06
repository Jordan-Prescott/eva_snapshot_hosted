from io import BytesIO
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import HttpResponse

from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404


import zipfile
import os
from datetime import date

from eva_snapshot.eva_snapshot import main as es

@api_view(['POST'])
def auth_token(request):
     user = get_object_or_404(User, username=request.data['username'])
     if not user.check_password(request.data['password']):
          return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
     token, created = Token.objects.get_or_create(user=user)
     serializer = UserSerializer(instance=user)
     print(token.key)
     return Response({"token": token.key, "user": serializer.data})

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def eva_snapshot(request):
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
        return Response({"Error": "no account_id specified"}, status=status.HTTP_400_BAD_REQUEST)
    elif project_id == None or project_id == '':
        return HttpResponse({"Error": "no project_id specified"}, status=status.HTTP_400_BAD_REQUEST)
    elif group_id == None or group_id == '':
            return HttpResponse({"Error": "no group_id specified"}, status=status.HTTP_400_BAD_REQUEST)
    elif region == None or region == '':
            return HttpResponse({"Error": "no region specified"}, status=status.HTTP_400_BAD_REQUEST)
    elif customer_email == None or customer_email == '':
            return HttpResponse({"Error": "no customer_email specified"}, status=status.HTTP_400_BAD_REQUEST)

    
    # run eva snapshot script
    #es(account_id, project_id, group_id, region, customer_email)


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
    response['Content-Disposition'] = f'attachment; filename="{group_id}_{date.today()}.zip"'
    
    return response