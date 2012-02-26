from gears.assets import Requirements
from unittest2 import TestCase


class FakeAsset(object):

    def __init__(self):
        self.requirements = Requirements(self)


class AssetRequirementsTests(TestCase):

    def setUp(self):
        self.asset = FakeAsset()

        self.a = FakeAsset()
        self.b = FakeAsset()
        self.c = FakeAsset()
        self.d = FakeAsset()
        self.e = FakeAsset()

        self.asset.requirements.add(self.a)
        self.asset.requirements.add(self.b)
        self.asset.requirements.add(self.c)
        self.asset.requirements.add(self.asset)
        self.asset.requirements.add(self.d)
        self.asset.requirements.add(self.e)

    def test_firstly_adds_before(self):
        self.assertEqual(self.asset.requirements.before, [self.a, self.b, self.c])

    def test_adds_after_in_the_end(self):
        self.assertEqual(self.asset.requirements.after, [self.d, self.e])
