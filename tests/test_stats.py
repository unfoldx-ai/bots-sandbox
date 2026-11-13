import json
import tempfile
import unittest

from sandbox import build, stats


def task(i, status='completed', at='2026-11-03T02:00:00Z'):
    return {'id': f'T-{i:03d}', 'status': status, 'created_at': at}


class StatsTest(unittest.TestCase):
    def test_daily_counts_group_by_day(self):
        tasks = [task(1, at='2026-11-03T01:00:00Z'), task(2, at='2026-11-03T05:00:00Z'), task(3, at='2026-11-04T03:00:00Z')]
        self.assertEqual(stats.daily_counts(tasks), {'2026-11-03': 2, '2026-11-04': 1})

    def test_failure_rate_over_finished_tasks(self):
        tasks = [task(1), task(2, 'failed'), task(3), task(4, 'running')]
        self.assertEqual(stats.failure_rate(tasks), 0.3333)

    def test_failure_rate_without_finished_tasks_is_unknown(self):
        self.assertIsNone(stats.failure_rate([task(1, 'running')]))

    def test_pages_split_items(self):
        items = list(range(20))
        self.assertEqual(stats.pages(items, 10), [list(range(10)), list(range(10, 20))])


class BuildTest(unittest.TestCase):
    def test_site_reports_version_and_pages(self):
        tasks = [task(i) for i in range(1, 21)]
        with tempfile.TemporaryDirectory() as out:
            summary = build.build(tasks, out, 'a' * 40, 'main')
            self.assertEqual(json.load(open(f'{out}/version.json'))['sha'], 'a' * 40)
            self.assertEqual(summary['pages'], 2)
            self.assertEqual(len(json.load(open(f'{out}/api/tasks/2.json'))['items']), 10)


if __name__ == '__main__':
    unittest.main()
