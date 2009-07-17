#!/usr/bin/python
# -*- python-indent: 2; py-indent-offset: 2 -*-
# Copyright 2009 Google Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""tests for debmarshal.distros.base."""


__authors__ = [
    'Evan Broder <ebroder@google.com>',
]


try:
  import hashlib as md5
except ImportError:
  import md5
import unittest

from debmarshal.distros import base
from debmarshal import errors


class TestDistributionMeta(unittest.TestCase):
  """Test the Distribution metaclass."""
  def test(self):
    class TestDist1(object):
      __metaclass__ = base.DistributionMeta
      _version = 1
    class TestDist2(TestDist1):
      _version = 2
    class TestDist3(TestDist2):
      _version = 3

    self.assertEqual(TestDist3.version, (3, (2, (1,))))


class TestDistributionInit(unittest.TestCase):
  """Test base.Distribution.__init__."""
  def testNoArguments(self):
    """Test passing no arguments to Distribution.__init__.

    This should work, but be totally uninteresting.
    """
    distro = base.Distribution()

    self.assertEqual(distro.base_config, None)
    self.assertEqual(distro.custom_config, None)

  def testBaseConfig(self):
    """Test missing and extra options to the Distribution base_config."""
    class TestDistro(base.Distribution):
      base_defaults = {'bar': 'baz'}

      base_configurable = set(['foo', 'bar'])

    self.assertRaises(errors.InvalidInput, TestDistro,
                      {})
    self.assertRaises(errors.InvalidInput, TestDistro,
                      {'foo': 'spam',
                       'blah': 'eggs'})

  def testCustomConfig(self):
    """Test missing and extra options to the Distribution custom_config."""
    class TestDistro(base.Distribution):
      custom_defaults = {'bar': 'baz'}

      custom_configurable = set(['foo', 'bar'])

    self.assertRaises(errors.InvalidInput, TestDistro,
                      None, {})
    self.assertRaises(errors.InvalidInput, TestDistro,
                      None, {'foo': 'spam',
                             'blah': 'eggs'})


class TestDistributionGetItems(unittest.TestCase):
  """Test retrieving image settings from a distribution."""
  def testBaseConfig(self):
    class TestDistro(base.Distribution):
      base_configurable = set(['foo'])

      base_defaults = {'bar': 'baz'}

    distro = TestDistro({'foo': 'quux'})

    self.assertEqual(distro.getBaseConfig('foo'), 'quux')
    self.assertEqual(distro.getBaseConfig('bar'), 'baz')
    self.assertRaises(KeyError, distro.getBaseConfig, 'spam')

  def testCustomConfig(self):
    class TestDistro(base.Distribution):
      custom_configurable = set(['foo'])

      custom_defaults = {'bar': 'baz'}

    distro = TestDistro(None, {'foo': 'quux'})

    self.assertEqual(distro.getCustomConfig('foo'), 'quux')
    self.assertEqual(distro.getCustomConfig('bar'), 'baz')
    self.assertRaises(KeyError, distro.getCustomConfig, 'spam')


class TestDistributionClassId(unittest.TestCase):
  """Test calculating the classID for a class."""
  def test(self):
    self.assertEqual(base.Distribution.classId(),
                     'debmarshal.distros.base.Distribution')

    class TestDistro(base.Distribution):
      pass

    self.assertEqual(TestDistro.classId(),
                     'debmarshal.tests.distros.test_base.TestDistro')


class TestDistributionHashConfig(unittest.TestCase):
  class TestDistro(base.Distribution):
    _version = 2

    base_defaults = {'a': '1', 'b': '2'}

    base_configurable = set('abc')

    custom_defaults = {'d': '1', 'e': '2'}

    custom_configurable = set('def')


  def testHashSameConfig(self):
    dist1 = self.TestDistro({'c': '3'}, {'f': '3'})
    dist2 = self.TestDistro({'c': '3'}, {'f': '3'})
    self.assertEqual(dist1.hashBaseConfig(), dist2.hashBaseConfig())
    self.assertEqual(dist1.hashConfig(), dist2.hashConfig())


  def testHashSameBaseConfig(self):
    dist1 = self.TestDistro({'c': '3'}, {'f': '3'})
    dist2 = self.TestDistro({'c': '3'}, {'f': '4'})
    self.assertEqual(dist1.hashBaseConfig(), dist2.hashBaseConfig())
    self.assertNotEqual(dist1.hashConfig(), dist2.hashConfig())

  def testHashDifferentConfigs(self):
    dist1 = self.TestDistro({'c': '3'}, {'f': '3'})
    dist2 = self.TestDistro({'c': '4'}, {'f': '4'})
    self.assertNotEqual(dist1.hashBaseConfig(), dist2.hashBaseConfig())
    self.assertNotEqual(dist1.hashConfig(), dist2.hashConfig())


if __name__ == '__main__':
  unittest.main()