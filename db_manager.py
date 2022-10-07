from V1.calendarModel import CalendarModel
from V1.logger import logger
from scraper import Scraper
from bs4 import BeautifulSoup
import datetime, time


weeks = [i for i in range(1,53)]
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026] 

# weeks = [i for i in range(35, 38)]
# years = [2021,2022]



docs = CalendarModel()


def scrape_and_save():
    """this function will use the Scraper module to scrape the information from www.babypips.com and store this data in a mongodb database."""

    now_timestamp, last_record_timestamp = timestamps()
    flag = False
    if last_record_timestamp == -1 :
        flag = True

    
    if flag:
        for year in years :
            for week in weeks :
                recs = Scraper(year, week)
                res = docs.create_docs(recs)
                if res == 0:
                    logger.info(f"Writing year : {year}, week : {week} in Database Successfully Completed.")
                else :
                    logger.error(f"Error in Writing year : {year}, week : {week} in Database.")
                        
                now_timestamp, last_record_timestamp = timestamps()

                flag = False
                break
            break

    if now_timestamp > last_record_timestamp :
        last_doc = docs.last_doc()[0]
        last_year = last_doc['year']
        last_week = last_doc['week']
        docs.delete_docs(last_year, last_week)
        logger.info(f"Deleting year : {last_year}, week : {int(last_week[1:])} From Database.")


        continue_year_from = years.index(int(last_year))
        continue_week_from = weeks.index(int(last_week[1:]))
        for year in years[ continue_year_from: ]:
            for week in weeks[ continue_week_from: ]:
                if now_timestamp > last_record_timestamp :
                    recs = Scraper(year, week)
                    res = docs.create_docs(recs)
                    if res == 0:
                        logger.info(f"Writing year : {year}, week : {week} in Database Successfully Completed.")
                    else :
                        logger.error(f"Error in Writing year : {year}, week : {week} in Database.")
                    
                    now_timestamp, last_record_timestamp = timestamps()
                else :
                    pass

            continue_week_from = 0
            
                
    if now_timestamp <= last_record_timestamp :
        last_doc = docs.last_doc()[0]
        last_year = last_doc['year']
        last_week = last_doc['week']
        docs.delete_docs(last_year, last_week)
        logger.info(f"Deleting year : {last_year}, week : {int(last_week[1:])} From Database.")
        recs = Scraper(last_year, int(last_week[1:]))
        res = docs.create_docs(recs)
        if res == 0:
            logger.info(f"updating (recreating) all documents with year : {last_year}, and week : {int(last_week[1:])}.")


def timestamps():
    """this function will return the timestamp of now and timestamp of the last record(or last event) in database."""

    now = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
    try :
        last_record = docs.last_doc()[0]['timestamp']
    except IndexError:
        last_record = -1
    return now, int(last_record)




# def Scraper(year, week):                # this function will scrape the data from www.babypips.com site given inputs year and week number and return the records of economic calendar as dictionaries in a list named info_list
#     """ scrape the data of economic calendar at www.babypips.com

#     Parameters
#     ----------
#     year : str 
#            a sting representing year number.
#            e.x. year='2022'
#     week : str 
#            a string representing week number. 
#            e.x. week='17'

#     Returns
#     -------
#     info_list : a list of dictionaries, each dictionary represents a record of economic calendar.

#     """
#     year = str(year)
#     week = f"{int(week):02}"

#     months = {
#         'Jan' : '01',
#         'Feb' : '02',
#         'Mar' : '03',
#         'Apr' : '04',
#         'May' : '05',
#         'Jun' : '06',
#         'Jul' : '07',
#         'Aug' : '08',
#         'Sep' : '09',
#         'Oct' : '10',
#         'Nov' : '11',
#         'Dec' : '12'
#     }


#     # blocks = <div> , 'Section-module__container___WUPgM Table-module__day___As54H'
#     # day_number = <div> , 'Table-module__dayNumber___dyJpm'
#     # week_day = <td> , 'Table-module__weekday___p3Buh'
#     # time = <td> , 'Table-module__time___IHBtp'
#     # currency = <td> , 'Table-module__currency___gSAJ5'
#     # name = <td> , 'Table-module__name___FugPe'
#     # impact = <td> , 'Table-module__impact___kYuei'
#     # actual = <td> , 'Table-module__actual___kzVNq'
#     # forecast = <td> , 'Table-module__forecast___WchYX'
#     # previous = <td> , 'Table-module__previous___F0PHu'

#     url = f'https://www.babypips.com/economic-calendar?week={year}-W{week}'
#     try : 
#         res = requests.get(url, allow_redirects=False)
#         soup = BeautifulSoup(res.content, 'lxml')
#     except :
#         logger.error(f"connection to the {url} can't be established.")
#         # return ResponseAPI.send(status_code=404,message=f"connection to the {url} can't be established.")

#     try :
#         if res.status_code == 200:
#             info_list = []
#             info = {'year' : None, 'week' : None, 'month_num' : None , 'month_name' : None, 'day_number' : None , 'week_day' : None, 'time' : None , 'currency_name' : None , 'source_name' : None , 'impact' : None , 'actual' : None , 'forecast' : None , 'previous' : None , 'timestamp' : None}
#             blocks = soup.find_all('div', class_='Section-module__container___WUPgM Table-module__day___As54H')

#             for i in range(len(blocks)) :
#                 info['year'] = year
#                 info['week'] = f'W{week}'
#                 info['month_name'] = blocks[i].table.thead.tr.td.find('div', class_='Table-module__month___PGbXI').text
#                 info['month_num'] = months[info['month_name']]
#                 info['day_number'] = blocks[i].table.thead.tr.td.find('div', class_='Table-module__dayNumber___dyJpm').text
#                 info['week_day'] = blocks[i].table.tr.find('td', class_='Table-module__weekday___p3Buh').text
                
#                 recs_list = blocks[i].table.tbody.find_all('tr')

#                 for j in range(len(recs_list)) :
#                     info['time'] = recs_list[j].find('td' , class_='Table-module__time___IHBtp').text
#                     info['currency_name'] = recs_list[j].find('td', class_='Table-module__currency___gSAJ5').text
#                     info['source_name'] = recs_list[j].find('td', class_='Table-module__name___FugPe').text
#                     info['impact'] = recs_list[j].find('td', class_='Table-module__impact___kYuei').text
#                     info['actual'] = recs_list[j].find('td', class_='Table-module__actual___kzVNq').text
#                     info['forecast'] = recs_list[j].find('td', class_='Table-module__forecast___WchYX').text
#                     info['previous'] = recs_list[j].find('td', class_='Table-module__previous___F0PHu').text

#                     info['timestamp'] = timestamp_calc(info)

#                     info_list.append(info.copy())
                
#             return info_list

#         else :
#             logger.error("babypips.com can't fufill the request(the response code is not 200).")
#             # return ResponseAPI.send(status_code=404, message="babypips.com can't fulfill the request.")

#     except :
#         logger.error(f"error occured while parsing the scraped data exctracted from '{url}'")
#         # return ResponseAPI.send(status_code=404, message="error occured while parsing the scraped data.")
    
    


# def timestamp_calc(info):
#     """this function will calculate the timestamp of a given event, for Scraper function."""

#     if info['time'] == 'All Day' or info['time'] == '' : 
#         timestamp = int(datetime.datetime(int(info['year']), int(info['month_num']), int(info['day_number']), 0, tzinfo=datetime.timezone.utc).timestamp())
#     else : 
#         timestamp = int(datetime.datetime(int(info['year']), int(info['month_num']), int(info['day_number']), int(info['time'][:2]) , tzinfo=datetime.timezone.utc).timestamp())
#     return str(timestamp)



def db_connection_checker():
    """ a function to check the connection of database."""
    if docs.last_doc() != -1:
        return True
    else :
        return False


def main():
    if not db_connection_checker() :
        logger.error(f"database connection error.")
        logger.error(f"exiting from db_manager.py")
        exit()
    while True:
        scrape_and_save()
        time.sleep(1000)           # 18000 secoonds = five hours 


if __name__ == '__main__' :
    main()