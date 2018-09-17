import unittest2 as unittest
import pytest

from foss_finder.utils.tracker import FossTracker


class TrackerTestCase(unittest.TestCase):

    def test_basic(self):
        tracker = FossTracker()
        tracker.add_project('foo')
        tracker.add_project('bar')
        self.assertEqual(tracker.number_of_projects_processed, 2)

        tracker.add_foss_to_project('foo', 'foss1')
        tracker.add_foss_to_project('foo', 'foss2')
        tracker.add_foss_to_project('bar', 'foss3')
        tracker.add_foss_to_project('foo', 'foss4')

        self.assertEqual(tracker.number_of_foss_found, 4)

        summary = tracker.report_project_summary('foo')
        self.assertTrue('Project foo:' in summary)
        self.assertTrue('Number of open source projects found: 3' in summary)
