import requests
from pyquery import PyQuery as pq
import re
import apiInfo
from config import *

baseUrl = 'https://source.android.com/security/bulletin'


def getTitleAndUrl(tdList):
    a = pq(tdList[0])('a')
    href = a.attr('href')
    title = href[href.rindex('/') + 1:]
    url = baseUrl + '/' + title
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

    resp = requests.get(url, verify=False, proxies=default_proxy)
    doc = pq(resp.text)
    tableList = doc('table')
    versions = []
    for table in tableList:
        trList = pq(table)('tr')

        # 判断哪一列是版本号
        thList = pq(trList[0])('th')
        valid = False
        for index, th in enumerate(thList):
            thText = pq(th).text()
            if thText == 'Updated AOSP versions' or thText == 'Updated versions' or thText == 'Affected versions' or thText == 'Affected Versions':
                valid = True
                break

        if not valid:
            continue

        # 修正 index 值为负值，反向查找，兼容某些表格行，前几列留空的情况
        index = index - len(thList)

        for tr in trList[1:]:
            tdList = pq(tr)('td')
            # 如果列数不足，则跳过
            if len(tdList) + index <= 0:
                continue
            td = tdList[index]
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
    resp = requests.get(baseUrl,  verify=False, proxies=default_proxy)
    trList = pq(resp.text)('table').children('tr')
    trList = trList.filter(lambda i, this: len(pq(this).children('td')) == 4)

    # 遍历获取每一个安全补丁版本
    for tr in trList:
        tdList = pq(tr).children('td')

        # 解析得到 title, url, date 数据
        title, url = getTitleAndUrl(tdList)
        dateList = getDateList(tdList)

        if len(dateList) == 0:
            continue

        date = dateList[0]

        # 从 url 页面解析得到该补丁影响的 Android 版本名
        versions = getAffectedAndroidVersion(title, url)

        # 将 Android 版本名转为 Android API，并写入结果数据
        for version in versions:
            versionInt = apiDict[version]
            if versionInt in versionLastDate:
                lastDate = versionLastDate[versionInt]
                if date > lastDate:
                    versionLastDate[versionInt] = date
            else:
                versionLastDate[versionInt] = date

        # print('title: ' + title + '\turl: ' + url +
        #       '\tdate: ' + date + '\tversion: ' + str(versions))

    print(versionLastDate)
