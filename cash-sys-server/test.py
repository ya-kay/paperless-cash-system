import requests
with open('./test.pdf','rb') as f:
	r = requests.post('http://192.168.178.82:8125/post', files={'test.pdf':f}, headers={'content-type': 'application/pdf'})