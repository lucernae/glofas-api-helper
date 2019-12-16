import datetime
import json
from collections import namedtuple
from datetime import timedelta

from owslib import wms
from lxml import html


class ReportingPointResult(object):

    Point = namedtuple('Point', 'lon lat')
    EPS = namedtuple('EPS', 'medium high severe')
    ForecastEPS = namedtuple(
        'ForecastEPS', 'forecast_date eps_value')
    ForecastEPSList = namedtuple(
        'ForecastEPSList', 'medium high severe')

    ALERT_LEVEL_MEDIUM = 'medium'
    ALERT_LEVEL_HIGH = 'high'
    ALERT_LEVEL_SEVERE = 'severe'

    def __init__(self, forecast_date, html=None):
        self.html = html
        self.forecast_date = forecast_date
        self._parse_result()

    def _parse_result(self):
        self.root_html = html.fragment_fromstring(
            self.html, create_parent='div')
        point_info_row = self.root_html.xpath(
            '//table[@class="tbl_info_point" and @summary="Point Information"]'
            '/tr[2]/td')
        self.country = point_info_row[0].text
        self.basin = point_info_row[1].text
        self.station_name = point_info_row[2].text
        lon = float(point_info_row[3].text)
        lat = float(point_info_row[4].text)
        self.coord = ReportingPointResult.Point(lon, lat)
        point_forecast = self.root_html.xpath(
            '//table[@class="tbl_info_point" and @summary="Point Forecast"]'
            '/tr[2]/td')
        self.point_no = int(point_forecast[1].text)
        eps = point_forecast[2].text
        eps_list = [float(e) for e in eps.split('/')]
        self.max_eps = ReportingPointResult.EPS(
            eps_list[0], eps_list[1], eps_list[2])
        self.alert_level = int(point_forecast[3].text)

        # Forecast arrays
        medium_table = self.root_html.xpath(
            '//table[@summary="Medium Alert Level"]')[0]
        medium_forecast_list = self._parse_forecast_table(medium_table)

        high_table = self.root_html.xpath(
            '//table[@summary="High Alert Level"]')[0]
        high_forecast_list = self._parse_forecast_table(high_table)

        severe_table = self.root_html.xpath(
            '//table[@summary="Severe Alert Level"]')[0]
        severe_forecast_list = self._parse_forecast_table(severe_table)

        self.forecast_eps_list = ReportingPointResult.ForecastEPSList(
            medium_forecast_list,
            high_forecast_list,
            severe_forecast_list)

    def _parse_forecast_table(self, forecast_table_element):
        current_forecast_date_string = self.forecast_date.strftime(
            '%d/%m/%Y')
        xpath = './/td[normalize-space(text())="{date}"]' \
                '//parent::tr/td'.format(
            date=current_forecast_date_string)
        tds = forecast_table_element.xpath(xpath)
        # first 5 columns is just offset and should be skipped
        tds = [td for td in tds][5:]
        current_date = self.forecast_date
        forecast_list = []
        for td in tds:
            eps_value = td.text or 0
            eps_value = float(eps_value)
            forecast_eps = ReportingPointResult.ForecastEPS(
                current_date, eps_value)
            current_date = current_date + timedelta(days=1)
            forecast_list.append(forecast_eps)
        return forecast_list

    def eps_array(self, alert_level):
        forecast_list = getattr(self.forecast_eps_list, alert_level)
        return [f.eps_value for f in forecast_list]


class ReportingPointAPI(object):

    _default_ows_endpoint = 'http://globalfloods-ows.ecmwf.int/glofas-ows/'

    def __init__(self, ows_endpoint=None, time=None):

        self.ows_endpoint = ows_endpoint \
                            or ReportingPointAPI._default_ows_endpoint
        self.wms = wms.WebMapService(self.ows_endpoint, '1.3.0')
        self.layers = ['RPG_U']
        self.time = time
        if self.time is None:
            self.time = datetime.datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0)

    def get_feature_info(self, point_location_layer, srs='EPSG:4326'):
        feature_info = []
        for feature in point_location_layer:
            geom = feature.GetGeometryRef()
            response = self.wms.getfeatureinfo(
                layers=self.layers,
                srs=srs,
                info_format='application/json',
                size=(512, 512),
                bbox=(geom.GetX(), geom.GetY(), geom.GetX(), geom.GetY()),
                xy=(256, 256),
                time=self.time.isoformat()
            )
            result = json.loads(response.read())
            reporting_point_result = ReportingPointResult(
                self.time,
                html=result['content']['point'])
            feature_info.append(reporting_point_result)

        return feature_info
