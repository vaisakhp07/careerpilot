"""CareerPilot read-only GitHub repository and PR trust verification.

No model execution, PR code execution, pushing, merging or thread resolution.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

EXPECTED = 'vaisakhp07/careerpilot'
EXPECTED_CHECKS = {
    'validate': ('github-actions', 15368),
    'analyze (python)': ('github-actions', 15368),
    'analyze (javascript-typescript)': ('github-actions', 15368),
    'CodeRabbit': ('coderabbitai', 347564),
    'security-gates': ('github-actions', 15368),
}
REQUIRED = {(name, app) for name, (app, _) in EXPECTED_CHECKS.items()}


def command(args: list[str], cwd: Path, timeout: int = 40) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True,
                            timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f'{args[0]} exited {result.returncode}: {result.stderr[-800:]}')
    return result.stdout.strip()


def repo_root() -> Path:
    return Path(command(['git', 'rev-parse', '--show-toplevel'], Path.cwd())).resolve()


def gh_pages(root: Path, endpoint: str) -> list[object]:
    """Retrieve every GitHub API page via its Link pagination headers."""
    raw = command(['gh', 'api', '--paginate', '--slurp', endpoint], root, timeout=120)
    pages = json.loads(raw)
    if not isinstance(pages, list) or not pages:
        raise RuntimeError('Unexpected paginated GitHub API response')
    return pages


def verify_remote(root: Path) -> None:
    actual = command(['gh', 'repo', 'view', '--json', 'nameWithOwner', '--jq', '.nameWithOwner'], root)
    if actual.lower() != EXPECTED.lower():
        raise RuntimeError(f'Refusing unexpected repo {actual!r}; expected {EXPECTED}')


def required_rules(root: Path) -> list[dict]:
    rules = []
    for page in gh_pages(root, f'repos/{EXPECTED}/rules/branches/main?per_page=100'):
        if not isinstance(page, list):
            raise TypeError('Unexpected branch-rules page shape')
        if not all(isinstance(item, dict) for item in page):
            raise RuntimeError('Unexpected branch rule data')
        rules.extend(page)
    return rules


def evaluate_bindings(rules: list[dict]) -> tuple[list[str], list[dict]]:
    configured = {}
    for rule in rules:
        if rule.get('type') != 'required_status_checks':
            continue
        for item in (rule.get('parameters') or {}).get('required_status_checks', []):
            if not isinstance(item, dict):
                raise TypeError('Malformed required check entry')
            name = item.get('context')
            if isinstance(name, str):
                configured.setdefault(name, []).append(item.get('integration_id'))
    missing = sorted(set(EXPECTED_CHECKS) - set(configured))
    mismatched = []
    for name, (app, expected_id) in sorted(EXPECTED_CHECKS.items()):
        if name in configured and set(configured[name]) != {expected_id}:
            mismatched.append({'name': name, 'expected_app': app,
                               'expected_integration_id': expected_id,
                               'configured_integration_ids': configured[name]})
    return missing, mismatched


def doctor(root: Path) -> dict:
    verify_remote(root)
    rules = required_rules(root)
    missing, mismatched = evaluate_bindings(rules)
    required = sorted({item.get('context') for rule in rules if rule.get('type') == 'required_status_checks'
                       for item in (rule.get('parameters') or {}).get('required_status_checks', [])
                       if isinstance(item.get('context'), str)})
    strict = any(rule.get('type') == 'required_status_checks' and
                 (rule.get('parameters') or {}).get('strict_required_status_checks_policy') is True
                 for rule in rules)
    pr_resolution = any(rule.get('type') == 'pull_request' and
                        (rule.get('parameters') or {}).get('required_review_thread_resolution') is True
                        for rule in rules)
    return {
        'repo': EXPECTED, 'root': str(root),
        'branch': command(['git', 'branch', '--show-current'], root),
        'dirty': bool(command(['git', 'status', '--porcelain'], root)),
        'required_checks': required,
        'missing_required_checks': missing,
        'mismatched_app_bindings': mismatched,
        'strict_required_status_checks': strict,
        'required_review_thread_resolution': pr_resolution,
        'all_required_checks_configured': not missing and not mismatched and strict and pr_resolution,
        'safety_mode': 'read-only',
    }


def pr_snapshot(root: Path, number: int) -> dict:
    verify_remote(root)
    pr = json.loads(command(['gh', 'pr', 'view', str(number), '--json',
                             'number,headRefOid,mergeStateStatus,mergeable,state,url'], root))
    sha = pr['headRefOid']
    found = {}
    for page in gh_pages(root, f'repos/{EXPECTED}/commits/{sha}/check-runs?per_page=100'):
        if not isinstance(page, dict) or not isinstance(page.get('check_runs'), list):
            raise TypeError('Unexpected check-runs page shape')
        for run in page['check_runs']:
            key = (run.get('name'), (run.get('app') or {}).get('slug'))
            if key in REQUIRED and run.get('head_sha') == sha:
                old = found.get(key)
                if old is None or (run.get('id') or 0) > (old.get('id') or 0):
                    found[key] = run
    evaluations = []
    for name, app in sorted(REQUIRED):
        run = found.get((name, app))
        evaluations.append({
            'name': name, 'app': app,
            'status': run.get('status') if run else 'missing',
            'conclusion': run.get('conclusion') if run else None,
            'pass': bool(run and run.get('status') == 'completed' and run.get('conclusion') == 'success'),
        })
    return {'pr': pr, 'checks': evaluations, 'checks_pass': all(e['pass'] for e in evaluations),
            'note': 'Check success does not imply review threads are resolved or that the PR is mergeable.'}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('doctor')
    pr = sub.add_parser('pr-status')
    pr.add_argument('number', type=int)
    args = parser.parse_args(argv)
    try:
        root = repo_root()
        report = doctor(root) if args.action == 'doctor' else pr_snapshot(root, args.number)
        print(json.dumps(report, indent=2))
        return 0 if report.get('all_required_checks_configured', report.get('checks_pass', False)) else 2
    except (RuntimeError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'Controller stopped safely: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
