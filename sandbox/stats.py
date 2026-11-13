import datetime as dt

SHANGHAI = dt.timezone(dt.timedelta(hours=8))
FINISHED = ('completed', 'failed')


def parse_time(text):
    return dt.datetime.fromisoformat(text.replace('Z', '+00:00'))


def day_of(task):
    return parse_time(task['created_at']).date().isoformat()


def daily_counts(tasks):
    counts = {}
    for task in tasks:
        day = day_of(task)
        counts[day] = counts.get(day, 0) + 1
    return dict(sorted(counts.items()))


def status_counts(tasks):
    counts = {}
    for task in tasks:
        counts[task['status']] = counts.get(task['status'], 0) + 1
    return dict(sorted(counts.items()))


def failure_rate(tasks):
    finished = [t for t in tasks if t['status'] in FINISHED]
    failed = [t for t in finished if t['status'] == 'failed']
    return round(len(failed) / len(finished), 4) if finished else None


def pages(items, size):
    return [items[start:start + size] for start in range(0, len(items), size)]
