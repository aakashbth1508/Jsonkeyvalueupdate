import os
import json
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import subprocess
from subprocess import Popen
from django.http.response import HttpResponse, Http404

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
                newdata = []
                keys =req_data.getlist('key')
                values = req_data.getlist('value')
                for (x,y) in zip(keys, values):
                    new_data={}
                    new_data["find"] = x
                    new_data["replace"] = y
                    newdata.append(new_data)
                str_data['merge'] = newdata
                data= {"new_data":newdata,"filename":request.POST.get('filename'),"data":str_data}
                data['new_data'] = json.dumps(newdata, indent=4)
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

def json_extract(obj, key):
    arr = []

    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

def update_data(data, updated_data):
    if type(data) is dict:
        for k, v in data.items():
            if k in updated_data:
                for k1, v1 in updated_data.items():
                    if k1 in data:
                        if type(data[k1]) != dict:
                            data[k1] = v1
            else:
                update_data(v, updated_data)
    elif type(data) is list:
        for i in data:
            update_data(i, updated_data)

    return data

class CalculateValue(View):

    def get(self, request):
        return render(request, 'calculate_json.html')

    def post(self, request):
        action = request.POST.get('action', 0)
        if action == '1':
            try:
                temp_file = request.FILES['json_file']
                file_content = temp_file.read()
                file_data = json.loads(file_content)
                data  = file_data
                block_data = file_data['merge']
                s = ''
                for data1 in block_data:
                    value = str(data1['replace'])
                    if value.isnumeric():
                        value
                    else:
                        value = '"' + value + '"'
                    s += data1['find'] + ' = ' + value + '\n'
                data = {"block_data":s,"filename":temp_file.name,"data":data}
                data['data'] = file_content.decode('utf-8')
                return render(request, 'calculate_json.html', context=data)
            except Exception as e:
                return render(request, 'calculate_json.html', {'error': str(e)})

        elif action == '3':
            try:
                filename = request.POST.get('filename')
                script_block = request.POST.get('script_block')
                data = request.POST.get('data')

                with open(os.path.join(settings.MEDIA_ROOT, filename), 'r') as f:
                    show_data = json.loads(f.read())

                if not temp_keys.strip():
                    return render(request, 'calculate_json.html', {
                        'filename': filename,
                        'keys_to_update': ', '.join(script_block),
                        'show_data': json.dumps(show_data, indent=4),
                        'script_block': script_block,
                        'error': 'please add atleast 1 key to update.'
                    })

                temp_keys = [i.strip() for i in temp_keys.split(',') if i]
                keys_to_update = []
                for i in temp_keys:
                    i = i.strip()
                    if '=' in i:
                        f = '==' in i or '!=' in i or '>=' in i or '<=' in i or '!=' in i or 'in' in i or 'not' in i
                        if not f:
                            keys_to_update.append(i)

                temp = script_block.split("\n")
                l = [i.split("=")[0].strip().replace(" ", "") for i in temp if i and "=" in i]
                s = set([i for i in l if i.isalpha() or i.isalnum()])

                script_name = os.path.join(settings.MEDIA_ROOT, filename + '_script.py')
                script_name = script_name.replace('(', '').replace(')', '').replace(' ', '')

                with open(script_name, 'w') as f:
                    f.write(script_block)

                    dict_str = '\ndata = {'
                    for i in s:
                        dict_str += f'"{i}": {i}, '
                    dict_str += '}\n'

                    f.write(dict_str)
                    f.write('\nimport json')
                    f.write('\nprint(json.dumps(data))\n')

                # this will run the shell command `cat me` and capture stdout and stderr
                proc = Popen(["python3", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # this will wait for the process to finish.
                proc.wait()
                read_data = proc.stdout.read().decode()
                read_err = proc.stderr.read().decode()
                if read_err:
                    context = {
                        'filename': filename,
                        'show_data': {},
                        'keys_to_update': ', '.join(temp_keys),
                        'script_block': script_block,
                        'error': read_err
                    }
                    return render(request, 'calculate_json.html', context)
                else:
                    updated_data = json.loads(read_data)

                show_data = update_data(data=show_data, updated_data=updated_data)

                with open(os.path.join(settings.MEDIA_ROOT, filename), 'w') as f:
                    f.write(json.dumps(show_data, indent=4))

                context = {'filename': filename, 'show_data': json.dumps(show_data, indent=4), 'keys_to_update': ', '.join(temp_keys), 'script_block': script_block}
                return render(request, 'calculate_json.html', context)
            except IsADirectoryError as e:
                return render(request, 'calculate_json.html', {'error': 'Please upload a file before proceed!'})
            except Exception as e:
                return render(request, 'calculate_json.html', {'error': e})

        return render(request, 'calculate_json.html', {'error': 'Invalid action!'})


def download(request, path):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force-download")  # content_type="application/json")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    except:
        pass
    raise Http404