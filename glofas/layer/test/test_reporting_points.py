import os
import unittest
from datetime import datetime

from osgeo import gdal

from glofas.layer.reporting_point import (
    ReportingPointAPI,
    ReportingPointResult)


class TestReportingPoint(unittest.TestCase):

    def fixture_path(self, *args):
        return os.path.join(os.path.dirname(__file__), 'resources', *args)

    def setUp(self):
        self.api = ReportingPointAPI()

    def test_fetch_info(self):
        time_slice = datetime(year=2019, month=12, day=15)
        self.api.time = time_slice

        ds = gdal.OpenEx(self.fixture_path('reporting_point_layer.geojson'))
        # Sample of using WFS:
        # ds = ogr.Open(
        #     'http://78.47.62.69/geoserver/kartoza/ows?service=WFS&version=1'
        #     '.0.0&request=GetFeature&typeName=kartoza:reporting_point'
        #     '&maxFeatures=50&outputFormat=application/json')
        point_layer = ds.GetLayer()

        feature_info = self.api.get_feature_info(point_layer, srs='EPSG:4326')

        self.assertTrue(feature_info)
        reporting_point_res = feature_info[0]
        self.assertEqual(reporting_point_res.station_name, 'CISADANE SERPONG')
        self.assertEqual(reporting_point_res.country, 'Indonesia')
        self.assertEqual(reporting_point_res.basin, 'Na')
        self.assertEqual(reporting_point_res.coord.lon, 106.65)
        self.assertEqual(reporting_point_res.coord.lat, -6.35)
        self.assertEqual(reporting_point_res.point_no, 1765)
        self.assertEqual(reporting_point_res.max_eps.medium, 4)
        self.assertEqual(reporting_point_res.max_eps.high, 2)
        self.assertEqual(reporting_point_res.max_eps.severe, 2)
        self.assertEqual(reporting_point_res.alert_level, 0)

        medium_eps_array = [0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0, 2.0, 2.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        high_eps_array = [0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        severe_eps_array = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self.assertEqual(
            reporting_point_res.eps_array(ReportingPointResult.ALERT_LEVEL_MEDIUM),
            medium_eps_array)
        self.assertEqual(
            reporting_point_res.eps_array(ReportingPointResult.ALERT_LEVEL_HIGH),
            high_eps_array)
        self.assertEqual(
            reporting_point_res.eps_array(ReportingPointResult.ALERT_LEVEL_SEVERE),
            severe_eps_array)
