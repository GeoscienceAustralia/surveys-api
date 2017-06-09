from lxml import etree
from lxml import objectify
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal, BNode
import requests
from datetime import datetime
from ldapi.ldapi import LDAPI
from flask import Response, render_template, redirect
import config


class EntityRenderer:
    """
    This class represents a Survey and methods in this class allow one to be loaded from GA's internal Oracle
    ARGUS database and to be exported in a number of mimetypes including RDF, according to the 'GA Public Data Ontology'
    and PROV-O, the Provenance Ontology.
    """

    URI_MISSSING = 'http://www.opengis.net/def/nil/OGC/0/missing'
    URI_INAPPLICABLE = 'http://www.opengis.net/def/nil/OGC/0/inapplicable'
    URI_GA = 'http://pid.geoscience.gov.au/org/ga'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.entity_name = None


    def render(self, view, mimetype):
        if self.survey_name is None:
            return Response('Survey with ID {} not found.'.format(self.survey_id), status=404, mimetype='text/plain')

        if view == 'gapd':
            if mimetype == 'text/html':
                return self.export_html(model_view=view)
            else:
                return Response(self.export_rdf(view, mimetype), mimetype=mimetype)
        elif view == 'argus':  # XML only for this view
            return redirect(config.XML_API_URL_SURVEY.format(self.survey_id), code=303)
        elif view == 'prov':
            if mimetype == 'text/html':
                return self.export_html(model_view=view)
            else:
                return Response(self.export_rdf(view, mimetype), mimetype=mimetype)
        elif view == 'sosa':  # RDF only for this view
            return Response(self.export_rdf(view, mimetype), mimetype=mimetype)

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
        self.release_date = datetime.strptime(root.ROW.RELEASEDATE.text, "%Y-%m-%dT%H:%M:%S") if root.ROW.RELEASEDATE != '' else None
        self.onshore_offshore = root.ROW.ONSHORE_OFFSHORE if root.ROW.ONSHORE_OFFSHORE != '' else None
        self.start_date = datetime.strptime(root.ROW.STARTDATE.text, "%Y-%m-%dT%H:%M:%S") if root.ROW.STARTDATE != '' else None
        self.end_date = datetime.strptime(root.ROW.ENDDATE.text, "%Y-%m-%dT%H:%M:%S") if root.ROW.ENDDATE != '' else None
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

    def export_rdf(self, model_view='default', rdf_mime='text/turtle'):
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

        # URI for this survey
        base_uri = 'http://pid.geoscience.gov.au/survey/'
        this_survey = URIRef(base_uri + self.survey_id)

        # define GA
        ga = URIRef(SurveyRenderer.URI_GA)

        # select model view
        if model_view == 'gapd' or model_view == 'prov':
            PROV = Namespace('http://www.w3.org/ns/prov#')
            g.bind('prov', PROV)

            g.add((this_survey, RDF.type, PROV.Activity))

            GEOSP = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geosp', GEOSP)

            AUROLE = Namespace('http://communications.data.gov.au/def/role/')
            g.bind('aurole', AUROLE)

            # default model is the GAPD model
            # Activity properties
            # TODO: add in label, startedAtTime, endedAtTime, atLocation

            # Agents
            contractor = BNode()
            contractor_agent = BNode()
            g.add((contractor_agent, RDF.type, PROV.Agent))
            g.add((contractor, RDF.type, PROV.Attribution))
            g.add((contractor, PROV.agent, contractor_agent))
            g.add((contractor, PROV.hadRole, AUROLE.PrincipalInvestigator))
            g.add((contractor_agent, RDFS.label, Literal(self.contractor, datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, contractor))

            operator = BNode()
            operator_agent = BNode()
            g.add((operator_agent, RDF.type, PROV.Agent))
            g.add((operator, RDF.type, PROV.Attribution))
            g.add((operator, PROV.agent, operator_agent))
            g.add((operator, PROV.hadRole, AUROLE.Sponsor))
            g.add((operator_agent, RDFS.label, Literal(self.operator, datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, operator))

            processor = BNode()
            processor_agent = BNode()
            g.add((processor_agent, RDF.type, PROV.Agent))
            g.add((processor, RDF.type, PROV.Attribution))
            g.add((processor, PROV.agent, processor_agent))
            g.add((processor, PROV.hadRole, AUROLE.Processor))
            g.add((processor_agent, RDFS.label, Literal(self.processor, datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, processor))

            publisher = BNode()
            g.add((ga, RDF.type, PROV.Org))
            g.add((publisher, RDF.type, PROV.Attribution))
            g.add((publisher, PROV.agent, ga))
            g.add((publisher, PROV.hadRole, AUROLE.Publisher))
            g.add((ga, RDFS.label, Literal("Geoscience Australia", datatype=XSD.string)))
            g.add((this_survey, PROV.qualifiedAttribution, publisher))

            # TODO: add in other Agents

            if model_view == 'gapd':
                # Geometry
                SAMFL = Namespace('http://def.seegrid.csiro.au/ontology/om/sam-lite#')
                g.bind('samfl', SAMFL)

                # Survey location in GML & WKT, formulation from GeoSPARQL

                geometry = BNode()
                g.add((this_survey, PROV.hadLocation, geometry))
                g.add((geometry, RDF.type, SAMFL.Polygon))
                # g.add((geometry, GEOSP.asGML, gml))
                g.add((geometry, GEOSP.asWKT, Literal(self.wkt_polygon, datatype=GEOSP.wktLiteral)))

                # GAPD model required namespaces
                GAPD = Namespace('http://pid.geoscience.gov.au/def/ont/gapd#')
                g.bind('gapd', GAPD)

                # classing the Survey in GAPD
                g.add((this_survey, RDF.type, GAPD.PublicSurvey))

                # TODO: add in other Survey properties
            elif model_view == 'prov':
                # redundant relationships just for SVG viewing
                # TODO: add in a recognition of Agent roles for the graph
                g.add((this_survey, RDFS.label, Literal('Survey ' + self.survey_id, datatype=XSD.string)))
                g.add((ga, RDF.type, PROV.Agent))
                g.add((this_survey, PROV.wasAssociatedWith, contractor_agent))
                g.add((this_survey, PROV.wasAssociatedWith, operator_agent))
                g.add((this_survey, PROV.wasAssociatedWith, processor_agent))
                g.add((this_survey, PROV.wasAssociatedWith, ga))
        elif model_view == 'sosa':
            SOSA = Namespace('http://www.w3.org/ns/sosa/')
            g.bind('sosa', SOSA)

            # Sampling
            g.add((this_survey, RDF.type, SOSA.Sampling))
            TIME = Namespace('http://www.w3.org/2006/time#')
            g.bind('time', TIME)

            if self.start_date is not None and self.end_date is not None:
                t = BNode()
                g.add((t, RDF.type, TIME.ProperInterval))

                start = BNode()
                g.add((start, RDF.type, TIME.Instant))
                g.add((start, TIME.inXSDDateTime, Literal(self.start_date.date(), datatype=XSD.date)))
                g.add((t, TIME.hasBeginning, start))
                finish = BNode()
                g.add((finish, RDF.type, TIME.Instant))
                g.add((finish, TIME.inXSDDateTime, Literal(self.end_date.date(), datatype=XSD.date)))
                g.add((t, TIME.hasEnd, finish))
                g.add((this_survey, TIME.hasTime, t))  # associate

            elif self.start_date is not None:
                t = BNode()
                g.add((t, RDF.type, TIME.Instant))
                g.add((t, TIME.inXSDDateTime, Literal(self.start_date.date(), datatype=XSD.date)))
                g.add((this_survey, TIME.hasTime, t))  # associate

            # Platform  # TODO: add lookup for 'Plane' etc to a vessel type vocab
            platform = BNode()
            g.add((platform, RDF.type, URIRef('http://pid.geoscience.gov.au/platform/' + self.vessel_type)))
            g.add((platform, RDFS.subClassOf, SOSA.Platform))
            g.add((platform, RDFS.label, Literal(self.vessel, datatype=XSD.string)))

            # Sampler
            if self.mag_instrument is not None:
                sampler_mag = BNode()
                g.add((sampler_mag, RDF.type, URIRef(self.mag_instrument)))
                g.add((sampler_mag, RDFS.subClassOf, SOSA.Sampler))
                g.add((sampler_mag, SOSA.madeSampling, this_survey))  # associate # TODO: resolve double madeSampling
                g.add((sampler_mag, SOSA.isHostedBy, platform))  # associate

            if self.rad_instrument is not None:
                sampler_rad = BNode()
                g.add((sampler_rad, RDF.type, URIRef(self.rad_instrument)))
                g.add((sampler_rad, RDFS.subClassOf, SOSA.Sampler))
                g.add((sampler_rad, SOSA.madeSampling, this_survey))  # associate
                g.add((sampler_rad, SOSA.isHostedBy, platform))  # associate

            if self.mag_instrument is None and self.rad_instrument is None:
                sampler = BNode()
                g.add((sampler, RDF.type, SOSA.Sampler))
                g.add((sampler, SOSA.isHostedBy, platform))  # associate

            # FOI
            foi = URIRef('http://pid.geoscience.gov.au/feature/earthSusbsurface')
            g.add((foi, RDFS.label, Literal('Earth Subsurface', datatype=XSD.string)))
            g.add((foi, RDFS.comment, Literal('Below the earth\'s terrestrial surface', datatype=XSD.string)))
            g.add((this_survey, SOSA.hasFeatureOfInterest, foi))  # associate

            # Sample
            sample = BNode()
            g.add((sample, RDF.type, SOSA.Sample))
            g.add((this_survey, SOSA.hasResult, sample))  # associate
            g.add((foi, SOSA.hasSample, sample))  # associate with FOI

            # Sample geometry
            GEOSP = Namespace('http://www.opengis.net/ont/geosparql#')
            g.bind('geosp', GEOSP)
            geometry = BNode()
            g.add((geometry, RDF.type, GEOSP.Geometry))
            g.add((geometry, GEOSP.asWKT, Literal(self.wkt_polygon, datatype=GEOSP.wktLiteral)))
            g.add((sample, GEOSP.hasGeometry, geometry))  # associate


        return g.serialize(format=LDAPI.get_rdf_parser_for_mimetype(rdf_mime))

    def export_html(self, model_view='gapd'):
        """
        Exports this instance in HTML, according to a given model from the list of supported models.

        :param model_view: string of one of the model view names available for survey objects
        :return: HTML string
        """
        if model_view == 'gapd':
            view_html = render_template(
                'survey_gapd.html',
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
                line_km=self.line_km,
                total_km=self.total_km,
                line_spacing=self.line_spacing,
                line_direction=self.line_direction,
                tie_spacing=self.tie_spacing,
                area=self.square_km,
                crystal_volume=self.crystal_volume,
                up_crystal_volume=self.up_crystal_volume,
                digital_data=self.digital_data,
                geodetic_datum=self.geodetic_datum,
                asl=self.asl,
                agl=self.agl,
                mag_instrument=self.mag_instrument,
                rad_instrument=self.rad_instrument,
                wkt_polygon=self.wkt_polygon
            )
        elif model_view == 'prov':
            prov_turtle = self.export_rdf('prov', 'text/turtle')
            g = Graph().parse(data=prov_turtle, format='turtle')

            view_html = render_template(
                'survey_prov.html',
                visjs=self._make_vsjs(g),
                prov_turtle=prov_turtle,
            )

        return render_template(
            'page_survey.html',
            view_html=view_html,
            survey_id=self.survey_id,
            end_date=self.end_date,
            survey_type=self.survey_type,
            date_now=datetime.now().strftime('%Y-%m-%d')
        )


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
    s = EntityRenderer(921)
    print(s.render(v, f))
