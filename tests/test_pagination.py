import json
import tempfile
import unittest

from sandbox import build, stats


def task(i, status='completed', at='2026-11-03T02:00:00Z'):
    return {'id': f'T-{i:03d}', 'status': status, 'created_at': at}


class PagesTest(unittest.TestCase):
    def test_pages_of_empty_list_is_empty(self):
        self.assertEqual(stats.pages([], 10), [])

    def test_pages_keeps_list_shorter_than_one_page(self):
        items = list(range(7))
        self.assertEqual(stats.pages(items, 10), [items])

    def test_pages_splits_into_exact_pages(self):
        items = list(range(20))
        self.assertEqual(stats.pages(items, 10), [items[:10], items[10:]])

    def test_pages_keeps_remainder_page(self):
        items = list(range(37))
        result = stats.pages(items, 10)
        self.assertEqual([len(page) for page in result], [10, 10, 10, 7])
        self.assertEqual([item for page in result for item in page], items)


class BuildPaginationTest(unittest.TestCase):
    def test_build_publishes_remainder_page_for_37_tasks(self):
        tasks = [task(i) for i in range(1, 38)]
        with tempfile.TemporaryDirectory() as out:
            summary = build.build(tasks, out, 'b' * 40, 'main')
            self.assertEqual(summary['total'], 37)
            self.assertEqual(summary['pages'], 4)
            listed = []
            for number in range(1, summary['pages'] + 1):
                with open(f'{out}/api/tasks/{number}.json') as page:
                    listed += json.load(page)['items']
            self.assertEqual(len(listed), 37)
            with open(f'{out}/api/tasks/4.json') as last:
                self.assertEqual(len(json.load(last)['items']), 7)


if __name__ == '__main__':
    unittest.main()
