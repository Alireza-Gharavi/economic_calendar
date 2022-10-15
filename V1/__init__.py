from flask_restx import Api
from flask import Blueprint, url_for

blueprint = Blueprint('calendar', __name__)

class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '5000' in self.base_url else 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)

from V1.calendar import api as calendar

api = MyApi(
    blueprint,
    title='Economic Calnedrar',
    version='1.0',
    description='This API Will Scrape the Data From www.babypips.com Economical Calendar.'
)

api.add_namespace(calendar)
