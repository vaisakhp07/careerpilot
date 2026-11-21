import unittest
from pathlib import Path
from unittest.mock import patch

from automation.controller import cli


def valid_rules():
    return [
        {'type': 'pull_request', 'parameters': {'required_review_thread_resolution': True}},
        {'type': 'required_status_checks', 'parameters': {
            'strict_required_status_checks_policy': True,
            'required_status_checks': [
                {'context': name, 'integration_id': integration_id}
                for name, (_, integration_id) in cli.EXPECTED_CHECKS.items()
            ],
        }},
    ]


class ControllerPhase1Tests(unittest.TestCase):
    def test_security_gate_required(self):
        self.assertIn(('security-gates', 'github-actions'), cli.REQUIRED)

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', side_effect=['main', ''])
    def test_doctor_valid(self, command, pages, remote):
        pages.return_value = [valid_rules()]
        result = cli.doctor(Path('/tmp'))
        self.assertTrue(result['all_required_checks_configured'])
        self.assertFalse(result['mismatched_app_bindings'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages', return_value=[[]])
    @patch.object(cli, 'command', side_effect=['main', ''])
    def test_missing_fails_closed(self, command, pages, remote):
        self.assertFalse(cli.doctor(Path('/tmp'))['all_required_checks_configured'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', side_effect=['main', ''])
    def test_wrong_integration_fails_closed(self, command, pages, remote):
        rules = valid_rules()
        rules[1]['parameters']['required_status_checks'][0]['integration_id'] = 999
        pages.return_value = [rules]
        result = cli.doctor(Path('/tmp'))
        self.assertFalse(result['all_required_checks_configured'])
        self.assertEqual(result['mismatched_app_bindings'][0]['configured_integration_ids'], [999])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', side_effect=['main', ''])
    def test_check_on_second_rules_page(self, command, pages, remote):
        rules = valid_rules()
        pages.return_value = [[rules[0]], [rules[1]]]
        self.assertTrue(cli.doctor(Path('/tmp'))['all_required_checks_configured'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', return_value='{"headRefOid":"sha-123","number":14}')
    def test_wrong_app_never_passes(self, command, pages, remote):
        pages.return_value = [{'check_runs': [
            {'name': name, 'app': {'slug': 'untrusted'}, 'head_sha': 'sha-123',
             'status': 'completed', 'conclusion': 'success'} for name, _ in cli.REQUIRED]}]
        self.assertFalse(cli.pr_snapshot(Path('/tmp'), 14)['checks_pass'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', return_value='{"headRefOid":"sha-123","number":14}')
    def test_wrong_sha_never_passes(self, command, pages, remote):
        pages.return_value = [{'check_runs': [
            {'name': name, 'app': {'slug': app}, 'head_sha': 'old',
             'status': 'completed', 'conclusion': 'success'} for name, app in cli.REQUIRED]}]
        self.assertFalse(cli.pr_snapshot(Path('/tmp'), 14)['checks_pass'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', return_value='{"headRefOid":"sha-123","number":14}')
    def test_checks_from_second_page(self, command, pages, remote):
        runs = [{'id': i+1, 'name': name, 'app': {'slug': app}, 'head_sha': 'sha-123',
                 'status': 'completed', 'conclusion': 'success'}
                for i, (name, app) in enumerate(sorted(cli.REQUIRED))]
        pages.return_value = [{'check_runs': []}, {'check_runs': runs}]
        self.assertTrue(cli.pr_snapshot(Path('/tmp'), 14)['checks_pass'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages')
    @patch.object(cli, 'command', return_value='{"headRefOid":"sha-123","number":14}')
    def test_latest_run_failure_overrides_success(self, command, pages, remote):
        runs = []
        for name, app in sorted(cli.REQUIRED):
            runs.append({'id': 1, 'name': name, 'app': {'slug': app}, 'head_sha': 'sha-123',
                         'status': 'completed', 'conclusion': 'success'})
        newer = dict(runs[0], id=2, conclusion='failure')
        pages.return_value = [{'check_runs': runs}, {'check_runs': [newer]}]
        self.assertFalse(cli.pr_snapshot(Path('/tmp'), 14)['checks_pass'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh_pages', return_value=[{'wrong': []}])
    @patch.object(cli, 'command', return_value='{"headRefOid":"sha-123","number":14}')
    def test_malformed_page_fails_closed(self, command, pages, remote):
        with self.assertRaises(TypeError):
            cli.pr_snapshot(Path('/tmp'), 14)


    def test_duplicate_correct_binding_is_accepted(self):
        rules = valid_rules()
        rules.append({
            'type': 'required_status_checks',
            'parameters': {
                'required_status_checks': [
                    {'context': 'validate', 'integration_id': 15368}
                ]
            },
        })

        missing, mismatched = cli.evaluate_bindings(rules)
        self.assertEqual(missing, [])
        self.assertEqual(mismatched, [])

        rules[-1]['parameters']['required_status_checks'][0]['integration_id'] = 999
        _, mismatched = cli.evaluate_bindings(rules)
        self.assertEqual(len(mismatched), 1)
        self.assertEqual(mismatched[0]['name'], 'validate')


if __name__ == '__main__':
    unittest.main()
