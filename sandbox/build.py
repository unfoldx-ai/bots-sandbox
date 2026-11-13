import argparse
import datetime as dt
import json
import pathlib

from sandbox import stats

PAGE_SIZE = 10
INDEX = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>任务看板（沙盒）</title>
<style>body{font:15px/1.6 system-ui,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#1f2328;background:#fff}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #d0d7de;padding:4px 8px;text-align:left}
code{background:#f6f8fa;padding:1px 4px;border-radius:4px}</style></head>
<body><h1>任务看板（沙盒测试环境）</h1><p id="meta">加载中…</p><h2>每日任务数</h2><table id="daily"></table>
<h2>任务列表</h2><table id="tasks"><tr><th>编号</th><th>状态</th><th>创建时间</th></tr></table>
<script>
(async () => {
  const get = p => fetch(p, {cache: 'no-store'}).then(r => r.json());
  const s = await get('api/summary.json');
  document.getElementById('meta').innerHTML = `版本 <code>${s.version.slice(0, 7)}</code> · 共 ${s.total} 个任务 · 失败率 ${s.failure_rate}`;
  document.getElementById('daily').innerHTML = Object.entries(s.daily).map(([d, n]) => `<tr><td>${d}</td><td>${n}</td></tr>`).join('');
  for (let i = 1; i <= s.pages; i++) {
    const page = await get(`api/tasks/${i}.json`);
    for (const t of page.items) document.getElementById('tasks').insertAdjacentHTML('beforeend', `<tr><td>${t.id}</td><td>${t.status}</td><td>${t.created_at}</td></tr>`);
  }
})();
</script></body></html>
'''


def build(tasks, out, sha, ref):
    out = pathlib.Path(out)
    (out / 'api' / 'tasks').mkdir(parents=True, exist_ok=True)
    chunks = stats.pages(tasks, PAGE_SIZE)
    summary = {'version': sha, 'total': len(tasks), 'by_status': stats.status_counts(tasks),
               'daily': stats.daily_counts(tasks), 'failure_rate': stats.failure_rate(tasks),
               'page_size': PAGE_SIZE, 'pages': len(chunks)}
    (out / 'api' / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    for number, chunk in enumerate(chunks, 1):
        (out / 'api' / 'tasks' / f'{number}.json').write_text(json.dumps({'page': number, 'items': chunk}, ensure_ascii=False))
    (out / 'version.json').write_text(json.dumps({'sha': sha, 'ref': ref, 'built_at': dt.datetime.now(dt.timezone.utc).isoformat()}))
    (out / 'index.html').write_text(INDEX)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/tasks.json')
    parser.add_argument('--out', default='site')
    parser.add_argument('--sha', required=True)
    parser.add_argument('--ref', required=True)
    args = parser.parse_args()
    print(json.dumps(build(json.loads(pathlib.Path(args.data).read_text()), args.out, args.sha, args.ref), ensure_ascii=False))


if __name__ == '__main__':
    main()
