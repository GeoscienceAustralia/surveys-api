import json
import os
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


def get_classes_views_mimetypes():
    """
    Caches the classes_views_mimetypes.json file in memory as a Python object
    :return: a Python object parsed from the classes_views_mimetypes.json file
    """
    cvf = cache.get('classes_views_mimetypes')
    if cvf is None:
        json_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'classes_views_mimetypes.json'), 'r')
        cvf = json.load(json_file)
        # times out never (i.e. on app startup/shutdown)
        cache.set('classes_views_mimetypes', cvf)
    return cvf
