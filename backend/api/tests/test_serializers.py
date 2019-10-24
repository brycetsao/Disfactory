from datetime import datetime, timedelta

from django.test import TestCase

from ..serializers import FactorySerializer, ImageSerializer
from ..models import Factory, ReportRecord, Image


class SerializersTestCase(TestCase):

    def test_factory_serializer_correct_report_date(self):
        factory = Factory(
            name="test factory",
            lat=23,
            lng=121,
            landcode="000120324",
            factory_type="2-1",
            status="A",
            status_time=datetime.now()
        )
        factory.save()

        # created first time, w/o any ReportRecord
        # should have null reported_at
        serialized_factory = FactorySerializer(factory)
        self.assertEqual(serialized_factory.data["type"], factory.factory_type)
        self.assertIsNone(serialized_factory.data["reported_at"])

        report_record1 = ReportRecord.objects.create(
            factory=factory,
            action_type="post_image",
            action_body={},
            contact="0800-092000",
            others="猴～被我拍到了吧",
            created_at=factory.created_at + timedelta(seconds=1)
        )
        im1 = Image.objects.create(
            image_path="https://i.imgur.com/RxArJUc.png",
            factory=factory,
            report_record=report_record1
        )
        report_record2 = ReportRecord.objects.create(
            factory=factory,
            action_type="post_image",
            action_body={},
            contact="07-7533967",
            others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            created_at=factory.created_at + timedelta(days=1),
        )
        im2 = Image.objects.create(
            image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
            factory=factory,
            report_record=report_record2,
        )
        report_record_latest = ReportRecord.objects.create(
            factory=factory,
            action_type="PUT",
            action_body={"status": "D"},
            contact="02-2392-0371",
            others="已呈報",
            created_at=factory.created_at + timedelta(days=2)
        )  # this one should be the `reported_at` of serialized factory
        factory.refresh_from_db()
        serialized_factory = FactorySerializer(factory)
        self.assertEqual(
            serialized_factory.data["reported_at"],
            report_record_latest.created_at,
        )
        self.assertCountEqual(serialized_factory.data["images"], [
            ImageSerializer(im1).data,
            ImageSerializer(im2).data,
        ])

    def test_image_serializer_coorect_url(self):
        img = Image(image_path="https://imgur.com/qwer")
        serialized_img = ImageSerializer(img)

        self.assertEqual(serialized_img.data['url'], img.image_path)


