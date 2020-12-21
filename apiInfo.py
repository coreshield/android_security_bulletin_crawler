import requests
import re
from pyquery import PyQuery as pq
from config import *

__api_dict = {
    '4.4': 19,
    '4.4.0': 19,
    '4.4.1': 19,
    '4.4.2': 19,
    '4.4.3': 19,
    '4.4.4': 19,

    '5.0': 21,
    '5.0.1': 21,
    '5.0.2': 21,

    '5.1': 22,
    '5.1.1': 22,
    '5.1.2': 22,

    '6.0': 23,
    '6.0.1': 23,
    '6.1': 23,

    '7.0': 24,

    '7.1': 25,
    '7.1.1': 25,
    '7.1.2': 25,

    '8.0': 26,
    '8.0.0': 26,

    '8.1': 27,
    '8.1.0': 27,

    '9': 28,
    '10': 29,
    '11': 30,
}

# TODO: 可以通过爬虫获取版本名称 → API 对应关系，但其 8.1 及以下的版本名称与安全补丁页显示的名称有细节差距
# https://source.android.com/setup/start/build-numbers


def getApiDict():
    url = 'https://source.android.com/setup/start/build-numbers'
    resp = requests.get(url, verify=False, proxies=get_default_proxy())
    # print(resp.text)
    trList = pq(resp.text)(
        'th:contains("Codename")').parent().parent().parent()('tr')

    for tr in trList:
        tdList = pq(tr)('td')

        if len(tdList) < 3:
            continue

        text = pq(tdList[1]).text()
        versionNames = versionMatcher.findall(text)
        if len(versionNames) == 0:
            continue

        text = pq(tdList[2]).text()
        apiLevelMatcher = re.compile(r'API level (\d+)').match(text)
        if apiLevelMatcher:
            apiLevel = apiLevelMatcher.group(1)
        else:
            continue

        for version in versionNames:
            __api_dict[version] = int(apiLevel)

    # print(__api_dict)

    return __api_dict
