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

class CalculateValue(View):

    def get(self, request):
        return render(request, 'calculate_json.html')

    def post(self, request):
        action = request.POST.get('action', 0)
        if action == '1':
            try:
                temp_file = request.FILES['json_file']
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, temp_file.name)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, temp_file.name))

                file_system_storage = FileSystemStorage()
                filename = file_system_storage.save(temp_file.name, temp_file)

                with open(os.path.join(settings.MEDIA_ROOT, filename), 'r') as f:
                    show_data = f.read()

                data = json.loads(show_data)
                merge_data = data.get('merge', None)
                if merge_data:
                    merge_data_to_display = []
                    for i in merge_data:
                        if type(i["replace"]) is str:
                            merge_data_to_display.append(f'{i["find"]} = "{i["replace"]}"')
                        else:
                            merge_data_to_display.append(f'{i["find"]} = {i["replace"]}')
                else:
                    merge_data_to_display = []

                context = {
                    'filename': filename,
                    'show_data': 'merge: '+json.dumps(merge_data, indent=4),
                    'script_block': '\n'.join(merge_data_to_display)
                }
                if not merge_data:
                    context['error'] = 'Invalid json file uploaded, It does not contain "merge" block!'
                return render(request, 'calculate_json.html', context)
            except Exception as e:
                return render(request, 'calculate_json.html', {'error': str(e)})

        elif action == '3':
            try:
                filename = request.POST.get('filename')
                script_block = request.POST.get('script_block')

                with open(os.path.join(settings.MEDIA_ROOT, filename), 'r') as f:
                    show_data = json.loads(f.read())

                script_block_vars = []
                script_block_lines = script_block.split("\n")
                for i in script_block_lines:
                    if i and "=" in i:
                        vn = i.split("=")[0]
                        if vn:
                            for j in [' ', '+', '-', '%', '/', '*', '//', '**']:
                                vn = vn.replace(j, "")
                            script_block_vars.append(vn)

                script_block_vars = set(script_block_vars)
                script_name = os.path.join(settings.MEDIA_ROOT, filename + '_script.py')
                
                script_name = script_name.replace('(', '').replace(')', '').replace(' ', '')
                print(script_name)
                with open(script_name, 'w') as f:
                    for line in script_block_lines:
                        if not 'print(' in line:
                            f.write(line)

                    dict_str = '\ndata = {'
                    for i in script_block_vars:
                        dict_str += f'"{i}": {i}, '
                    dict_str += '}\n'

                    f.write(dict_str)
                    f.write('\nimport json')
                    f.write('\nprint(json.dumps(data))\n')

                # this will run the shell command `cat me` and capture stdout and stderr
                proc = Popen(["py", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # this will wait for the process to finish.
                proc.wait()
                read_data = proc.stdout.read().decode()
                read_err = proc.stderr.read().decode()
                if read_err:
                    context = {
                        'filename': filename,
                        'show_data': {},
                        'script_block': script_block,
                        'error': read_err
                    }
                    return render(request, 'calculate_json.html', context)
                else:
                    updated_data = json.loads(read_data)
                    merge_data = show_data.get('merge', None)
                    if merge_data:
                        for i in merge_data:
                            if i['find'] in updated_data:
                                i['replace'] = updated_data[i['find']]

                show_data['merge'] = merge_data

                with open(os.path.join(settings.MEDIA_ROOT, filename), 'w') as f:
                    f.write(json.dumps(show_data, indent=4))

                context = {
                    'filename': filename,
                    'show_data': 'merge: ' + json.dumps(merge_data, indent=4),
                    'script_block': script_block
                }
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