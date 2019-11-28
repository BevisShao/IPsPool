import requests
from proxypool.setting import TEST_URL

# proxy = '96.9.90.90:8080'
proxy = '125.167.108.71:80'

proxies = {
    'http': 'http://' + proxy,
    'https': 'https://' + proxy,
}

print(TEST_URL)
response = requests.get('http://httpbin.org/get', proxies=proxies, )
print(response.text)
response = requests.get(TEST_URL, proxies=proxies, verify=False)
if response.status_code == 200:
    print('Successfully')
    print(response.text)