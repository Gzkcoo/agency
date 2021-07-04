from bs4 import BeautifulSoup      #网页解析，获取数据
import re           #正则表达式，文字匹配
import urllib.request,urllib.error
import xlwt        #excel操作
import random
import pymysql.cursors


def main():

    ipList = ['27.43.188.200:9999', '58.253.154.234:9999', '60.187.113.250:9000', '182.34.26.240:9999']
    proxy_support = urllib.request.ProxyHandler({'http': random.choice(ipList)})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    baseurl = 'https://www.89ip.cn/'

    # 获取网页
    dataList = getData(baseurl)
    # savePath = 'agency.xlsx'

    # 保存数据
    saveDB(dataList)
    # saveData(dataList,savePath)


# 得到网页内容
def askUrl(url):
    head = {}
    head['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
    req = urllib.request.Request(url=url, headers=head)
    html = ''
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html


# 爬取网页
def getData(baseurl):
    dataList =[]
    for i in range(1,11):
        url = baseurl + 'index_' + str(i) + '.html'
        html = askUrl(url)
        # 逐一解析数据
        soup =BeautifulSoup(html, 'html.parser')
        for item in soup.select('tbody > tr'):
            item = str(item)
            data = []
            findContent = re.compile(r'<td>(.*?)</td>', re.S)
            content = re.findall(findContent, item)
            for j in range(0, 5):
                content[j] = content[j].strip()
            dataList.append(content)
    return dataList


# 保存数据到excel
def saveData(dataList,savePath):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('2021年', cell_overwrite_ok=True)
    col = ('序号','ip地址','端口号','地理位置','运营商','录入时间')
    for i in range(0,6):
        sheet.write(0,i,col[i])
    for i in range(0,len(dataList)):
        data = dataList[i]
        sheet.write(i+1,0,i+1)
        for j in range(0,5):
            sheet.write(i+1,j+1,data[j])
    book.save(savePath)  # 保存数据表



# 保存数据到数据库
def saveDB(dataList):
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='010426', db='guo', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        cursor = conn.cursor()
        for data in dataList:
            for index in range(len(data)):
                data[index] = '"' + data[index] + '"'
            sql = '''insert into agency(
                       ip,a_port,adress,operator,p_time) 
                       value (%s)''' % ','.join(data)
            cursor.execute(sql)
        conn.commit()  # 提交数据要不然数据库不刷新
    except Exception:
        print('增加到数据库失败')
    finally:
        conn.close()
        cursor.close()



def initDB():
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='010426', db='guo', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        cursor = conn.cursor()
        sql = '''create table agency (
                        id int(11)  primary key ,
                        ip varchar (30),
                        a_port varchar (10),
                        adress varchar(30) ,
                        operator varchar(30) ,
                        p_time varchar (30)
                        )
                '''
        cursor.execute(sql)
    except Exception:
        print('创建数据库失败')
    finally:
        conn.close()
        cursor.close()



if __name__ == '__main__':
    main()
    # initDB()
    print('爬取成功')
    # askUrl('https://www.89ip.cn/')