from lxml import etree
from lxml import objectify
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
import requests
from datetime import datetime
from ldapi.ldapi import LDAPI
from flask import Response, render_template
import config


class SurveyRenderer:
    """
    This class represents a Survey and methods in this class allow one to be loaded from GA's internal Oracle
    ARGUS database and to be exported in a number of mimetypes including RDF, according to the 'GA Public Data Ontology'
    and PROV-O, the Provenance Ontology.
    """

    URI_MISSSING = 'http://www.opengis.net/def/nil/OGC/0/missing'
    URI_INAPPLICABLE = 'http://www.opengis.net/def/nil/OGC/0/inapplicable'
    URI_GA = 'http://pid.geoscience.gov.au/org/ga'

    def __init__(self, survey_id):
        self.survey_id = survey_id
        self.survey_name = None
        self.state = None
        self.operator = None
        self.contractor = None
        self.processor = None
        self.survey_type = None
        self.data_types = None
        self.vessel = None
        self.vessel_type = None
        self.release_date = None
        self.onshore_offshore = None
        self.start_date = None
        self.end_date = None
        self.w_long = None
        self.e_long = None
        self.s_lat = None
        self.n_lat = None
        self.line_km = None
        self.total_km = None
        self.line_spacing = None
        self.line_direction = None
        self.tie_spacing = None
        self.square_km = None
        self.crystal_volume = None
        self.up_crystal_volume = None
        self.digital_data = None
        self.geodetic_datum = None
        self.asl = None
        self.agl = None
        self.mag_instrument = None
        self.rad_instrument = None

        self.srid = 8311  # TODO: replace this magic number with a value from the DB

        # populate all instance variables from API
        # TODO: lazy load this, i.e. only populate if a view that need populating is loaded which is every view except for Alternates
        self._populate_from_oracle_api(survey_id)

    def render(self, view, mimetype):
        if view == 'gapd':
            if mimetype == 'text/html':
                return self.export_as_html(model_view=view)
        elif view == 'prov':
            return Response(self.export_as_rdf('prov', 'text/turtle'), mimetype=mimetype)

    def validate_xml(self, xml):
        parser = etree.XMLParser(dtd_validation=False)

        try:
            etree.fromstring(xml, parser)
            return True
        except Exception:
            print('not valid xml')
            return False

    def _populate_from_oracle_api(self, survey_id):
        """
        Populates this instance with data from the Oracle ARGUS table API
        """
        # internal URI
        # os.environ['NO_PROXY'] = 'ga.gov.au'
        # call API
        r = requests.get(config.XML_API_URL_SURVEY.format(survey_id))
        # deal with missing XML declaration
        if "No data" in r.text:
            raise ParameterError('No Data')

        xml = r.text

        if self.validate_xml(xml):
            self._populate_from_xml_file(xml)
            return True
        else:
            return False

    def _populate_from_xml_file(self, xml):
        """
        Populates this instance with data from an XML file.

        :param xml: XML according to GA's Oracle XML API from the Samples DB
        :return: None
        """
        '''
        example from API: http://www.ga.gov.au/www/argus.argus_api.survey?pSurveyNo=921

        <?xml version="1.0" ?>
        <ROWSET>
            <ROW>
                <SURVEYID>921</SURVEYID>
                <SURVEYNAME>Goomalling, WA, 1996</SURVEYNAME>
                <STATE>WA</STATE>
                <OPERATOR>Stockdale Prospecting Ltd.</OPERATOR>
                <CONTRACTOR>Kevron Geophysics Pty Ltd</CONTRACTOR>
                <PROCESSOR>Kevron Geophysics Pty Ltd</PROCESSOR>
                <SURVEY_TYPE>Detailed</SURVEY_TYPE>
                <DATATYPES>MAG,RAL,ELE</DATATYPES>
                <VESSEL>Aero Commander</VESSEL>
                <VESSEL_TYPE>Plane</VESSEL_TYPE>
                <RELEASEDATE/>
                <ONSHORE_OFFSHORE>Onshore</ONSHORE_OFFSHORE>
                <STARTDATE>05-DEC-96</STARTDATE>
                <ENDDATE>22-DEC-96</ENDDATE>
                <WLONG>116.366662</WLONG>
                <ELONG>117.749996</ELONG>
                <SLAT>-31.483336</SLAT>
                <NLAT>-30.566668</NLAT>
                <LINE_KM>35665</LINE_KM>
                <TOTAL_KM/>
                <LINE_SPACING>250</LINE_SPACING>
                <LINE_DIRECTION>180</LINE_DIRECTION>
                <TIE_SPACING/>
                <SQUARE_KM/>
                <CRYSTAL_VOLUME>33.6</CRYSTAL_VOLUME>
                <UP_CRYSTAL_VOLUME>4.2</UP_CRYSTAL_VOLUME>
                <DIGITAL_DATA>MAG,RAL,ELE</DIGITAL_DATA>
                <GEODETIC_DATUM>WGS84</GEODETIC_DATUM>
                <ASL/>
                <AGL>60</AGL>
                <MAG_INSTRUMENT>Scintrex CS2</MAG_INSTRUMENT>
                <RAD_INSTRUMENT>Exploranium GR820</RAD_INSTRUMENT>
            </ROW>
        </ROWSET>
        '''
        # turn the XML doc into a Python object
        root = objectify.fromstring(xml)

        self.survey_name = root.ROW.SURVEYNAME if root.ROW.SURVEYNAME != '' else None
        self.state = root.ROW.STATE if root.ROW.STATE != '' else None
        self.operator = root.ROW.OPERATOR if root.ROW.OPERATOR != '' else None
        self.contractor = root.ROW.CONTRACTOR if root.ROW.CONTRACTOR != '' else None
        self.processor = root.ROW.PROCESSOR if root.ROW.PROCESSOR != '' else None
        self.survey_type = root.ROW.SURVEY_TYPE if root.ROW.SURVEY_TYPE != '' else None
        self.data_types = root.ROW.DATATYPES if root.ROW.DATATYPES != '' else None
        self.vessel = root.ROW.VESSEL if root.ROW.VESSEL != '' else None
        self.vessel_type = root.ROW.VESSEL_TYPE if root.ROW.VESSEL_TYPE != '' else None
        self.release_date = datetime.strptime(root.ROW.RELEASEDATE.text, '%d-%b-%y') if root.ROW.RELEASEDATE != '' else None
        self.onshore_offshore = root.ROW.ONSHORE_OFFSHORE if root.ROW.ONSHORE_OFFSHORE != '' else None
        self.start_date = datetime.strptime(root.ROW.STARTDATE.text, '%d-%b-%y') if root.ROW.STARTDATE != '' else None
        self.end_date = datetime.strptime(root.ROW.ENDDATE.text, '%d-%b-%y') if root.ROW.ENDDATE != '' else None
        self.w_long = root.ROW.WLONG if root.ROW.WLONG != '' else None
        self.e_long = root.ROW.ELONG if root.ROW.ELONG != '' else None
        self.s_lat = root.ROW.SLAT if root.ROW.SLAT != '' else None
        self.n_lat = root.ROW.NLAT if root.ROW.NLAT != '' else None
        self.line_km = root.ROW.LINE_KM if root.ROW.LINE_KM != '' else None
        self.total_km = root.ROW.TOTAL_KM if root.ROW.TOTAL_KM != '' else None
        self.line_spacing = root.ROW.LINE_SPACING if root.ROW.LINE_SPACING != '' else None
        self.line_direction = root.ROW.LINE_DIRECTION if root.ROW.LINE_DIRECTION != '' else None
        self.tie_spacing = root.ROW.TIE_SPACING if root.ROW.TIE_SPACING != '' else None
        self.square_km = root.ROW.SQUARE_KM if root.ROW.SQUARE_KM != '' else None
        self.crystal_volume = root.ROW.CRYSTAL_VOLUME if root.ROW.CRYSTAL_VOLUME != '' else None
        self.up_crystal_volume = root.ROW.UP_CRYSTAL_VOLUME if root.ROW.UP_CRYSTAL_VOLUME != '' else None
        self.digital_data = root.ROW.DIGITAL_DATA if root.ROW.DIGITAL_DATA != '' else None
        self.geodetic_datum = root.ROW.GEODETIC_DATUM if root.ROW.GEODETIC_DATUM != '' else None
        self.asl = root.ROW.ASL if root.ROW.ASL != '' else None
        self.agl = root.ROW.AGL if root.ROW.AGL != '' else None
        self.mag_instrument = root.ROW.MAG_INSTRUMENT if root.ROW.MAG_INSTRUMENT != '' else None
        self.rad_instrument = root.ROW.RAD_INSTRUMENT if root.ROW.RAD_INSTRUMENT != '' else None

    def _generate_survey_wkt(self):
        if self.z is not None:
            # wkt = "SRID=" + self.srid + ";POINTZ(" + self.x + " " + self.y + " " + self.z + ")"
            wkt = "<https://epsg.io/" + self.srid + "> " \
                  "POINTZ(" + self.x + " " + self.y + " " + self.z + ")"
        else:
            # wkt = "SRID=" + self.srid + ";POINT(" + self.x + " " + self.y + ")"
            if self.srid is not None and self.x is not None and self.y is not None:
                wkt = "<https://epsg.io/" + self.srid + "> POINT(" + self.x + " " + self.y + ")"
            else:
                wkt = ''

        return wkt

    def _generate_survey_gml(self):
        if self.z is not None:
            gml = '<gml:Point srsDimension="3" srsName="https://epsg.io/' + self.srid + '">' \
                  '<gml:pos>' + self.x + ' ' + self.y + ' ' + self.z + '</gml:pos>' \
                  '</gml:Point>'
        else:
            if self.srid is not None and self.x is not None and self.y is not None:
                gml = '<gml:Point srsDimension="2" srsName="https://epsg.io/' + self.srid + '">' \
                      '<gml:pos>' + self.x + ' ' + self.y + '</gml:pos>' \
                      '</gml:Point>'
            else:
                gml = ''

        return gml

    def export_as_rdf(self, model_view='default', rdf_mime='text/turtle'):
        """
        Exports this instance in RDF, according to a given model from the list of supported models,
        in a given rdflib RDF mimetype

        :param model_view: string of one of the model view names available for Sample objects ['igsn', 'dc', '',
            'default']
        :param rdf_mime: string of one of the rdflib serlialization mimetype ['n3', 'nquads', 'nt', 'pretty-xml', 'trig',
            'trix', 'turtle', 'xml'], from http://rdflib3.readthedocs.io/en/latest/plugin_serializers.html
        :return: RDF string
        """

        # things that are applicable to all model views; the graph and some namespaces
        g = Graph()

        GEOSP = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geosp', GEOSP)

        AUROLE = Namespace('http://communications.data.gov.au/def/role/')
        g.bind('aurole', AUROLE)

        PROV = Namespace('http://www.w3.org/ns/prov#')
        g.bind('prov', PROV)

        # URI for this survey
        base_uri = 'http://pid.geoscience.gov.au/survey/'
        this_survey = URIRef(base_uri + self.survey_id)

        # define GA
        ga = URIRef(SurveyRenderer.URI_GA)

        # classing the Survey in PROV - relevant to all model options
        g.add((this_survey, RDF.type, PROV.Activity))

        # Activity properties
        # TODO: add in label, startedAtTime, endedAtTime, atLocation

        # define GA as an PROV Org with an ISO19115 role of Publisher
        g.add((ga, RDF.type, PROV.Org))
        qualified_attribution = BNode()
        g.add((qualified_attribution, RDF.type, PROV.Attribution))
        g.add((qualified_attribution, PROV.agent, ga))
        g.add((qualified_attribution, PROV.hadRole, AUROLE.Publisher))
        g.add((this_survey, PROV.qualifiedAttribution, qualified_attribution))

        # TODO: add in other Agents

        # Geometry
        SAMFL = Namespace('http://def.seegrid.csiro.au/ontology/om/sam-lite#')
        g.bind('samfl', SAMFL)

        # Survey location in GML & WKT, formulation from GeoSPARQL
        wkt = Literal(self._generate_survey_wkt(), datatype=GEOSP.wktLiteral)
        gml = Literal(self._generate_survey_gml(), datatype=GEOSP.gmlLiteral)

        geometry = BNode()
        g.add((this_survey, PROV.hadLocation, geometry))
        g.add((geometry, RDF.type, SAMFL.Polygon))
        g.add((geometry, GEOSP.asGML, gml))
        g.add((geometry, GEOSP.asWKT, wkt))

        # select model view
        if model_view == 'gapd':
            # default model is the GAPD model
            # DAPD model required namespaces
            GAPD = Namespace('http://pid.geoscience.gov.au/def/ont/gapd#')
            g.bind('gapd', GAPD)

            # classing the Survey in GAPD
            g.add((this_survey, RDF.type, GAPD.PublicSurvey))

            # TODO: add in other Survey properties
        elif model_view == 'prov':
            # nothing to do here as all PROV-O parts already created
            pass

        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(rdf_mime))

    def export_as_html(self, model_view='gapd'):
        """
        Exports this instance in HTML, according to a given model from the list of supported models.

        :param model_view: string of one of the model view names available for survey objects
        :return: HTML string
        """
        '''
        <?xml version="1.0" ?>
        <ROWSET>
         <ROW>
          <SURVEYID>921</SURVEYID>
          <SURVEYNAME>Goomalling, WA, 1996</SURVEYNAME>
          <STATE>WA</STATE>
          <OPERATOR>Stockdale Prospecting Ltd.</OPERATOR>
          <CONTRACTOR>Kevron Geophysics Pty Ltd</CONTRACTOR>
          <PROCESSOR>Kevron Geophysics Pty Ltd</PROCESSOR>
          <SURVEY_TYPE>Detailed</SURVEY_TYPE>
          <DATATYPES>MAG,RAL,ELE</DATATYPES>
          <VESSEL>Aero Commander</VESSEL>
          <VESSEL_TYPE>Plane</VESSEL_TYPE>
          <RELEASEDATE/>
          <ONSHORE_OFFSHORE>Onshore</ONSHORE_OFFSHORE>
          <STARTDATE>05-DEC-96</STARTDATE>
          <ENDDATE>22-DEC-96</ENDDATE>
          <WLONG>116.366662</WLONG>
          <ELONG>117.749996</ELONG>
          <SLAT>-31.483336</SLAT>
          <NLAT>-30.566668</NLAT>
          <LINE_KM>35665</LINE_KM>
          <TOTAL_KM/>
          <LINE_SPACING>250</LINE_SPACING>
          <LINE_DIRECTION>180</LINE_DIRECTION>
          <TIE_SPACING/>
          <SQUARE_KM/>
          <CRYSTAL_VOLUME>33.6</CRYSTAL_VOLUME>
          <UP_CRYSTAL_VOLUME>4.2</UP_CRYSTAL_VOLUME>
          <DIGITAL_DATA>MAG,RAL,ELE</DIGITAL_DATA>
          <GEODETIC_DATUM>WGS84</GEODETIC_DATUM>
          <ASL/>
          <AGL>60</AGL>
          <MAG_INSTRUMENT>Scintrex CS2</MAG_INSTRUMENT>
          <RAD_INSTRUMENT>Exploranium GR820</RAD_INSTRUMENT>
         </ROW>
        </ROWSET>
        '''
        if model_view == 'gapd':
            return render_template(
                'page_survey.html',
                survey_id=self.survey_id,
                survey_name=self.survey_name,
                state=self.state,
                operator=self.operator,
                contractor=self.contractor,
                processor=self.processor,
                survey_type=self.survey_type,
                data_types=self.data_types,
                vessel=self.vessel,
                vessel_type=self.vessel_type,
                release_date=self.release_date,
                onshore_offshore=self.onshore_offshore,
                start_date=self.start_date,
                end_date=self.end_date,
                w_long=self.w_long,
                e_long=self.e_long,
                s_lat=self.s_lat,
                n_lat=self.n_lat,
                line_km=self.line_km,
                total_km=self.total_km,
                line_spacing=self.line_spacing,
                line_direction=self.line_direction,
                tie_spacing=self.tie_spacing,
                square_km=self.square_km,
                crystal_volume=self.crystal_volume,
                up_crystal_volume=self.up_crystal_volume,
                digital_data=self.digital_data,
                geodetic_datum=self.geodetic_datum,
                asl=self.asl,
                agl=self.agl,
                mag_instrument=self.mag_instrument,
                rad_instrument=self.rad_instrument,
                srid=self.srid
            )

    # @staticmethod
    # def render_template_local(template_filename, **context):
    #     import os
    #     PATH = os.path.dirname(os.path.abspath(__file__))
    #     TEMPLATE_ENVIRONMENT = Environment(
    #         autoescape=False,
    #         loader=FileSystemLoader(os.path.join(os.path.dirname(PATH), 'templates')),
    #         trim_blocks=False)
    #     return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


class ParameterError(ValueError):
    pass

if __name__ == '__main__':
    import routes.model_classes_functions
    # get the valid views and mimetypes for a Survey
    survey_views_mimetypes = routes.model_classes_functions.get_classes_views_mimetypes()\
        .get('http://pid.geoscience.gov.au/def/ont/gapd#Survey')
    # get my required view & mimetype
    v, f = LDAPI.get_valid_view_and_mimetype(
        None,
        None,
        survey_views_mimetypes
    )
    import config
    s = SurveyRenderer(921)
    print(s.render(v, f))
