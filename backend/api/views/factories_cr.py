from typing import List
import json
import datetime

from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.db import transaction

from rest_framework.decorators import api_view

from .utils import _get_nearby_factories, _get_client_ip
from ..models import Factory, Image, ReportRecord
from ..serializers import FactorySerializer

import easymap


import logging
logger = logging.getLogger('django')


def _not_in_taiwan(lat, lng):
    lat_invalid = lat < 22 or lat > 25
    lng_invalid = lng < 120 or lng > 122
    return lat_invalid or lng_invalid


def _radius_strange(radius):
    # NOTE: need discussion about it
    return radius > 100 or radius < 0.01


def _all_image_id_exist(image_ids: List[str]) -> bool:
    images = Image.objects.only("id").filter(id__in=image_ids)
    return len(images) == len(image_ids)


@api_view(["GET", "POST"])
def get_nearby_or_create_factories(request):
    # TODO
    if request.method == "GET":
        try:
            latitude = request.GET["lat"]  # 緯度: y
            longitude = request.GET["lng"]  # 經度: x
            radius = request.GET["range"]  # km
        except MultiValueDictKeyError:
            missing_params = [
                p
                for p in ("lat", "lng", "range")
                if p not in request.GET
            ]
            missing_params = ", ".join(missing_params)
            return HttpResponse(
                f"Missing query parameter: {missing_params}.",
                status=400,
            )

        latitude = float(latitude)
        longitude = float(longitude)
        if _not_in_taiwan(latitude, longitude):
            return HttpResponse(
                "The query position is not in the range of Taiwan."
                "Valid query parameters should be: "
                "120 < lng < 122, "
                "22 < lat < 25.",
                status=400,
            )

        radius = float(radius)
        if _radius_strange(radius):
            return HttpResponse(
                f"`range` should be within 0.01 to 100 km, but got {radius}",
                status=400,
            )

        nearby_factories = _get_nearby_factories(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )
        serializer = FactorySerializer(nearby_factories, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == "POST":
        user_ip = _get_client_ip(request)
        post_body = json.loads(request.body)
        # print(post_body)
        serializer = FactorySerializer(data=post_body)
        if not serializer.is_valid():
            logger.WARNING(f" {client_ip} : <serializer.errors> ")
            return JsonResponse(
                serializer.errors,
                status=400,
            )
        longitude = post_body['lng']
        latitude = post_body['lat']
        image_ids = post_body.get('images', [])
        if not _all_image_id_exist(image_ids):
            logger.WARNING(f" {client_ip} : <please check if every image id exist> ")
            return HttpResponse(
                "please check if every image id exist",
                status=400,
            )
        try:
            land_number = easymap.get_land_number(longitude, latitude)['landno']
        except Exception:
            logger.WARNING(f" {client_ip} : <Something wrong happened when getting land numbe> ")
            return HttpResponse(
                "Something wrong happened when getting land number, please try later.",
                status=400,
            )
        
        new_factory_field = {
            'name': post_body["name"],
            'lat': post_body["lat"],
            'lng': post_body["lng"],
            'factory_type': post_body["type"],
            'status_time': datetime.datetime.now(),
            'landcode': land_number,
        }
        new_report_record_field = {
            'user_ip': user_ip,
            'action_type': "POST",
            "action_body": post_body,
            'contact': post_body.get("contact"),
            "others": post_body.get("others", ""),
        }
        
        with transaction.atomic():
            new_factory = Factory.objects.create(**new_factory_field)
            report_record = ReportRecord.objects.create(
                factory=new_factory,
                **new_report_record_field,
            )
            Image.objects.filter(id__in=image_ids).update(
                factory=new_factory,
                report_record=report_record
            )
        serializer = FactorySerializer(new_factory)
        logger.INFO(f" {user_ip} : <Create factory> {new_factory_field['name']} {new_factory_field['factory_type']} {new_factory_field['landcode']} ")
        return JsonResponse(serializer.data, safe=False)
