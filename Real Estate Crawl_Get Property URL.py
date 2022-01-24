import re
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome('C:\\Program Files (x86)\\Google\\Chrome\\chromedriver.exe', options=chrome_options)#r默认不转译
wait = WebDriverWait(driver, 10)


def searchCity(city):
    # Read city list
    try:
        #check whether there are properties on sale
        location = city + ', NY (City)'
        driver.get("http://www.mlsli.com/")
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#LocationBox'))
        )
        input.send_keys(location)  # search the property information of each city
        time.sleep(15)

        num = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mapsearch-count > span.mapsearch-count-total'))
        )

        num = num.text
        print(num)
        int_text = re.findall(r'\b\d+\b', num) 
        num = int(int_text[0])
        if num == 0:
            total = 0
            return total
        else:
            total = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mapsearch-results-all > div:nth-child(5) > div.mapsearch-results-paging-pages'))
            )
            total = total.text
            int_text = re.findall(r'\b\d+\b',total)
            total = int(int_text[-1])
            return total
    except TimeoutError:
        return searchCity(city)

def next_page():
    try:
        submit = wait.until(
            EC.element_to_be_clickable((By.NAME, 'ms-results-next'))
        )
        submit.click() 
        time.sleep(5)

       
        next_page()

def main():

    f = open('LongislandCitylist.txt', 'r', encoding='utf-8') # open the city list
    cities = f.readlines()
    for j in range(250, len(cities)):
        city = str(cities[j])
        print(city)
        print('Extracting info. from: ' + city + '......')
        n_page = searchCity(city)
        print(n_page)
        if n_page > 0:
            for i in range(1, n_page+1):
                outfile = 'Info of LongIslandCity\\' + city[:-2] + '_url_' + str(i) + '.txt' # get the url of each page
                print(outfile)
                file = open(outfile, "w")

                urls = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, """// *[ @ id = "mapsearch-results-body"] / div / div / div / div / div / a"""))
                )

               
                for url in urls:
                    str_url = str(url.get_attribute('href'))
                    file.write(str_url+'\n')
                file.close()



                if i < n_page:
                    next_page()

    f.close()

if __name__ == '__main__':
    main()
