"""Entry check against the deployed test environment. Maintained by humans; agents must not modify it."""
import argparse
import json
import os
import sys
import time
import urllib.request


def get(url):
    with urllib.request.urlopen(url + ('&' if '?' in url else '?') + f't={time.time_ns()}', timeout=20) as response:
        return json.load(response)


def wait_version(base, expected, seconds):
    deadline = time.time() + seconds
    while True:
        version = get(base + '/version.json')
        if not expected or version['sha'] == expected or time.time() > deadline:
            return version
        time.sleep(10)


def check(base, expected, wait):
    version = wait_version(base, expected, wait)
    problems = []
    if expected and version['sha'] != expected:
        problems.append(f"测试环境版本是 {version['sha']}，不是要验证的 {expected}")
    summary = get(base + '/api/summary.json')
    if summary['version'] != version['sha']:
        problems.append('summary.json 与 version.json 的版本不一致')
    listed = []
    for number in range(1, summary['pages'] + 1):
        listed += get(f'{base}/api/tasks/{number}.json')['items']
    if len(listed) != summary['total']:
        problems.append(f"任务列表分页一共只能翻到 {len(listed)} 个任务，总数却是 {summary['total']}")
    if sum(summary['daily'].values()) != summary['total']:
        problems.append(f"每日任务数合计 {sum(summary['daily'].values())}，与总数 {summary['total']} 不一致")
    return version, summary, problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--expected-sha', default='')
    parser.add_argument('--wait', type=int, default=300)
    args = parser.parse_args()
    version, summary, problems = check(args.url.rstrip('/'), args.expected_sha, args.wait)
    lines = [f"测试环境 {args.url}", f"版本 {version['sha']}（{version['ref']}，构建于 {version['built_at']}）",
             f"总数 {summary['total']}，分页 {summary['pages']} 页 × {summary['page_size']}"]
    lines += [f"- 失败：{p}" for p in problems] or ['- 全部通过']
    report = '\n'.join(lines)
    print(report)
    for name, value in (('GITHUB_STEP_SUMMARY', report + '\n'),):
        if os.environ.get(name):
            open(os.environ[name], 'a').write(value)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
            out.write(f"ref={version['ref']}\nsha={version['sha']}\nreport<<EOF\n{report}\nEOF\n")
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
