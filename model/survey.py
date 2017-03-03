from lxml import etree
from lxml import objectify
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
import requests
from datetime import datetime
from ldapi.ldapi import LDAPI
from flask import Response, render_template


class SurveyRenderer:
    """
    This class represents a Survey and methods in this class allow one to be loaded from GA's internal Oracle
    ARGUS database and to be exported in a number of formats including RDF, according to the 'GA Public Data Ontology'
    and PROV-O, the Provenance Ontology.
    """

    URI_MISSSING = 'http://www.opengis.net/def/nil/OGC/0/missing'
    URI_INAPPLICABLE = 'http://www.opengis.net/def/nil/OGC/0/inapplicable'
    URI_GA = 'http://pid.geoscience.gov.au/org/ga'

    def __init__(self, oracle_api_survey_url, survey_id):
        self.oracle_api_survey_url = oracle_api_survey_url

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
        self._populate_from_oracle_api()

    def render(self, view, mimetype):
        if view == 'gapd':
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

    def _populate_from_oracle_api(self):
        """
        Populates this instance with data from the Oracle ARGUS table API
        """
        # internal URI
        # os.environ['NO_PROXY'] = 'ga.gov.au'
        # call API
        r = requests.get(self.oracle_api_survey_url.format(self.survey_id))
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
        # turn the XML doc into a Python object
        root = objectify.fromstring(xml)

        self.survey_name = root.ROW.SURVEYNAME
        self.state = root.ROW.SURVEYNAME
        self.operator = root.ROW.SURVEYNAME
        self.contractor = root.ROW.SURVEYNAME
        self.processor = root.ROW.SURVEYNAME
        self.survey_type = root.ROW.SURVEYNAME
        self.data_types = root.ROW.SURVEYNAME
        self.vessel = root.ROW.SURVEYNAME
        self.vessel_type = root.ROW.SURVEYNAME
        self.release_date = root.ROW.SURVEYNAME
        self.onshore_offshore = root.ROW.SURVEYNAME
        self.start_date = root.ROW.SURVEYNAME
        self.end_date = root.ROW.SURVEYNAME
        self.w_long = root.ROW.SURVEYNAME
        self.e_long = root.ROW.SURVEYNAME
        self.s_lat = root.ROW.SURVEYNAME
        self.n_lat = root.ROW.SURVEYNAME
        self.line_km = root.ROW.SURVEYNAME
        self.total_km = root.ROW.SURVEYNAME
        self.line_spacing = root.ROW.SURVEYNAME
        self.line_direction = root.ROW.SURVEYNAME
        self.tie_spacing = root.ROW.SURVEYNAME
        self.square_km = root.ROW.SURVEYNAME
        self.crystal_volume = root.ROW.SURVEYNAME
        self.up_crystal_volume = root.ROW.SURVEYNAME
        self.digital_data = root.ROW.SURVEYNAME
        self.geodetic_datum = root.ROW.SURVEYNAME
        self.asl = root.ROW.SURVEYNAME
        self.agl = root.ROW.SURVEYNAME
        self.mag_instrument = root.ROW.SURVEYNAME
        self.rad_instrument = root.ROW.SURVEYNAME

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

        # if elem.tag == "IGSN":
        #     self.survey_id = elem.text
        # elif elem.tag == "SAMPLEID":
        #     self.sampleid = elem.text

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
        in a given rdflib RDF format

        :param model_view: string of one of the model view names available for Sample objects ['igsn', 'dc', '',
            'default']
        :param rdf_mime: string of one of the rdflib serlialization format ['n3', 'nquads', 'nt', 'pretty-xml', 'trig',
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

    def export_as_html(self, model_view='default'):
        """
        Exports this instance in HTML, according to a given model from the list of supported models.

        :param model_view: string of one of the model view names available for survey objects ['igsn', 'dc', '',
            'default']
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

        html = '<table class="lined">'
        html += '   <tr><th>Property</th><th>Value</th></tr>'
        if model_view == 'igsn':
            # TODO: complete the properties in this view
            html += '   <tr><th>IGSN</th><td>' + self.survey_id + '</td></tr>'
            html += '   <tr><th>Identifier</th><td>' + self.survey_id + '</td></tr>'
            if self.survey_id is not None:
                html += '   <tr><th>survey ID</th><td>' + self.survey_id + '</td></tr>'
            if self.survey_type is not None:
                html += '   <tr><th>survey Type</th><td><a href="' + self.survey_type + '">' + self.survey_type.split('/')[-1] + '</a></td></tr>'
            html += '   <tr><th>Sampling Location (WKT)</th><td>' + self._generate_survey_wkt() + '</td></tr>'
            html += '   <tr><th>Current Location</th><td>GA Services building</td></tr>'
            # TODO: make this resolve
            html += '   <tr><th>Sampling Feature</th><td><a style="text-decoration: line-through;" href="' + TERM_LOOKUP['entity_type'][self.entity_type] + '">' + TERM_LOOKUP['entity_type'][self.entity_type] + '</a></td></tr>'
            if self.method_type is not None:
                html += '   <tr><th>Method Type</th><td><a href="' + self.method_type + '">' + self.method_type.split('/')[-1] + '</a></td></tr>'
            # TODO: replace with dynamic
            html += '   <tr><th>Access Rights</th><td><a href="http://pid.geoscience.gov.au/def/voc/igsn-codelists/Public">Public</a></td></tr>'
            html += '   <tr><th>Publisher</th><td><a href="http://pid.geoscience.gov.au/org/ga">Geoscience Australia</a></td></tr>'
            if self.remark is not None:
                html += '   <tr><th>Description</th><td>' + self.remark + '</td></tr>'

        elif model_view == 'dc':
            html += '   <tr><th>IGSN</th><td>' + self.survey_id + '</td></tr>'
            html += '   <tr><th>Coverage</th><td>' + self._generate_survey_wkt() + '</td></tr>'
            if self.date_acquired is not None:
                html += '   <tr><th>Date</th><td>' + self.date_acquired.isoformat() + '</td></tr>'
            if self.remark is not None:
                html += '   <tr><th>Description</th><td>' + self.remark + '</td></tr>'
            if self.material_type is not None:
                html += '   <tr><th>Format</th><td>' + self.material_type + '</td></tr>'
            if self.survey_type is not None:
                html += '   <tr><th>Type</th><td>' + self.survey_type + '</td></tr>'

        html += '</table>'

        if self.date_acquired is not None:
            year_acquired = datetime.strftime(self.date_acquired, '%Y')
        else:
            year_acquired = 'XXXX'

        return render_template(
            'page_survey.html',
            view=model_view,
            igsn=self.survey_id,
            year_acquired=year_acquired,
            placed_html=html,
            date_now=datetime.now().strftime('%d %B %Y')
        )


class ParameterError(ValueError):
    pass

if __name__ == '__main__':
    import config
    s = SurveyRenderer(config.XML_API_URL_SURVEY ,921)
    print(s.render(None, None))
