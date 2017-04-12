"""
This file contains all the HTTP routes for classes from the IGSN model, such as Samples and the Sample Register
"""
from flask import Blueprint, render_template, request
from routes import routes_functions
from ldapi.ldapi import LDAPI, LdapiParameterError
from routes import model_classes_functions
# import urllib.parse
from urlparse import urlparse

model_classes = Blueprint('model_classes', __name__)


@model_classes.route('/survey/<string:survey_id>')
def survey(survey_id):
    """
    A single Sample

    :return: HTTP Response
    """
    # lists the views and mimetypes available for a Survey
    views_mimetypes = model_classes_functions.get_classes_views_mimetypes()\
        .get('http://pid.geoscience.gov.au/def/ont/gapd#Survey')

    try:
        view, mimetype = LDAPI.get_valid_view_and_mimetype(
            request.args.get('_view'),
            request.args.get('_format'),
            views_mimetypes
        )

        # if alternates model, return this info from file
        if view == 'alternates':
            class_uri = 'http://pid.geoscience.gov.au/def/ont/gapd#Survey'
            class_uri_name = class_uri.split('#')[1]
            instance_uri = 'http://pid.geoscience.gov.au/survey/' + survey_id
            del views_mimetypes['renderer']
            return routes_functions.render_alternates_view(
                class_uri_name,
                urllib.parse.quote_plus(class_uri),
                instance_uri,
                instance_uri,
                views_mimetypes,
                request.args.get('_format')
            )
        else:
            from model.survey import SurveyRenderer
            try:
                s = SurveyRenderer(survey_id)
                return s.render(view, mimetype)
            except ValueError:
                return render_template('page_no_survey_record.html'), 404

    except LdapiParameterError as e:
        return routes_functions.client_error_Response(e)


@model_classes.route('/survey/')
def surveys():
    """
    The Register of Samples

    :return: HTTP Response
    """
    # lists the views and mimetypes available for a Survey Register (a generic Register)
    views_mimetypes = model_classes_functions.get_classes_views_mimetypes() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        view, mimetype = LDAPI.get_valid_view_and_mimetype(
            request.args.get('_view'),
            request.args.get('_format'),
            views_mimetypes
        )

        # if alternates model, return this info from file
        class_uri = 'http://pid.geoscience.gov.au/def/ont/igsn#Sample'

        if view == 'alternates':
            del views_mimetypes['renderer']
            return routes_functions.render_alternates_view(
                class_uri,
                urllib.quote_plus(class_uri),
                None,
                None,
                views_mimetypes,
                request.args.get('_format')
            )
        else:
            from model import register
            return register.RegisterRenderer(request, class_uri, None).render(view, mimetype)

    except LdapiParameterError as e:
        return routes_functions.client_error_Response(e)
