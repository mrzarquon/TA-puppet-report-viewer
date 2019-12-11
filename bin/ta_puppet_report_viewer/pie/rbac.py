import sys
import json
import requests

# Handle both new and old versions of requests 
try:
  from requests.packages.urllib3.exceptions import InsecureRequestWarning
  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
  import urllib3
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#https://puppet.angrydome.org:4433/rbac-api/v1/auth/token
def genauthtoken(username, password, label, url, timeout=360):

  lifetime = "{}s".format(timeout*2)

  req = {
    'login': username,
    'password': password,
    'lifetime': lifetime,
    'label': label,
  }
  
  try:
    r = requests.post('{}/auth/token'.format(url), json=req, verify=False)
  except:
    print('Unexpected error:', sys.exc_info()[0])
    raise
  
  if r.status_code != 200:
    raise ValueError('Unable to get PE auth token', r.status_code, r.text)

  return json.loads(r.text)['token']
