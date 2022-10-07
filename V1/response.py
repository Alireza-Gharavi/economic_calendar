from flask import Response
from flask import current_app

class ResponseAPI:

    @staticmethod
    def send(status_code, message='', data=None):
        resp = Response({
            "status" : status_code,
            "message" : message,
            "data" : data
        },
            status = status_code        
        )

        current_app.logger.info("request done with {0} status code and message {1}".format(str(status_code), message))
        return resp.response