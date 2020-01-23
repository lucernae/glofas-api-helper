# GloFAS API Helper

CI Status:
Master branch:[![Build Status](https://travis-ci.com/lucernae/glofas-api-helper.svg?branch=master)](https://travis-ci.com/lucernae/glofas-api-helper)

This helper package is intended to use as API Wrapper to GloFAS OWS API.

[GloFAS](https://www.globalfloods.eu/) is a Global System for Flood Awareness.

# Installations

The modules needs python GDAL.
Installing GDAL vary depending on OS distributions.
In most debian distro, you can do it like this

```
apt -y update
apt -y install gdal-bin libgdal-dev python3-gdal
```

It also needs python 3.

You can install the module itself directly from github like this:

```
pip install -e git+https://github.com/lucernae/glofas-api-helper.git@master#egg=GloFAS-API-Wrapper-0.1
```

Current available endpoint:


## Reporting Point API

The corresponding layer is under Hydrological > Reporting Point.
OWS layer name is **RPG_U**.

Use the ReportingPointAPI to iterate an OGR point feature layer, and fetch nearest 
reporting point forecast.

```python
from glofas.layer.reporting_point import ReportingPointAPI, ReportingPointResult
from osgeo import gdal

api = ReportingPointAPI()
data_source = gdal.OpenEx('reporting_point_location.geojson')
point_layer = data_source.GetLayer()

# Automatically means fetch today's forecast, unless you specify the time slice
# api.time = datetime(year=2019, month=12, day=15)
feature_info = api.get_feature_info(point_layer)
# feature info is a list of forecast information for each point layer

reporting_point_result = feature_info[0]
# This is an instance of ReportingPointResult

# Query the information easily
reporting_point_result.station_name
reporting_point_result.country
reporting_point_result.basin
reporting_point_result.coord.lon
reporting_point_result.coord.lat

# forecast array for the following 30 days (EPS max probability of exceeding threshold)

# forecast for Severe alert
reporting_point_result.eps_array(ReportingPointResult.ALERT_LEVEL_SEVERE)

```
