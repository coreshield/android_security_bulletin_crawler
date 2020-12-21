import urllib3
import re
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_default_proxy():
    environ = os.environ
    if 'GITHUB_ACTIONS' in environ:
        if environ['GITHUB_ACTIONS'] == 'true':
            return {}

    return {
        'http': 'http://127.0.0.1:1087',
        'https': 'https://127.0.0.1:1087',
    }


versionMatcher = re.compile(r'[\d\.]+')
