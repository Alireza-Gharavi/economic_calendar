import datetime
from V1.response import ResponseAPI
from V1.calendarModel import CalendarModel
from flask import request, current_app
from flask_restx import Resource, Namespace
from V1.logger import logger



api = Namespace('Economic_Calendar', description='Economic Calendar Routes')

# logger.basicConfig(filename='logs.log', level=logger.ERROR, format='%(asctime)s:%(name)s:%(message)s')

now_timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

@api.route('/')
class calnedar(Resource):
    @api.doc(params={
        'source_name':{'description':'source name of the event', 'in':'query', 'type':'str','default':'all'},
        'currency_name':{'description':'currency symbol (e.x. USD)', 'in':'query','type':'str','default':'all'},
        'impact':{'description':'low/med/high', 'in':'query', 'type':'str', 'default':'all'},
        'from':{'description':'start timestamp', 'in':'query', 'type':'int', 'default':0},
        'to':{'description':f'end timestamp (default = {datetime.datetime.now(tz=datetime.timezone.utc)})', 'in':'query', 'type':'int', 'default':now_timestamp}
    } ,responses={ 
        200: 'Operation done successfully',
        401: 'Database connection error',
        404: 'Error in connecting to economic calendar provider',
        422: 'Inconsistent paramters'
    })
    def get(self):
        source_name = request.args.get('source_name')
        currency_name = request.args.get('currency_name')
        impact = request.args.get('impact')
        from_timestamp = request.args.get('from')
        to_timestamp = request.args.get('to')

        if source_name == None :
            logger.error("currency_name can't be None value.")
            return ResponseAPI.send(status_code=422, message="source_name parameter can't be None value.")

        if (currency_name == None) or (currency_name.isalpha() != True) or (len(currency_name) != 3) :
            logger.error('bad value for currency_name paramter.')
            return ResponseAPI.send(status_code=422, message='bad value for currency parameter.') 
        else :
            currency_name = currency_name.upper()

        if (impact == None) or (impact.lower() not in ['all', 'low', 'med', 'high']) :
            logger.error('bad value for impact parameter.')
            return ResponseAPI.send(status_code=422, message='impact parameter value must be one of the all/low/med/high.')
        else :
            impact = impact.lower()

        if (to_timestamp == None) or (from_timestamp == None) or (from_timestamp.isdigit() != True) or (to_timestamp.isdigit() != True):
            logger.error("value of 'from' and 'to' parameters is not a digit")
            return ResponseAPI.send(status_code=422, message="value of 'from' and 'to' parameters must be digits.")

        if from_timestamp > to_timestamp :
            logger.error('value of start timestamp is greater than end timestamp.')
            return ResponseAPI.send(status_code=422, message='value of start parameter(from) is greater than end parameter(to)', data={'present timestamp':int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())})
        
        try :
            docs = CalendarModel()
        except :
            logger.error("database connection error.")
            return ResponseAPI.send(status_code=401, message='database connection error.')


        result = docs.search(source_name, currency_name, impact, from_timestamp, to_timestamp)
        # return json.loads(json.dumps(list(result)))
        return ResponseAPI.send(status_code=200, message='done successfully', data=list(result))


