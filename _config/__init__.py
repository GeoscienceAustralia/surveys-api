from os.path import dirname, realpath, join, abspath

APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
LOGFILE = APP_DIR + 'surveys-api.log'
DEBUG = True

XML_API_URL_SURVEY_REGISTER = 'http://dbforms.ga.gov.au/www/argus.argus_api.SearchSurveys' \
                              '?pOrder=SURVEYID&pPageno={0}&pNoOfRecordsPerPage={1}'
XML_API_URL_SURVEY = 'http://dbforms.ga.gov.au/www/argus.argus_api.survey?pSurveyNo={}'

BASE_URI_SAMPLE = 'http://pid.geoscience.gov.au/survey/'

ADMIN_EMAIL = 'dataman@ga.gov.au'

XML_API = {
    'ENTITIES': {
        'GET_CAPABILITIES': 'http://dbforms.ga.gov.au/www/a.entities_api.getCapabilities',
        'ENTITY': 'http://dbforms.ga.gov.au/www/a.entities_api.entities?pEno={}',
        'ENTITY_REGISTER': ''

    },
    'SURVEYS': {
        'GET_CAPABILITIES': 'http://dbforms.ga.gov.au/www/argus.argus_api.getCapabilities',
        'SURVEY': '',
        'SURVEY_REGISTER': 'http://dbforms.ga.gov.au/www/argus.argus_api.SearchSurveys'
                           '?pOrder=SURVEYID&pPageno={0}&pNoOfRecordsPerPage={1}'

    }
}

GOOGLE_MAPS_API_KEY_EMBED = 'AIzaSyDhuFCoJynhhQT7rcgKYzk3i7K77IEwjO4'
GOOGLE_MAPS_API_KEY = 'AIzaSyCUDcjVRsIHVHpv53r7ZnaX5xzqJbyGk58'
