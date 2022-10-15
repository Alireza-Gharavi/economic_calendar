from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from V1.logger import logger
import datetime

# os.environ['PATH'] += ':webdriver/'

def Scraper(year, week):                # this function will scrape the data from www.babypips.com site given inputs year and week number and return the records of economic calendar as dictionaries in a list named info_list
    """ scrape the data of economic calendar at www.babypips.com

    Parameters
    ----------
    year : str 
           a sting representing year number.
           e.x. year='2022'
    week : str 
           a string representing week number. 
           e.x. week='17'

    Returns
    -------
    info_list : a list of dictionaries, each dictionary represents a record of economic calendar.

    """
    year = str(year)
    week = f"{int(week):02}"

    attempt_counter = 0

    months = {
        'Jan' : '01',
        'Feb' : '02',
        'Mar' : '03',
        'Apr' : '04',
        'May' : '05',
        'Jun' : '06',
        'Jul' : '07',
        'Aug' : '08',
        'Sep' : '09',
        'Oct' : '10',
        'Nov' : '11',
        'Dec' : '12'
    }


    # blocks = <div> , 'Section-module__container___WUPgM Table-module__day___As54H'
    # day_number = <div> , 'Table-module__dayNumber___dyJpm'
    # week_day = <td> , 'Table-module__weekday___p3Buh'
    # time = <td> , 'Table-module__time___IHBtp'
    # currency = <td> , 'Table-module__currency___gSAJ5'
    # name = <td> , 'Table-module__name___FugPe'
    # impact = <td> , 'Table-module__impact___kYuei'
    # actual = <td> , 'Table-module__actual___kzVNq'
    # forecast = <td> , 'Table-module__forecast___WchYX'
    # previous = <td> , 'Table-module__previous___F0PHu'

    url = f'https://www.babypips.com/economic-calendar?week={year}-W{week}'
    
    driver = initializer()

    try :
        attempt_counter += 1
        driver.get(url)
    except :
        logger.error(f"connection to the {url} can't be established.")
        if attempt_counter <= 3 :
            logger.info(f'connecting to the {url}, attempt : {attempt_counter}')
            Scraper(year, week)
        else :
            return -1

    
    try:
        driver.maximize_window()
        driver.implicitly_wait(50)
    except Exception as e :
        logger.error("unknow error occured :",e)

    if len(driver.page_source) > 200 :
        try :
            interact_with_site(driver)
        except Exception as e:
            logger.error(f'selenium unable to intract with {url}. {e}')
            if attempt_counter <= 3 :
                logger.info(f'rerequesting to the {url}, attempt : {attempt_counter}')
                Scraper(year, week)
            else :
                return -1
    else :
        logger.error(f"source of the requested page does not scraped properly.")
        if attempt_counter <= 3 :
                logger.info(f'rerequesting to the {url}, attempt : {attempt_counter}')
                Scraper(year, week)
        else :
            return -1

    res = driver.page_source
    soup = BeautifulSoup(res, 'lxml')

    driver.quit()
    

    try :
        info_list = []
        info = {'year' : None, 'week' : None, 'month_num' : None , 'month_name' : None, 'day_number' : None , 'week_day' : None, 'time' : None , 'currency_name' : None , 'source_name' : None , 'impact' : None , 'actual' : None , 'forecast' : None , 'previous' : None , 'timestamp' : None}
        blocks = soup.find_all('div', class_='Section-module__container___WUPgM Table-module__day___As54H')

        for i in range(len(blocks)) :
            info['year'] = year
            info['week'] = f'W{week}'
            info['month_name'] = blocks[i].table.thead.tr.td.find('div', class_='Table-module__month___PGbXI').text
            if info['week'] == 'W01' and info['month_name']=='Dec' :
                continue
            info['month_num'] = months[info['month_name']]
            info['day_number'] = blocks[i].table.thead.tr.td.find('div', class_='Table-module__dayNumber___dyJpm').text
            info['week_day'] = blocks[i].table.tr.find('td', class_='Table-module__weekday___p3Buh').text
            
            recs_list = blocks[i].table.tbody.find_all('tr')

            for j in range(len(recs_list)) :
                info['time'] = recs_list[j].find('td' , class_='Table-module__time___IHBtp').text
                info['currency_name'] = recs_list[j].find('td', class_='Table-module__currency___gSAJ5').text
                info['source_name'] = recs_list[j].find('td', class_='Table-module__name___FugPe').text
                info['impact'] = recs_list[j].find('td', class_='Table-module__impact___kYuei').text
                info['actual'] = recs_list[j].find('td', class_='Table-module__actual___kzVNq').text
                info['forecast'] = recs_list[j].find('td', class_='Table-module__forecast___WchYX').text
                info['previous'] = recs_list[j].find('td', class_='Table-module__previous___F0PHu').text

                info['timestamp'] = timestamp_calc(info)

                info_list.append(info.copy())
            
        return info_list
    except :
        logger.error(f'an error occured during parsing the extracted data from {url} by BeatifulSoup.')


def timestamp_calc(info):
    """this function will calculate the timestamp of a given event, for scraper function."""

    if info['time'] == 'All Day' or info['time'] == '' : 
        timestamp = int(datetime.datetime(int(info['year']), int(info['month_num']), int(info['day_number']), 0, tzinfo=datetime.timezone.utc).timestamp())
    else : 
        timestamp = int(datetime.datetime(int(info['year']), int(info['month_num']), int(info['day_number']), int(info['time'][:2]) , tzinfo=datetime.timezone.utc).timestamp())
    return str(timestamp)


def interact_with_site(driver):
    """this function uses selenium to interact with site in order to provide the desired source code to extract and scraping."""
    try :
        week_button = driver.find_element(By.XPATH,'/html/body/div[2]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[2]/button[1]')
        week_button.click()

        timestamp_key = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/button')
        timestamp_key.click()

        list_box = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/ol')
        select_timestamp = list_box.find_element(By.XPATH, '/html/body/div[2]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/ol/li[13]')
        select_timestamp.find_element(By.XPATH, '/html/body/div[2]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/ol/li[13]/div').click()
    except:
        try:
            week_button = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[2]/button[1]')
            week_button.click()

            timestamp_key = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/button')
            timestamp_key.click()

            list_box = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/ol')
            select_timestamp = list_box.find_element(By.XPATH, '/html/body/div[1]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/ol/li[13]')
            select_timestamp.find_element(By.XPATH, '/html/body/div[1]/div[2]/section[2]/div/div/div[1]/div/div[2]/div[1]/ol/li[13]/div').click()
        except Exception as e :
            raise e



def initializer():
    """intialize webdriver for selenium client."""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')  
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Remote('http://0.0.0.0:4444/wd/hub', options=options)
    # driver = webdriver.Remote('http://0.0.0.0:4444/wd/hub', DesiredCapabilities.CHROME)
    return driver

if __name__=='__main__' :
    year = input('year : ')
    week = input('week : ')
    res = Scraper(year, week)
    for i in res :
        print(res)