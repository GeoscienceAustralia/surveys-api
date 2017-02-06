# Surveys Linked Data API
A Linked Data API for GA's geophysics Survey records.

This is a Python Flask HTTP API that provides access to metadata about Surveys stored in GA's corporate database known as ARGUS. Surveys are data collection activities undertaken by various vehicles (usually ships and aeroplanes). The data collected is of a range of types including magnetics, radiometrics and LiDAR. The data are stored at the National Computational Infrastructure (NCI) (http://www.ngi.org.au) in netCDF format and are catalogued in GA's corporate data catalogue eCat (http://ecat.ga.gov.au/geonetwork/). The data stored at the NCI and their catalogue entries contain links back to these Surveys. 


#### Object representation
This Linked Data API represents objects - Surveys and Registers of Surveys (collections) according to a variety of 'views' (models) and in a variety of formats. There is a native 'GA Survey' metadata model (an [OWL ontology](https://en.wikipedia.org/wiki/Web_Ontology_Language)) that we have made to cater for all the metadata we need to represent. The Linked Data API serves this model, in a variety of formats, by default with HTML being the default format.

In addition to the GA Survey model of Surveys' metadata, the Linked Data API also serves other, well known and standardised, model views of Surveys, such as a provenance view according to [PROV-O](https://www.w3.org/TR/prov-o/), the [W3C's](https://www.w3.org/) provenance ontology.


##### Provenance Modelling
We model the Surveys as Activity class objects according to PROV-O, the provenance ontology. We then model the data from the Surveys as PROV-O Entities, thus the relationship between Entities and Surveys is a normal PROV-O Activity <--> Entity relationship, one of *wasGeneratedBy*, i.e.:
 
 > Entity X *wasGeneratedBy* Survey Y
 
The inverse of this is:

> Survey Y *generated* Entity X


## About this code repository
This code repository is developed and maintained by [Geoscience Australia](http://www.ga.gov.au) (GA). It is licensed as Creative Commons 4.0 Internationals (see LICENSE). 


### Authors and Contact
**Nicholas Car**  
Geoscience Australia  
<nicholas.car@ga.gov.au>   
  
**Alex Ip**  
Geoscience Australia  
<alex.ip@ga.gov.au>  

