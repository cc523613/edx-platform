"""
Tests for exporting OLX content.
"""

from __future__ import absolute_import

import shutil
import tarfile
import unittest
from six import StringIO
from tempfile import mkdtemp

import ddt
import six
from django.core.management import CommandError, call_command
from path import Path as path

from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class TestArgParsingCourseExportOlx(unittest.TestCase):
    """
    Tests for parsing arguments for the `export_olx` management command
    """
    def test_no_args(self):
        """
        Test export command with no arguments
        """
        if six.PY2:
            errstring = "Error: too few arguments"
        else:
            errstring = "Error: the following arguments are required: course_id"
        with self.assertRaisesRegexp(CommandError, errstring):
            call_command('export_olx')


@ddt.ddt
class TestCourseExportOlx(ModuleStoreTestCase):
    """
    Test exporting OLX content from a course or library.
    """

    def test_invalid_course_key(self):
        """
        Test export command with an invalid course key.
        """
        errstring = "Unparsable course_id"
        with self.assertRaisesRegexp(CommandError, errstring):
            call_command('export_olx', 'InvalidCourseID')

    def test_course_key_not_found(self):
        """
        Test export command with a valid course key that doesn't exist.
        """
        errstring = "Invalid course_id"
        with self.assertRaisesRegexp(CommandError, errstring):
            call_command('export_olx', 'x/y/z')

    def create_dummy_course(self, store_type):
        """Create small course."""
        course = CourseFactory.create(default_store=store_type)
        self.assertTrue(
            modulestore().has_course(course.id),
            u"Could not find course in {}".format(store_type)
        )
        return course.id

    def check_export_file(self, tar_file, course_key):
        """Check content of export file."""
        names = tar_file.getnames()
        dirname = "{0.org}-{0.course}-{0.run}".format(course_key)
        self.assertIn(dirname, names)
        # Check if some of the files are present, without being exhaustive.
        self.assertIn("{}/about".format(dirname), names)
        self.assertIn("{}/about/overview.html".format(dirname), names)
        self.assertIn("{}/assets/assets.xml".format(dirname), names)
        self.assertIn("{}/policies".format(dirname), names)

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_export_course(self, store_type):
        test_course_key = self.create_dummy_course(store_type)
        tmp_dir = path(mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_dir)
        filename = tmp_dir / 'test.tar.gz'
        call_command('export_olx', '--output', filename, six.text_type(test_course_key))
        with tarfile.open(filename) as tar_file:
            self.check_export_file(tar_file, test_course_key)

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_export_course_stdout(self, store_type):
        test_course_key = self.create_dummy_course(store_type)
        out = StringIO()
        call_command('export_olx', six.text_type(test_course_key), stdout=out)
        out.seek(0)
        output = out.read()
        with tarfile.open(fileobj=StringIO(output)) as tar_file:
            self.check_export_file(tar_file, test_course_key)
