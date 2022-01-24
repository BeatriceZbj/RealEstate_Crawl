#coding=utf-8
import requests
import re
import time
import random
import os
from bs4 import BeautifulSoup
import js2xml
import urllib.request
#如果strip()的参数为空，那么会默认删除字符串头和尾的空白字符(包括\n，\r，\t这些)
# Start a new session every time to keep the cache update in runtime.
''' get_html(url): Send http requests
    find_link(html): Find more links to crawl on the pages. Verify for the blocked.
    craw_main(f, html): Main page crawler.
    craw_sales(f, sales_link): Sales page crawler
    craw_neighbors(f, neighbors_link): Neignbors page crawler
    get_url(path): Get urls in seperate files and output in one file.
    read_url(file): Get urls from a single file.
    rename_saleslink(): Rename the downloaded webpages which are illegal to request by webservice.
    main(): Main entrance.
'''
s = requests.Session() #定义一个类似于cookie池的东西 可以实现cookie共享
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
# def getHtml(url):
#     html = urllib.request.urlopen(url).read()
#     return html

# def saveHtml(file_name, file_content):
    
#     with open(r'C:\Users\39118\Desktop\saleslink'+'\\' + str(file_name)+".html", "wb") as f:
#         f.write(file_content)
#         f.close()

def get_html(url):
    '''Send http request
    Args:
        url: the web url need to fetch
    Return:
        html: the webpage
    '''

    # Sometimes time gap may be needed between each request
    # time.sleep(5+random.random()*5) 
    
    # Http header, copy cookie at start 
    # head={'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    #html = s.get(url).text
    html=s.get(url,verify=False,headers=headers).text
    return html

def find_link(html):
    '''Get related links
    Find the needed links on the main page, judge whether blocked.
    Args:
        html: webpage returned by get_html()
    Return:
        links: needed links
    '''
    # Some websites have auto-block system, judge it by identifying special strings
    if re.search(r'distilIdentificationBlock',html):
        print("Error! Blocked!")
        return 0, 0
    else:
        sales_link = re.search(r'nearbyDiv.load\(Utils.AppPath(.*?),',html)
        #Some webpages don't have such links
        if not sales_link: 
            print("Error! Invalid!")
            return 0,0
        sales_link = "http://www.mlsli.com"+str(sales_link.group(1))[4:-1]
        print(sales_link)
 
        neighbors_link = re.search(r'https:\/\/www.rdesk.com\/(.*?);',html)
        neighbors_link = str(neighbors_link.group())[:-2]
        # print("Success")
    
    return sales_link, neighbors_link

def craw_main(f, html):
    # 先运行
    # print('Craw main is running')
    '''Craw the main page

    Get the information on the main page and output to file.
    Args:
        f: output stream 
        html: webpage returned by get_html()
    Output: 
        Write info to file
    Raise:
        IndexError: some tag organized differently.
    '''
   
    # street = re.search(r'full-address.*inline">(.*?),',html)
    #street =  str(street.group(1))
    # except:
    #     situation1
    #soup = BeautifulSoup(urlopen(html),"html.parser")
    html=s.get(html).text
  
    street = re.search(r'full-address.*inline">(.*?),',html)
    street = str(street.group(1))


    soup = BeautifulSoup(html,'lxml')




    city = soup.select('span[itemprop="addressLocality"]')[0].string
    state = soup.select('span[itemprop="addressRegion"]')[0].string
    postcode = soup.select('span[itemprop="postalCode"]')[0].string
    status = soup.select('span[class="ld-status"]')[0].select('span')[0].string



    try:
        price = soup.select('span[class="price"]')[0].string
    except:
        price = soup.select('span[class="price"]')[0].select('span')[0].string
        

    bed_bath = soup.select('div[class="bed-baths"]')[0].text
    MLS_num = soup.select('div[class="listing-number"]')[0].text
    # Some webpages don't have summary
    if soup.select('div[class="summary-remarks"]'):
        summary = soup.select('div[class="summary-remarks"]')[0].text
    else:
        summary = "" 


    basic_info = [street, city, state, postcode, status, price, bed_bath, MLS_num, summary]
    try:
        _list_summary = soup.select('div[class="summary-additional details-info"]')[0].select('div')
        list_summary = []
        for item in _list_summary:
            label = item.text.replace("\n","").split(':')
            if label[0]:
                label[1] = label[1].lstrip()#去左边头部
                list_summary.append(label)
    except:
        pass
    try:
        _list_info = soup.select('table[class="details-info-table1"]')[0].select('td')
        list_info = [] #创建一个空列表
        for item in _list_info:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").split(':')
            if label[0]:
                label[1] = label[1].lstrip()
                list_info.append(label)
    except:
        pass
    try:
        _room_info = soup.select('div[id="listingdetail-roominfo"]')[0].select('div[class="details-3-per-row details-text-data"]')
        room_info = []
        for item in _room_info:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").split(':')
            if label[0]:
                label[1] = label[1].lstrip()
                room_info.append(label)
    except:
        pass
    try:
        _int_info = soup.select('div[id="listingdetail-interiorfeatures1"]')[0].select('div[class="details-3-per-row details-text-data"]')
        int_info = []
        for item in _int_info:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").split(':')
            if label[0]:
                label[1] = label[1].lstrip()
                int_info.append(label)
    except:
        pass

    try:
        _ext_info = soup.select('div[id="listingdetail-exteriorfeatures"]')[2].select('div[class="details-3-per-row details-text-data"]')
        ext_info = []
        for item in _ext_info:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").split(':')
            if label[0]:
                label[1] = label[1].lstrip()
                ext_info.append(label)
    except:
         pass   
    try:
        _fin_info = soup.select('div[id="listingdetail-financial"]')[0].select('div[class="details-3-per-row details-text-data"]')
        fin_info = []
        for item in _fin_info:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").split(':')
            if label[0]:
                label[1] = label[1].lstrip()
                fin_info.append(label)
    except:
        pass

    try:
        _other_info = soup.select('div[id="listingdetail-financial"]')[1].select('div[class="details-1-per-row details-text-data"]')
        other_info = []
        for item in _other_info:
            label = item.text.replace("\n","").replace("\r","").replace("\t","")
            sp = label.index(":")
            label = [label[:sp+1],label[sp+1:]]
            if label[0]:
                label[1] = label[1].lstrip()
                other_info.append(label)

    print("Basic Info:\n", basic_info, "\n", file=f)
    print("Listing Summary:\n", list_summary, "\n", file=f)
    print("Listing Information:\n", list_info, "\n", file=f)
    print("Room Information:\n", room_info, "\n", file=f)
    print("Interior Features / Utilities:\n", int_info, "\n", file=f)
    print("Exterior / Lot Features:\n", ext_info, "\n", file=f)
    print("Financial Considerations:\n", fin_info, "\n", file=f)
    print("Other:\n", other_info, "\n", file=f)


def craw_sales(f, sales_link):
#     '''Craw the sales page
#     Get the information on the sales page and output to file.
#     Some website have block system, may use some auto-operate software to download the html files then crawl the local webpages.
#     Args:
#         f: output stream
#         sales_link: needed link returned by find_link
#     Output: 
#         Write info to file
#     Raise:
#         IndexError: some tag organized differently.
#     '''
#     print("Getting Sales")
#     # Overwrite sales_link, crawl local downloaded webpages.
#     # with open(r'C:\Users\39118\Desktop\HTML'+'\\'+sales_link[-9:]+'.html','w') as f:
#     #     print(sales_link,file=f) 
#         #withdraw the content of the file 

    html = getHtml(sales_link)
    # saveHtml(number, html)
    # sales_link = "http://localhost/"+sales_link[-9:]+".html"
    # html = get_html(sales_link)
    # print(html)
    time.sleep(25+random.random()*5)
    soup = BeautifulSoup(html,"lxml")
    # print(soup)
    tables = soup.select('table[class="price-history-tbl"]')
    # print(tables)
    
    _sales_thead = tables[0].select('thead th')
    sales_thead =[]
    for item in _sales_thead:
        label = item.text
        sales_thead.append(label)
    sales_thead[0] = '#'
    print(sales_thead)


    _sales_table = tables[0].select('tbody tr')
    sales_table = []
    
    for row in _sales_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").strip().lstrip()
            print(label)
            trow.append(label)
            
        sales_table.append(trow)
    print("Get sales table")
    _price_thead = tables[1].select('thead th')
    price_thead =[]
    for item in _price_thead:
        label = item.text.replace("\n","").replace("\r","").replace("\t","").strip().lstrip()
        print(label)
        price_thead.append(label)
    _price_table = tables[1].select('tbody tr')
    price_table = []
    for row in _price_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").replace("\xc2\xa0","").replace(" ","").strip().lstrip()
            trow.append(label)
        price_table.append(trow)
    print("Get price table")

    tables = soup.select('table[class="price-history-tbl property-tax-history-tbl"]')[0]
    _tax_thead = tables.select('thead th')
    tax_thead =[]
    for item in _tax_thead:
        label = item.textreplace("\n","").replace("\r","").replace("\t","")
        tax_thead.append(label)
    _tax_table = tables.select('tbody tr')
    tax_table = []
    for row in _tax_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").replace("\xc2\xa0","").replace(" ","").strip().lstrip()
            trow.append(label)
        tax_table.append(trow)
    print("Get tax table")

    print("Nearby Recent Sales:\n", sales_thead, "\n", sales_table, "\n", file=f)
    print("Price History:\n", price_thead, "\n", price_table, "\n", file=f)
    print("Tax History:\n", tax_thead, "\n", tax_table, "\n", file=f)
    soup = BeautifulSoup(html,"lxml")
    
    tables = soup.select('table[class="price-history-tbl"]')
    print(tables)
    
    _sales_thead = tables[0].select('thead th')
    # print(_sales_thead)
    sales_thead =[]
    for item in _sales_thead:
        label = item.text
        # print(label)
        sales_thead.append(label)
    sales_thead[0] = '#'
    # print(sales_thead)
    # 没有运行


    _sales_table = tables[0].select('tbody tr')
    sales_table = []
    
    for row in _sales_table:
        _trow = row.select('td')
        trow = []
        for item in _trow:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").strip().lstrip()
            # print(label)
            trow.append(label)
            
        sales_table.append(trow)
    # print("Get sales table")
    print("Nearby Recent Sales:\n", sales_thead, "\n", sales_table, "\n", file=f)
    
    try:
        _price_thead = tables[1].select('thead th')
        price_thead =[]
        for item in _price_thead:
            label = item.text.replace("\n","").replace("\r","").replace("\t","").strip().lstrip()
            # print(label)
            price_thead.append(label)
        _price_table = tables[1].select('tbody tr')
        price_table = []
        for row in _price_table:
            _trow = row.select('td')
            trow = []
            for item in _trow:
                label = item.text.replace("\n","").replace("\r","").replace("\t","").replace("\xc2\xa0","").replace(" ","").strip().lstrip()
                trow.append(label)
            price_table.append(trow)
        # print("Get price table")
        print("Price History:\n", price_thead, "\n", price_table, "\n", file=f)
    except:
        pass
  
    try:
        tables = soup.select('table[class="price-history-tbl property-tax-history-tbl"]')[0]
        _tax_thead = tables.select('thead th')
        # print(_tax_thead)
        # print('00000000000000000011111111111111')
        tax_thead =[]
        for item in _tax_thead:
            # print(item)
            label = item.text.replace("\n","").replace("\r","").replace("\t","")
            tax_thead.append(label)
        _tax_table = tables.select('tbody tr')
        tax_table = []
        for row in _tax_table:
            _trow = row.select('td')
            trow = []
            for item in _trow:
                label = item.text.replace("\n","").replace("\r","").replace("\t","").replace("\xc2\xa0","").replace(" ","").strip().lstrip()
                trow.append(label)
            tax_table.append(trow)
      
        # print("Get tax table")
        print("Tax History:\n", tax_thead, "\n", tax_table, "\n", file=f)
    except:
        pass

def craw_neighbors(f, neighbors_link):
    '''Craw the sales page
    Get the information on the neighbors page and output to file.
    This is an api page, so no blocked.
    Args:
        f: output stream
        neighbors_link: needed link returned by find_link
    Output: 
        Write info to file
    '''
    print("Getting Neighbors")
    # Re-construct neighbors_link to get different tabs data
    tab_name = ["HomeValues2","Demographics2", "Economy2", "SchoolsEducation", "Environment", "Commute"]
    print(tab_name)
    sp = neighbors_link.index("ReportName=")
    print(sp)
    neighbors_link1 = neighbors_link[:sp+11]
    neighbors_link2 = neighbors_link[sp+11:]
    sp = neighbors_link2.index("&")
    neighbors_link2 = neighbors_link2[sp:]
   

    for name in tab_name:
        neighbors_url = neighbors_link1+name+neighbors_link2
        print(neighbors_url)
      
        html = get_html(neighbors_url)
        data=[]
        print(html)
        soup=BeautifulSoup(html,'html.parser')
        items=soup.find_all('td',class_='DataCell DataCell')
        for i in items:
            tag=i.text
            data.append(tag)
            print
        soup=BeautifulSoup(html,'xml')
        content=soup.find_all('td',class_='DataCell DataCell')
        title=soup.find_all('td',class_='DataCell LabelDataCell')
        print(title)
        neidata=[]
        labeldata=[]

        for i in range(0,len(content)):
            if len(str(content[i]))<75:
                    print(content[i])
                    neidata.append(content[i].string)
        print(content)
        
                
#     # time.sleep(2+random.random()*3)
        data = re.findall(r'.Data = \[(.*?)\];',html)
        print(data)
        # Descriptions show at the end of every row, hidden on webpages
        for item in data:
            print(name, ":\n", item, "\n", file=f) 
        print("Get tab "+str(tab_name.index(name)))
        
# # def get_url(path):
# #     '''Get urls from seperate files
# #     At first the input was thousands of files, need to get all links in a list and output the links to a single file.
# #     Args:
# #         path: the path of files
# #     Returns:
# #         urls: list of urls
# #     '''
# #     files= os.listdir(path)
# #     urls = []  
# #     for file in files: 
# #         if not os.path.isdir(file):   
# #             f = open(path+"/"+file)
# #             iter_f = iter(f)
# #             i=0     # Only get the first 10 links, all the repeated links after 10.
# #             for line in iter_f:  
# #                 urls.append(line.strip())  
# #                 i=i+1
# #                 if i>9: break
# #     print("Total urls: ", len(urls)) 
# #     path = r"C:\Users\39118\Desktop\HTML"
# #     f = open("urls.txt","w")
# #     for url in urls:
# #         print(url, file=f)
# #     f.close()

# #     return urls

# # def read_url(file):
# #     '''Get urls from single file
# #     Args:
# #         path: the path of single file
# #     Returns:
# #         urls: list of urls
# #     '''
# #     urls = []
# #     f = open(file,"r")
# #     iter_f = iter(f)
# #     for line in iter_f:  
# #         urls.append(line.strip())
# #     print("Total urls: ", len(urls)) 
# #     return urls

# # def rename_saleslink():
# #     '''Rename the downloaded sales pages
# #     The downloaded filename format may be not able to request from localhost
# #     '''
# #     src = r"C:\Users\39118\Desktop\HTML\saleslinks"
# #     # saleslink
# #     filelist = os.listdir(src)
# #     for i in filelist:
# #         if i[:4] == "http":
# #             h_id = re.search(r'listingid=(.*?) .htm',i).group(1)
# #             os.rename(src+i,src+h_id+".html")

def main():
    path = r"C:\Users\39118\Desktop\Real Estate Data Crawl Python\HTMLLI"
    filelist = os.listdir(path)
    # Store the index of error pages 
    # error = [655,755,1129,1393,1471,2181,2402,2527,2683,2887,2934,2958,3203]
    
    # Start from breakpoint
    #len(filelist) is 485 and < 3204
    for i in range(8995,len(filelist)):
        print(i)
        print(filelist[i])
        # Request from local files
        url = "http://localhost/"+filelist[i]
        html = get_html(url)
    
        (sales_link, neighbors_link) = find_link(html)
        # if neighbors_link==0:
        #     pass
        # else:
        
        file ="BasicINFO\\"+str(i)+".txt"
            # f = open(file,"w")
            # print(url, file=f)
            # print(sales_link, file=f)
            # print(neighbors_link, file=f)
        
        with open(file,"w") as f:
                # print(url, file=f)
                # print(sales_link, file=f)
                # print(neighbors_link, file=f)
            craw_main(f, url)
            # craw_sales(f, sales_link)
                
                # craw_neighbors(f, neighbors_link)

            # # Raise a weird alarm noise when error, if you leave the machine alone.
            # print("Error!")
            # 发出声音 
        # f.close()
        # time.sleep(120+random.random()*60)

main()
