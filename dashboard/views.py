from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
from firebase import firebase  
import requests
from django.http import HttpResponse, JsonResponse, QueryDict
import json
from django.views.decorators.csrf import csrf_exempt

fbase = firebase.FirebaseApplication('https://beelamo-a3577.firebaseio.com/', None)

@csrf_exempt
def create_sandox_user(request):
    mydata = json.loads(request.body)
    url2 = 'https://sandbox.momodeveloper.mtn.com/v1_0/apiuser'
    headers2 = {
        "Content-Type":'application/json',
        "X-Reference-Id":mydata.get('X-Reference-Id'),
        "Ocp-Apim-Subscription-Key":mydata.get('Ocp-Apim-Subscription-Key')
        }
    result = requests.post(url2, headers=headers2, data= {
        'providerCallbackHost':
            'http://webhook.site/38949764-f87b-4c35-8927-845f767f8845'
      })
    



@csrf_exempt 
def get_user_account_balance(request):
    url = 'https://sandbox.momodeveloper.mtn.com/disbursement/v1_0/account/balance'
    mydata = json.loads(request.body)
    token  = mydata.get('token')
    ocp_apim_subscription_key = mydata.get('ocp_apim_subscription_key')
    headers = {
            'authorization': 'Bearer '+ token,
            "X-Target-Environment": "sandbox",
            "Ocp-Apim-Subscription-Key": ocp_apim_subscription_key
            }
    
    result = requests.get(url, headers=headers)
    response = {}
    if result.status_code == 200 and result.status_code != '':
        response['availableBalance'] = json.loads(result.text)['availableBalance']
        response['currency'] = json.loads(result.text)['currency']

    elif result.status_code !='' and result.status_code != 200:
        response['message'] = json.loads(result.text)['message']
        response['code'] = json.loads(result.text)['code']  
    else:
        response['message'] = 'error'
        response['code'] = 'un Known'

    return JsonResponse(status = result.status_code, data = response, safe=False)

def file_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        # services
        df = pd.read_excel(myfile, sheet_name = 'service')
        for index, row in df.iterrows():
        	data = {
        		'name':row['name'],
        		'description':row['description'] if str(row['description']) != 'nan' else ''
        	}
        	service = fbase.put('/service/',row['id'], data) 

        # ratings
        df1 = pd.read_excel(myfile, sheet_name = 'rate')
        for  index, row in df1.iterrows():
        	data = {
        		'min':row['min'],
        		'max':row['max']
        	}
        	service = fbase.put('/rate/',row['id'], data) 

        # subservices
        df2 = pd.read_excel(myfile, sheet_name = 'subservice')
        for  index, row in df2.iterrows():
        	print(row['description'])
        	data = {
        		'name':row['name'],
        		'serviceid':row['serviceid'],
        		'description':row['description'] if str(row['description']) !='nan' else '',
        		'type':row['type'] if str(row['type']) !='nan' else '',
        		'parentid':row['parentid'] if str(row['parentid']) !='nan' else ''
        	}
        	service = fbase.put('/subservice/',row['id'], data) 

        # services ratings
        df3 = pd.read_excel(myfile, sheet_name = 'service_rate')
        for  index, row in df3.iterrows():
        	data = {
        		'sub_serviceid':row['sub_serviceid'],
        		'rateid':row['rateid']
        	}
        	service = fbase.put('/service_rate/',row['id'], data) 

        # # services ratings charge
        df4 = pd.read_excel(myfile, sheet_name = 'charge')
        for  index, row in df4.iterrows():
        	data = {
        		'newcost':row['newcost'],
        		'servicerateid':row['servicerateid'],
        		'oldcost':row['oldcost'] if str(row['oldcost']) != 'nan' else '',
        	}
        	service = fbase.put('/charge/',row['id'], data)

        # # services ratings charge
        df5 = pd.read_excel(myfile, sheet_name = 'tax')
        for  index, row in df5.iterrows():
        	data = {
        		'chargeid':row['chargeid'],
        		'name':row['name'],
        		'percent':row['percent'] if str(row['percent']) != 'nan' else '',
        		'value':row['value'] if str(row['value']) != 'nan' else ''
        	}
        	service = fbase.put('/tax/',row['id'], data)

        return render(request, 'upload.html', {
            'uploaded_file_url': uploaded_file_url, 'message':'Successfully'
        })
    return render(request, 'upload.html')