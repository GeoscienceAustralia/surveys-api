"""
This file contains all the HTTP routes for basic pages (usually HTML)
"""
import os
from flask import Blueprint, Response, request, render_template, send_from_directory
from lxml import etree
from lxml.builder import ElementMaker
from _ldapi.ldapi import LDAPI, LdapiParameterError
from controller import routes_functions

pages = Blueprint('controller', __name__)


@pages.route('/favicon.ico')
def favicon():
    favicon_path = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        'static',
        'img'
    )
    return send_from_directory(favicon_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@pages.route('/')
def index():
    """
    A basic landing page for this web service

    :return: HTTP Response (HTML page only)
    """
    views_mimetypes = {
        'default': 'landingpage',
        'alternates': ['text/html'],
        'landingpage': ['text/html'],
        'getcapabilities': ['text/xml']
    }

    try:
        view, mimetype = LDAPI.get_valid_view_and_mimetype(
            request.args.get('_view'),
            request.args.get('_format'),
            views_mimetypes
        )
    except LdapiParameterError as e:
        return routes_functions.client_error_Response(e)

    # select controller and mimetype

    if view != 'getcapabilities':
        if mimetype == 'text/html':
            return render_template(
                'page_index.html',
            )
        else:
            return Response(
                'This controller of the API\'s root only has an HTML representation',
                status=400,
                mimetype='text/plain')
    elif view == 'getcapabilities':
        # move GetCapabilities response formulation to a Renderer class
        # only a single mimetype for this controller
        em = ElementMaker(
            namespace="http://fake.com/_ldapi",
            nsmap={
                '_ldapi': "http://fake.com/_ldapi"
             }
        )
        onl = ElementMaker(
            namespace="http://fake.com/_ldapi",
            nsmap={
                'xlink': "http://www.w3.org/1999/xlink",
            }
        )
        doc = em.LDAPI_Capabilities(
            em.Service(
                em.Name('Linked Data API'),
                em.Title('Geoscience Australia\'s Physical Samples'),
                em.KeywordList(
                    em.Keyword('model'),
                    em.Keyword('IGSN'),
                    em.Keyword('Linked Data'),
                    em.Keyword('XML'),
                    em.Keyword('RDF'),
                ),
                # TODO: parameterised namespaces not working yet
                onl.OnlineResource(type="simple", href="http://pid.geoscience.gov.au/service/survey/"),
                em.ContactInformation(
                    em.ContactPersonPrimary(
                        em.contactPerson('Nicholas Car'),
                        em.ContactOrganization('Geoscience Australia')
                    ),
                    em.ContactAddress(
                        em.AddressType('Postal'),
                        em.Address('GPO Box 378'),
                        em.City('Canberra'),
                        em.StateOrProvince('ACT'),
                        em.PostCode('2601'),
                        em.Country('Australia'),
                        em.ContactVoiceTelephone('+61 2 6249 9111'),
                        em.ContactFacsimileTelephone(),
                        em.ContactElectronicMailAddress('clientservices@ga.gov.au')
                    )
                ),
                em.Fees('none'),
                em.AccessConstraints(
                    '(c) Commonwealth of Australia (Geoscience Australia) 2016. This product is released under the ' +
                    'Creative Commons Attribution 4.0 International Licence. ' +
                    'http://creativecommons.org/licenses/by/4.0/legalcode'
                )
            ),
            em.Capability(
                em.Request(
                    em.GetCapabilities(
                        em.Format('text/xml'),
                        em.DCPType(
                            em.HTTP(
                                em.Get(
                                    onl.OnlineResource(
                                        type="simple",
                                        href="http://pid.geoscience.gov.au/service/survey/" +
                                             "?_view=getcapabilities&_format=text/xml"
                                    ),
                                )
                            )
                        )
                    ),
                    em.Sample(
                        em.Format('text/html'),
                        em.Format('text/turtle'),
                        em.Format('application/rdf+xml'),
                        em.Format('application/rdf+json'),
                        em.DCPType(
                            em.HTTP(
                                em.Get(
                                    onl.OnlineResource(
                                        type="simple",
                                        href="http://pid.geoscience.gov.au/service/survey/{SURVEY_ID}"
                                    ),
                                )
                            )
                        )
                    ),
                    em.SampleRegister(
                        em.Format('text/html'),
                        em.Format('text/turtle'),
                        em.Format('application/rdf+xml'),
                        em.Format('application/rdf+json'),
                        em.DCPType(
                            em.HTTP(
                                em.Get(
                                    onl.OnlineResource(
                                        type="simple",
                                        href="http://pid.geoscience.gov.au/service/survey/"
                                    ),
                                )
                            )
                        )
                    )
                )

            )
        )
        xml = etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return Response(xml, status=200, mimetype='text/xml')


@pages.route('/page/about')
def about():
    return render_template('page_about.html')
