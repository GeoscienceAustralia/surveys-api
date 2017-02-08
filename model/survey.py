from lxml import etree
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
from io import StringIO
import requests
from datetime import datetime
from ldapi.ldapi import LDAPI
from flask import Response, render_template


class Survey:
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
        self.sampleid = None
        self.sample_type = None
        self.method_type = None
        self.material_type = None
        self.long_min = None
        self.long_max = None
        self.lat_min = None
        self.lat_max = None
        self.gtype = None
        self.srid = None
        self.x = None
        self.y = None
        self.z = None
        self.elem_info = None
        self.ordinates = None
        self.state = None
        self.country = None
        self.depth_top = None
        self.depth_base = None
        self.strath = None
        self.age = None
        self.remark = None
        self.lith = None
        self.date_acquired = None
        self.entity_uri = None
        self.entity_name = None
        self.entity_type = None
        self.hole_long_min = None
        self.hole_long_max = None
        self.hole_lat_min = None
        self.hole_lat_max = None
        self.date_load = None
        self.date_modified = None
        self.sample_no = None

        # populate all instance variables from API
        # TODO: lazy load this, i.e. only populate if a view that need populating is loaded which is every view except for Alternates
        self._populate_from_oracle_api()

    def render(self, view, mimetype):
        if mimetype in LDAPI.get_rdf_mimetypes_list():
            return Response(self.export_as_rdf(view, mimetype), mimetype=mimetype)

        if view == 'gapd':
            # RDF formats handled by general case
            # HTML is the only other enabled format for igsn view
            return self.export_as_html(model_view=view)
        elif view == 'prov':
            # RDF formats handled by general case
            # only RDF for this view so set the mimetype to our favourite mime format
            mimetype = 'text/turtle'
            return Response(self.export_as_rdf('prov', mimetype), mimetype=mimetype)

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
        if "No data" in r.content:
            raise ParameterError('No Data')

        xml = r.content

        if self.validate_xml(xml):
            self._populate_from_xml_file(StringIO(xml))
            return True
        else:
            return False

    def _populate_from_xml_file(self, xml):
        """
        Populates this instance with data from an XML file.

        :param xml: XML according to GA's Oracle XML API from the Samples DB
        :return: None
        """
        # iterate through the elements in the XML element tree and handle each
        for event, elem in etree.iterparse(xml):
            '''
            <ROWSET>
             <ROW>
              <SURVEYID>368</SURVEYID>
              <SURVEYNAME>Swain Reefs (Townsville), QLD, 1969</SURVEYNAME>
              <STATE>QLD</STATE>
              <OPERATOR>Aust Gulf Oil Co</OPERATOR>
              <CONTRACTOR>Aero Service</CONTRACTOR>
              <PROCESSOR/>
              <SURVEY_TYPE>Regional</SURVEY_TYPE>
              <DATATYPES>MAG</DATATYPES>
              <VESSEL/>
              <VESSEL_TYPE>Plane</VESSEL_TYPE>
              <RELEASEDATE/>
              <ONSHORE_OFFSHORE>Offshore</ONSHORE_OFFSHORE>
              <STARTDATE>06-MAR-69</STARTDATE>
              <ENDDATE>19-MAR-69</ENDDATE>
              <WLONG>146</WLONG>
              <ELONG>150.5</ELONG>
              <SLAT>-21</SLAT>
              <NLAT>-16.85</NLAT>
              <LINE_KM/>
              <TOTAL_KM>11878</TOTAL_KM>
              <LINE_SPACING>4000</LINE_SPACING>
              <LINE_DIRECTION>45</LINE_DIRECTION>
              <TIE_SPACING>20000</TIE_SPACING>
              <SQUARE_KM>25958</SQUARE_KM>
              <CRYSTAL_VOLUME/>
              <UP_CRYSTAL_VOLUME/>
              <DIGITAL_DATA>MAG</DIGITAL_DATA>
              <GEODETIC_DATUM/>
              <ASL>600</ASL>
              <AGL>150</AGL>
              <MAG_INSTRUMENT/>
              <RAD_INSTRUMENT/>
             </ROW>
            </ROWSET>
            '''
            if elem.tag == "IGSN":
                self.survey_id = elem.text
            elif elem.tag == "SAMPLEID":
                self.sampleid = elem.text
            elif elem.tag == "SAMPLE_TYPE_NEW":
                if elem.text is not None:
                    self.sample_type = TERM_LOOKUP['sample_type'].get(elem.text)
                    if self.sample_type is None:
                        self.sample_type = Survey.URI_MISSSING
            elif elem.tag == "SAMPLING_METHOD":
                if elem.text is not None:
                    self.method_type = TERM_LOOKUP['method_type'].get(elem.text)
                    if self.method_type is None:
                        self.method_type = Survey.URI_MISSSING
            elif elem.tag == "MATERIAL_CLASS":
                if elem.text is not None:
                    self.material_type = TERM_LOOKUP['material_type'].get(elem.text)
                    if self.material_type is None:
                        self.material_type = Survey.URI_MISSSING
            elif elem.tag == "SAMPLE_MIN_LONGITUDE":
                if elem.text is not None:
                    self.long_min = elem.text
            elif elem.tag == "SAMPLE_MAX_LONGITUDE":
                if elem.text is not None:
                    self.long_max = elem.text
            elif elem.tag == "SAMPLE_MIN_LATITUDE":
                if elem.text is not None:
                    self.lat_min = elem.text
            elif elem.tag == "SAMPLE_MAX_LATITUDE":
                if elem.text is not None:
                    self.lat_max = elem.text
            elif elem.tag == "SDO_GTYPE":
                if elem.text is not None:
                    self.gtype = elem.text
            elif elem.tag == "SDO_SRID":
                if elem.text is not None:
                    self.srid = elem.text
            elif elem.tag == "X":
                if elem.text is not None:
                    self.x = elem.text
            elif elem.tag == "Y":
                if elem.text is not None:
                    self.y = elem.text
            elif elem.tag == "Z":
                if elem.text is not None:
                    self.z = elem.text
            elif elem.tag == "SDO_ELEM_INFO":
                if elem.text is not None:
                    self.elem_info = elem.text
            elif elem.tag == "SDO_ORDINATES":
                if elem.text is not None:
                    self.ordinates = elem.text
            elif elem.tag == "STATEID":
                if elem.text is not None:
                    self.state = TERM_LOOKUP['state'].get(elem.text)
                    if self.state is None:
                        self.state = Survey.URI_MISSSING
            elif elem.tag == "COUNTRY":
                if elem.text is not None:
                    self.country = TERM_LOOKUP['country'].get(elem.text)
                    if self.country is None:
                        self.country = Survey.URI_MISSSING
            elif elem.tag == "TOP_DEPTH":
                if elem.text is not None:
                    self.depth_top = elem.text
            elif elem.tag == "BASE_DEPTH":
                if elem.text is not None:
                    self.depth_base = elem.text
            elif elem.tag == "STRATNAME":
                if elem.text is not None:
                    self.strath = elem.text
            elif elem.tag == "AGE":
                if elem.text is not None:
                    self.age = elem.text
            elif elem.tag == "REMARK":
                if elem.text:
                    self.remark = elem.text
            elif elem.tag == "LITHNAME":
                if elem.text is not None:
                    self.lith = TERM_LOOKUP['lith'].get(elem.text)
                    if self.lith is None:
                        self.lith = Survey.URI_MISSSING
            elif elem.tag == "ACQUIREDATE":
                if elem.text is not None:
                    self.date_acquired = datetime.strptime(elem.text, '%Y-%m-%d %H:%M:%S')
            elif elem.tag == "ENO":
                if elem.text is not None:
                    self.entity_uri = 'http://pid.geoscience.gov.au/site/' + elem.text
            elif elem.tag == "ENTITYID":
                if elem.text is not None:
                    self.entity_name = elem.text
            elif elem.tag == "ENTITY_TYPE":
                if elem.text is not None:
                    self.entity_type = elem.text
            elif elem.tag == "HOLE_MIN_LONGITUDE":
                if elem.text is not None:
                    self.hole_long_min = elem.text
            elif elem.tag == "HOLE_MAX_LONGITUDE":
                if elem.text is not None:
                    self.hole_long_max = elem.text
            elif elem.tag == "HOLE_MIN_LATITUDE":
                if elem.text is not None:
                    self.hole_lat_min = elem.text
            elif elem.tag == "HOLE_MAX_LATITUDE":
                if elem.text is not None:
                    self.hole_lat_max = elem.text
            elif elem.tag == "LOADEDDATE":
                if elem.text is not None:
                    self.date_load = datetime.strptime(elem.text, '%Y-%m-%d %H:%M:%S')
            elif elem.tag == "MODIFIED_DATE":
                if elem.text is not None:
                    self.date_modified = datetime.strptime(elem.text, '%Y-%m-%d %H:%M:%S')
            elif elem.tag == "SAMPLENO":
                if elem.text is not None:
                    self.sample_no = elem.text

        return True

    def _generate_sample_wkt(self):
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

    def _generate_sample_gml(self):
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

        # URI for this sample
        base_uri = 'http://pid.geoscience.gov.au/sample/'
        this_survey = URIRef(base_uri + self.survey_id)

        # define GA
        ga = URIRef(Survey.URI_GA)

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
        wkt = Literal(self._generate_sample_wkt(), datatype=GEOSP.wktLiteral)
        gml = Literal(self._generate_sample_gml(), datatype=GEOSP.gmlLiteral)

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

        :param model_view: string of one of the model view names available for Sample objects ['igsn', 'dc', '',
            'default']
        :return: HTML string
        """
        html = '<style>' + \
               '   table.data {' + \
               '       border-collapse: collapse;' + \
               '       border: solid 2px black;' + \
               '   }' + \
               '   table.data td, table.data th {' + \
               '       border: solid 1px black;' + \
               '       padding: 5px;' + \
               '   }' + \
               '</style>'

        html += '<table class="data">'
        html += '   <tr><th>Property</th><th>Value</th></tr>'
        if model_view == 'igsn':
            # TODO: complete the properties in this view
            html += '   <tr><th>IGSN</th><td>' + self.survey_id + '</td></tr>'
            html += '   <tr><th>Identifier</th><td>' + self.survey_id + '</td></tr>'
            if self.sampleid is not None:
                html += '   <tr><th>Sample ID</th><td>' + self.sampleid + '</td></tr>'
            if self.date_acquired is not None:
                html += '   <tr><th>Date</th><td>' + self.date_acquired.isoformat() + '</td></tr>'
            if self.sample_type is not None:
                html += '   <tr><th>Sample Type</th><td><a href="' + self.sample_type + '">' + self.sample_type.split('/')[-1] + '</a></td></tr>'
            html += '   <tr><th>Sampling Location (WKT)</th><td>' + self._generate_sample_wkt() + '</td></tr>'
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
            html += '   <tr><th>Coverage</th><td>' + self._generate_sample_wkt() + '</td></tr>'
            if self.date_acquired is not None:
                html += '   <tr><th>Date</th><td>' + self.date_acquired.isoformat() + '</td></tr>'
            if self.remark is not None:
                html += '   <tr><th>Description</th><td>' + self.remark + '</td></tr>'
            if self.material_type is not None:
                html += '   <tr><th>Format</th><td>' + self.material_type + '</td></tr>'
            if self.sample_type is not None:
                html += '   <tr><th>Type</th><td>' + self.sample_type + '</td></tr>'

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
    # s = Sample('http://fake.com', 'AU100')
    # print s.export_dc_xml()
    #
    # # print s.is_xml_export_valid(open('../tests/sample_eg3_IGSN_schema.xml').read())
    # # print s.export_as_igsn_xml()
    pass