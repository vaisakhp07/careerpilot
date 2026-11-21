import unittest
from unittest.mock import patch
from pathlib import Path
from automation.controller import cli


class ControllerPhase1Tests(unittest.TestCase):
    def test_required_checks_include_security_gate(self):
        self.assertIn(('security-gates', 'github-actions'), cli.REQUIRED)

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh')
    @patch.object(cli, 'command')
    def test_doctor_enforces_checks(self, command, gh, remote):
        command.side_effect = ['main', '']
        gh.return_value = [{'type': 'required_status_checks', 'parameters': {
            'required_status_checks': [{'context': name} for name, _ in cli.REQUIRED]}}]
        result = cli.doctor(Path('/tmp'))
        self.assertTrue(result['all_required_checks_configured'])
        self.assertEqual(result['safety_mode'], 'read-only')

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh')
    @patch.object(cli, 'command')
    def test_missing_check_fails_closed(self, command, gh, remote):
        command.side_effect = ['main', '']
        gh.return_value = []
        self.assertFalse(cli.doctor(Path('/tmp'))['all_required_checks_configured'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh')
    @patch.object(cli, 'command')
    def test_wrong_app_never_passes(self, command, gh, remote):
        command.return_value = '{"headRefOid":"sha-123","number":2}'
        gh.return_value = {'check_runs': [
            {'name': name, 'app': {'slug': 'untrusted-app'}, 'head_sha': 'sha-123',
             'status': 'completed', 'conclusion': 'success'} for name, _ in cli.REQUIRED]}
        self.assertFalse(cli.pr_snapshot(Path('/tmp'), 2)['checks_pass'])

    @patch.object(cli, 'verify_remote')
    @patch.object(cli, 'gh')
    @patch.object(cli, 'command')
    def test_wrong_sha_never_passes(self, command, gh, remote):
        command.return_value = '{"headRefOid":"sha-123","number":2}'
        gh.return_value = {'check_runs': [
            {'name': name, 'app': {'slug': app}, 'head_sha': 'old-sha',
             'status': 'completed', 'conclusion': 'success'} for name, app in cli.REQUIRED]}
        self.assertFalse(cli.pr_snapshot(Path('/tmp'), 2)['checks_pass'])

if __name__ == '__main__':
    unittest.main()
