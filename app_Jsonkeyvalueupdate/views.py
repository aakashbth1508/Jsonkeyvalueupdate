import os
import json
import mimetypes

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http.response import HttpResponse


class UpdateJSON(View):
    
    def get(self, request):
        return render(request, 'update_json.html')
    
    def post(self, request):
        action = request.POST.get('action', 0)
        try:  
            if action == '1':
                temp_file = request.FILES['json_file']
                file_content = temp_file.read()
                file_data = json.loads(file_content)
                data  = file_data
                block_data = file_data['merge']
                data = {"block_data":block_data,"filename":temp_file.name,"data":data}
                data['data'] = file_content.decode('utf-8')

                # data['data'] = file_content.decode('utf-8')
                return render(request, 'update_json.html', context=data)
            
            elif action == '2': 
                # filedate data get 
                req_data = request.POST
                # original data
                str_data = req_data.get('data')
                try:
                    str_data = json.loads(str_data)
                except Exception as E:
                    print(E)
                    raise ValueError('invalid filedata!') 
                # original data
                new_data={}
                keys =req_data.getlist('key')
                values = req_data.getlist('value')
                for (key, value) in zip(keys, values):
                    new_data[key] = value
                # Updating the temporary file data
                str_data['merge'] = new_data
                data= {"new_data":new_data,"filename":request.POST.get('filename'),"data":str_data}
                data['new_data'] = json.dumps(new_data, indent=4)
                # send  original file
                return render(request, 'update_json.html', context=data)

            elif action == '3':
                str_data = request.POST.get('data')
                filename = request.POST.get('filename')
                import ast
                try:
                    str_data = ast.literal_eval(str_data)
                    str_data= json.dumps(str_data, indent=4)
                except Exception as E:
                    raise ValueError('invalid data to download!') 
                response = HttpResponse(str_data, content_type='application/json')
                response['Content-Disposition'] = "attachment; filename=%s" % filename
                return response

        except Exception as e:
            return render(request, 'update_json.html', {'error': 'error: '+str(e)})

        # return render(request, 'update_json.html', {'error': 'error: Invalid action!'})
    



# temp_file = request.FILES['json_file']
# file_system_storage = FileSystemStorage()
# filename = file_system_storage.save(temp_file.name, temp_file)
# uploaded_file_url = file_system_storage.url(filename)

# with open(os.path.join(settings.MEDIA_ROOT, filename)) as f:
#     print(json.loads(f.read()))
# return render(request, 'update_json.html', {
#     'uploaded_file_url': uploaded_file_url
# })