import urllib3
import re
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_default_proxy():
    environ = os.environ
    if 'GITHUB_ACTIONS' in environ:
        if environ['GITHUB_ACTIONS'] == 'true':
            return {}
    
    http_proxy = {'http': environ['http_proxy']} if "http_proxy" else {}
    https_proxy = {'https': environ['https_proxy']} if "https_proxy" else {}
    return {**http_proxy, **https_proxy}


versionMatcher = re.compile(r'[\d\.]+')
