import requests
from pyquery import PyQuery as pq
import re
import sys
import os
import apiInfo
from config import *
import json
import collections

BULLETIN_URL = 'https://source.android.com/security/bulletin'


def getTitleAndUrl(tdList):
    a = pq(tdList[0])('a')
    href = a.attr('href')
    title = href[href.rindex('/') + 1:]
    url = BULLETIN_URL + '/' + title
    return title, url


def getDateList(tdList):
    dateContent = pq(tdList[-1]).text()
    dateList = re.compile(r'\d{4}-\d{2}-\d{2}').findall(dateContent)
    return dateList


def writeFile(fileName, content):
    with open(fileName, 'w') as f:
        f.write(content)


def getAffectedAndroidVersion(title, url):
    titleMatcher = re.compile(r'android-(\d+)').findall(title)
    if len(titleMatcher) == 1:
        return titleMatcher

    resp = requests.get(url, verify=False, proxies=get_default_proxy())
    doc = pq(resp.text)
    tables = doc('table')
    versions = []
    for table in tables:
        rows = pq(table)('tr')

        # 判断哪一列是版本号
        headers = pq(rows[0])('th')
        valid = False
        for index, th in enumerate(headers):
            header_text = pq(th).text()
            if header_text == 'Updated AOSP versions' or header_text == 'Updated versions' or header_text == 'Affected versions' or header_text == 'Affected Versions':
                valid = True
                break

        if not valid:
            continue

        # 修正 index 值为负值，反向查找，兼容某些表格行，前几列留空的情况
        index = index - len(headers)

        for tr in rows[1:]:
            cells = pq(tr)('td')
            # 如果列数不足，则跳过
            if len(cells) + index <= 0:
                continue
            td = cells[index]
            versionText = pq(td).text()
            versionMatched = versionMatcher.findall(versionText)
            if versionMatched:
                versions += versionMatched

    versions = list(set(versions))
    # versions = filter(lambda version: versionMatcher.match(version), versions)
    # versions = list(versions)
    versions.sort(key=lambda version: list(map(int, version.split('.'))))
    return versions


if __name__ == "__main__":
    # 结果，用于存放 Android API 版本及对应的最新更新版本
    versionLastDate = {}

    # 获取 Android 版本名称与 API 对应关系
    apiDict = apiInfo.getApiDict()

    # 获取安全补丁数据
    resp = requests.get(BULLETIN_URL,  verify=False, proxies=get_default_proxy())
    trList = pq(resp.text)('table').children('tr')
    trList = trList.filter(lambda i, this: len(pq(this).children('td')) == 4)

    # 遍历获取每一个安全补丁版本
    for tr in trList:
        cells = pq(tr).children('td')

        # 解析得到 title, url, date 数据
        title, url = getTitleAndUrl(cells)
        dateList = getDateList(cells)

        if len(dateList) == 0:
            continue

        date = dateList[0]

        # 从 url 页面解析得到该补丁影响的 Android 版本名
        versionNames = getAffectedAndroidVersion(title, url)

        # 将 Android 版本名转为 Android API，并写入结果数据
        for version in versionNames:
            versionIntStr = str(apiDict[version])
            if versionIntStr in versionLastDate:
                lastDate = versionLastDate[versionIntStr]
                if date > lastDate:
                    versionLastDate[versionIntStr] = date
            else:
                versionLastDate[versionIntStr] = date

        print('title: ' + title + '\turl: ' + url +
              '\tdate: ' + date + '\tversion: ' + str(versionNames))

    versionLastDate['10'] = '2010'
    print('versionLastDate: ' + str(versionLastDate))
    for k, v in versionLastDate.items(): print(k, v)
    digest1 = hash(frozenset(versionLastDate.items()))
    print('digest1: ' + str(digest1))

    versionLastDate = collections.OrderedDict(sorted(versionLastDate.items()))

    # versionLastDate = sorted(versionLastDate)
    print('versionLastDate: ' + str(versionLastDate))
    for k, v in versionLastDate.items(): print(k, v)
    digest2 = hash(frozenset(versionLastDate.items()))
    print('digest2: ' + str(digest2))

    writeFile('result.json', json.dumps(versionLastDate))
