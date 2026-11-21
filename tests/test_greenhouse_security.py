import unittest
from unittest.mock import MagicMock, patch

from services.ingestion.greenhouse import (
    GREENHOUSE_HOST,
    MAX_RESPONSE_BYTES,
    fetch_approved_greenhouse_board,
)


class GreenhouseSecurityTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.response = self.connection.getresponse.return_value
        self.response.status = 200
        self.response.read.return_value = b'{"jobs": [{"id": 1}]}'
        self.patcher = patch(
            "services.ingestion.greenhouse.http.client.HTTPSConnection",
            return_value=self.connection,
        )
        self.https = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def get_jobs(self, board="example"):
        return fetch_approved_greenhouse_board(
            board, approved_ids=frozenset({"example"})
        )

    def test_fixed_https_host_and_safe_path(self):
        self.assertEqual(self.get_jobs(), [{"id": 1}])
        self.https.assert_called_once_with(GREENHOUSE_HOST, timeout=6)
        self.connection.request.assert_called_once()
        args = self.connection.request.call_args.args
        self.assertEqual(args[:2], ("GET", "/v1/boards/example/jobs"))
        self.connection.close.assert_called_once()

    def test_unapproved_board_rejected_before_network(self):
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            self.get_jobs("other")
        self.https.assert_not_called()

    def test_injection_board_rejected_before_network(self):
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            fetch_approved_greenhouse_board(
                "../evil", approved_ids=frozenset({"../evil"})
            )
        self.https.assert_not_called()

    def test_redirect_rejected_without_second_request(self):
        self.response.status = 302
        with self.assertRaisesRegex(ValueError, "HTTP 302"):
            self.get_jobs()
        self.connection.request.assert_called_once()
        self.connection.close.assert_called_once()

    def test_oversized_response_rejected(self):
        self.response.read.return_value = b"x" * (MAX_RESPONSE_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "size limit"):
            self.get_jobs()
        self.response.read.assert_called_once_with(MAX_RESPONSE_BYTES + 1)

    def test_invalid_json_response_shape_rejected(self):
        self.response.read.return_value = b'{"jobs": "invalid"}'
        with self.assertRaisesRegex(ValueError, "shape"):
            self.get_jobs()

    def test_connection_closed_on_error(self):
        self.connection.getresponse.side_effect = TimeoutError("timeout")
        with self.assertRaises(TimeoutError):
            self.get_jobs()
        self.connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
