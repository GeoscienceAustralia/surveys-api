"""
This file contains all the HTTP routes for classes from the IGSN model, such as Samples and the Sample Register
"""
from flask import Blueprint, render_template, request, Response
from routes import routes_functions
from ldapi.ldapi import LDAPI, LdapiParameterError
from routes import model_classes_functions
import urllib
import config
import requests

model_classes = Blueprint('model_classes', __name__)


@model_classes.route('/survey/<string:survey_id>')
def survey(survey_id):
    """
    A single Survey

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
                class_uri,
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
            except ValueError as e:
                print(e)
                return render_template('page_no_survey_record.html'), 404

    except LdapiParameterError as e:
        return routes_functions.client_error_Response(e)


@model_classes.route('/survey/')
def surveys():
    """
    The Register of Surveys

    :return: HTTP Response
    """
    # lists the views and mimetypes available for a Survey Register (a generic Register)
    views_mimetypes = model_classes_functions.get_classes_views_mimetypes() \
        .get('http://purl.org/linked-data/registry#Register')

    try:
        view, mime_format = LDAPI.get_valid_view_and_mimetype(
            request.args.get('_view'),
            request.args.get('_format'),
            views_mimetypes
        )

        # if alternates model, return this info from file
        class_uri = 'http://pid.geoscience.gov.au/def/ont/gapd#Survey'

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

            # pagination
            page = int(request.args.get('page')) if request.args.get('page') is not None else 1
            per_page = int(request.args.get('per_page')) if request.args.get('per_page') is not None else 100

            if per_page > 100:
                return Response(
                    'You must enter either no value for per_page or an integer <= 100.',
                    status=400,
                    mimetype='text/plain'
                )

            links = []
            links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
            links.append('<http://www.w3.org/ns/ldp#Page>; rel="type"')  # signalling that this is, in fact, a resource described in pages
            links.append('<{}?per_page={}>; rel="first"'.format(config.BASE_URI_SAMPLE, per_page))

            # if this isn't the first page, add a link to "prev"
            if page != 1:
                links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                    config.BASE_URI_SAMPLE,
                    per_page,
                    (page - 1)
                ))

            # add a link to "next" and "last"
            try:
                # r = requests.get(config.XML_API_URL_TOTAL_COUNT)
                # no_of_samples = int(r.content.split('<RECORD_COUNT>')[1].split('</RECORD_COUNT>')[0])
                no_of_samples = 9200  # TODO: implement a survey count Oracle XML API
                last_page_no = int(round(no_of_samples / per_page, 0)) + 1  # same as math.ceil()

                # if we've gotten the last page value successfully, we can choke if someone enters a larger value
                if page > last_page_no:
                    return Response(
                        'You must enter either no value for page or an integer <= {} which is the last page number.'
                            .format(last_page_no),
                        status=400,
                        mimetype='text/plain'
                    )

                # add a link to "next"
                if page != last_page_no:
                    links.append('<{}?per_page={}&page={}>; rel="next"'.format(config.BASE_URI_SAMPLE, per_page, (page + 1)))

                # add a link to "last"
                links.append('<{}?per_page={}&page={}>; rel="last"'.format(config.BASE_URI_SAMPLE, per_page, last_page_no))
            except:
                # if there's some error in getting the no of samples, add the "next" link but not the "last" link
                links.append('<{}?per_page={}&page={}>; rel="next"'.format(config.BASE_URI_SAMPLE, per_page, (page + 1)))

            headers = {
                'Link': ', '.join(links)
            }

            return register.RegisterRenderer(request, class_uri, None, page, per_page, last_page_no)\
                .render(view, mime_format, extra_headers=headers)

    except LdapiParameterError as e:
        return routes_functions.client_error_Response(e)
