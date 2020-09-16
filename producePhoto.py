import requests, json,sys,os,glob, time
import status_codes

if len(sys.argv) < 2:
    # To run in terminal:
    # python producePhoto.py /Users/../Documents/.../orthophoto/images
    print("Usage: ./{} <path_to_images>".format(sys.argv[0]))
    sys.exit(1)

types = ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG")
images_list = []
for t in types:
    images_list.extend(glob.glob(os.path.join(sys.argv[1], t)))

if len(images_list) < 1:
    print("Need at least 2 images")
    sys.exit(1)
else:
    print("Found {} images".format(len(images_list)))

# api call
res = requests.post('http://localhost:8000/api/token-auth/', 
                    data={'username': 'gavinwebodm',
                          'password': 'Gavin1234'}).json()

if 'token' in res:
    print("Logged-in!")
    token = res['token']
    # api call
    res = requests.post('http://localhost:8000/api/projects/', 
                    headers={'Authorization': 'JWT {}'.format(token)},
                    data={'name': 'Combine Images Test'}).json()
    project_id = res['id']

    # shortcut way: list out all images in the same folder
    # images = [
    # ('images', ('1.jpg', open('1.jpg', 'rb'), 'image/jpg')), 
    # ('images', ('2.jpg', open('2.jpg', 'rb'), 'image/jpg')),
    # ('images', ('3.jpg', open('3.jpg', 'rb'), 'image/jpg')),
    # ('images', ('4.jpg', open('4.jpg', 'rb'), 'image/jpg')),
    # ('images', ('5.jpg', open('5.jpg', 'rb'), 'image/jpg'))
    # ]

    images = [('images', (os.path.basename(file), open(file, 'rb'), 'image/jpg')) for file in images_list]

    options = json.dumps([{'name': "orthophoto-resolution", 'value': 5}])

    res = requests.post('http://localhost:8000/api/projects/{}/tasks/'.format(project_id), 
            headers={'Authorization': 'JWT {}'.format(token)},
            files=images,
            data={
                'options': options
            }).json()

    task_id = res['id']

    while True:
    	res = requests.get('http://localhost:8000/api/projects/{}/tasks/{}/'.format(project_id, task_id), 
                headers={'Authorization': 'JWT {}'.format(token)}).json()
    	if res['status'] == status_codes.COMPLETED:
    		print("Task has completed!")
    		break
    	elif res['status'] == status_codes.FAILED:
    		print("Task failed: {}".format(res))
    		sys.exit(1)
    	else:
    		print("Please wait! Still processing...")
    		time.sleep(3)
    res = requests.get("http://localhost:8000/api/projects/{}/tasks/{}/download/orthophoto.tif".format(project_id, task_id), 
                    headers={'Authorization': 'JWT {}'.format(token)},
                    stream=True)
    with open("orthophoto.tif", 'wb') as f:
    	for chunk in res.iter_content(chunk_size=1024): 
    		if chunk:
    			f.write(chunk)
    print("Saved ./orthophoto.tif")
else:
    print("Invalid credentials!") # login failed