import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_proxy = {
    'http': 'http://127.0.0.1:1087',
    'https': 'https://127.0.0.1:1087',
}

versionMatcher = re.compile(r'[\d\.]+')
