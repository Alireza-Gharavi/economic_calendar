from V1.calendarModel import CalendarModel
from V1.logger import logger
from scraper import Scraper
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
                if recs == -1 :
                    logger.info(f"skip the writing of year : {year}, week : {week} in database.")
                    continue
                res = docs.create_docs(recs)
                if res == 0:
                    logger.info(f"Writing year : {year}, week : {week} in Database Successfully Completed.")
                    flag = False
                else :
                    logger.error(f"Error in Writing year : {year}, week : {week} in Database.")
                        
                now_timestamp, last_record_timestamp = timestamps()

                
                break
            break

    if now_timestamp > last_record_timestamp and not flag:
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
                    if recs == -1 :
                        logger.info(f"skip the writing of year : {year}, week : {week} in database.")
                        continue
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
        if recs != -1:
            res = docs.create_docs(recs)
            if res == 0:
                logger.info(f"updating (recreating) all documents with year : {last_year}, and week : {int(last_week[1:])}.")
        else :
            logger.info(f"skip the writing of year : {last_year}, week : {last_week} in database.")

def timestamps():
    """this function will return the timestamp of now and timestamp of the last record(or last event) in database."""

    now = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
    try :
        last_record = docs.last_doc()[0]['timestamp']
    except IndexError:
        last_record = -1
    return now, int(last_record)



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
        time.sleep(3600)           # 3600 secoonds = five hours 


if __name__ == '__main__' :
    main()