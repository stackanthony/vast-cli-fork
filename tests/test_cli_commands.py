
class TestCLICommands(unittest.TestCase):

    def test_attach_ssh_invalid_inputs(self):
        """Test attach__ssh command with invalid inputs."""
        args = MagicMock()
        args.ssh_key = None  # Missing ssh_key
        args.instance_id = "abc"  # Invalid instance_id type
        with self.assertRaises(ValueError):
            parser.parse_args(['attach__ssh', '--ssh-key', args.ssh_key, '--instance-id', args.instance_id])

    def test_attach_ssh_error_conditions(self):
        """Test attach__ssh command handling API errors."""
        args = MagicMock()
        args.ssh_key = "path/to/key"
        args.instance_id = 123
        with patch('vastai_cli.http_post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            with self.assertRaises(Exception):
                parser.parse_args(['attach__ssh', '--ssh-key', args.ssh_key, '--instance-id', args.instance_id])

    def test_create_instance_edge_cases(self):
        """Test create__instance command with edge cases."""
        args = MagicMock()
        args.onstart = ""
        args.entrypoint = "default_entrypoint"
        args.image = "test_image"
        args.env = {}
        args.price = 0  # Boundary value for price
        with patch('vastai_cli.http_put') as mock_put:
            mock_put.return_value.json.return_value = {'success': True}
            parser.parse_args(['create__instance', '--image', args.image, '--price', str(args.price)])

    def test_destroy_instance_invalid_input(self):
        """Test destroy__instance command with invalid instance id."""
        args = MagicMock()
        args.id = "not_an_integer"
        with self.assertRaises(ValueError):
            parser.parse_args(['destroy__instance', '--id', args.id])
from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
from unittest.mock import patch, MagicMock
import argparse
from vast import vast
 

class TestAttachSSH(unittest.TestCase):
    def setUp(self):
        # Setup base arguments that would come from argparse
        self.args = argparse.Namespace()
        self.args.id = 12345
        self.args.api_key = "test_key"
        self.args.raw = False
        self.args.url = "https://vast.ai/api/v0"
        self.args.ssh_key = "ssh-rsa AAAAB3NzaC1..."

    @patch('vast.http_put')
    def test_attach_ssh_success(self, mock_http_put):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_http_put.return_value = mock_response

        # Call the function
        attach__ssh(self.args)

        # Verify correct URL construction
        expected_url = f"{self.args.url}/instances/{self.args.id}/ssh"
        mock_http_put.assert_called_once()
        actual_url = mock_http_put.call_args[0][1]
        self.assertEqual(actual_url, expected_url)

        # Verify correct payload
        actual_payload = mock_http_put.call_args[1]['json']
        self.assertEqual(actual_payload['ssh_key'], self.args.ssh_key)

    @patch('vast.http_put')
    def test_attach_ssh_raw_output(self, mock_http_put):
        # Test with raw output enabled
        self.args.raw = True
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_http_put.return_value = mock_response

        with patch('builtins.print') as mock_print:
            attach__ssh(self.args)
            mock_print.assert_called_with(json.dumps({"success": True}, indent=1))

    @patch('vast.http_put')
    def test_attach_ssh_error_handling(self, mock_http_put):
        # Test API error handling
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_http_put.return_value = mock_response

        with self.assertRaises(Exception):
            attach__ssh(self.args)

    @patch('vast.http_put')
    def test_attach_ssh_missing_key(self, mock_http_put):
        # Test missing SSH key
        self.args.ssh_key = None
        
        with self.assertRaises(ValueError):
            attach__ssh(self.args)
        
        mock_http_put.assert_not_called()
 

@pytest.fixture
def base_args():
    args = argparse.Namespace()
    args.ID = "12345"
    args.image = "nvidia/cuda:11.0"
    args.env = []
    args.price = 0.4
    args.disk = 10
    args.label = "test-instance"
    args.extra = ""
    args.onstart = None
    args.onstart_cmd = None
    args.entrypoint = "/bin/bash"
    args.login = "root"
    args.python_utf8 = True
    args.lang_utf8 = True
    args.jupyter_lab = False
    args.jupyter_dir = "/workspace"
    args.force = False
    args.cancel_unavail = True
    args.template_hash = None
    args.args = None
    args.raw = False
    args.retry = 3
    args.explain = False
    return args
 

@pytest.mark.parametrize("raw_output", [True, False])
def test_create_instance_basic(base_args, raw_output, capsys):
    base_args.raw = raw_output
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "new_contract": 7835610}
    
    with patch('vast.http_put', return_value=mock_response) as mock_put:
        create__instance(base_args)
        
        # Verify API call
        mock_put.assert_called_once()
        url = mock_put.call_args[0][1]
        payload = mock_put.call_args[1]['json']
        
        # Check URL construction
        assert f"/asks/{base_args.ID}/" in url
        
        # Verify payload
        assert payload['client_id'] == "me"
        assert payload['image'] == base_args.image
        assert payload['price'] == base_args.price
        assert payload['onstart'] == base_args.entrypoint
        
        # Check output format
        captured = capsys.readouterr()
        if raw_output:
            assert json.dumps(mock_response.json(), indent=1) in captured.out
        else:
            assert "Started." in captured.out
 

def test_create_instance_with_onstart_file(base_args):
    onstart_content = "#!/bin/bash\necho hello"
    base_args.onstart = "startup.sh"
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    
    with patch('builtins.open', mock_open(read_data=onstart_content)) as mock_file:
        with patch('vast.http_put', return_value=mock_response) as mock_put:
            create__instance(base_args)
            
            mock_file.assert_called_once_with("startup.sh", "r")
            payload = mock_put.call_args[1]['json']
            assert payload['onstart'] == onstart_content
 

def test_create_instance_with_env_vars(base_args):
    base_args.env = ["KEY1=value1", "KEY2=value2"]
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    
    with patch('vast.http_put', return_value=mock_response) as mock_put:
        create__instance(base_args)
        
        payload = mock_put.call_args[1]['json']
        assert payload['env']['KEY1'] == "value1"
        assert payload['env']['KEY2'] == "value2"
 

def test_create_instance_with_template_hash(base_args):
    base_args.template_hash = "abc123"
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    
    with patch('vast.http_put', return_value=mock_response) as mock_put:
        create__instance(base_args)
        
        payload = mock_put.call_args[1]['json']
        assert payload['template_hash_id'] == "abc123"
        assert 'runtype' not in payload
 
from vast import destroy__instance

class TestDestroyInstance(unittest.TestCase):
    def setUp(self):
        self.mock_args = argparse.Namespace()
        self.mock_args.id = 12345
        self.mock_args.api_key = "test_key"
        self.mock_args.raw = False

    @patch('vast.http_del')
    def test_destroy_instance_success(self, mock_http_del):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_http_del.return_value = mock_response

        # Execute destroy command
        destroy__instance(self.mock_args)

        # Verify correct API call
        mock_http_del.assert_called_once()
        call_args = mock_http_del.call_args
        self.assertEqual(call_args[0][1].split('/')[-2], str(self.mock_args.id))

    @patch('vast.http_del')
    def test_destroy_instance_not_found(self, mock_http_del):
        # Setup mock response for 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Instance not found")
        mock_http_del.return_value = mock_response

        # Verify exception is raised
        with self.assertRaises(Exception):
            destroy__instance(self.mock_args)

    @patch('vast.http_del')
    def test_destroy_instance_server_error(self, mock_http_del):
        # Setup mock response for 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_http_del.return_value = mock_response

        # Verify exception is raised
        with self.assertRaises(Exception):
            destroy__instance(self.mock_args)

    def test_destroy_instance_invalid_id(self):
        # Test with invalid ID type
        invalid_args = argparse.Namespace()
        invalid_args.id = "not_a_number"
        invalid_args.api_key = "test_key"
        
        with self.assertRaises(TypeError):
            destroy__instance(invalid_args)

    @patch('vast.http_del')
    def test_destroy_instance_url_construction(self, mock_http_del):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.status_code = 200
        mock_http_del.return_value = mock_response

        # Execute destroy command
        destroy__instance(self.mock_args)

        # Verify URL construction
        call_args = mock_http_del.call_args
        expected_url_part = f"/instances/{self.mock_args.id}/"
        self.assertTrue(expected_url_part in call_args[0][1])
 
from vast import prepay__instance

class TestPrepayInstance(unittest.TestCase):
    def setUp(self):
        self.args = MagicMock()
        self.args.ID = 12345
        self.args.amount = 100.0
        self.args.explain = False
        self.args.api_key = "test_key"
        self.args.url = "https://vast.ai/api/v0"

    @patch('vast.http_put')
    def test_prepay_instance_success(self, mock_http_put):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "timescale": 1.5,
            "discount_rate": 0.25
        }
        mock_http_put.return_value = mock_response

        # Capture stdout
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            prepay__instance(self.args)

        # Verify API call
        expected_url = f"{self.args.url}/instances/prepay/{self.args.ID}/"
        expected_json = {"amount": self.args.amount}
        mock_http_put.assert_called_once()
        call_args = mock_http_put.call_args[0]
        self.assertEqual(call_args[1], expected_url)
        self.assertEqual(mock_http_put.call_args[1]['json'], expected_json)

        # Verify output
        expected_output = "prepaid for 1.5 months of instance 12345 applying $100.0 credits for a discount of 25.0%\n"
        self.assertEqual(captured_output.getvalue(), expected_output)

    @patch('vast.http_put')
    def test_prepay_instance_failure(self, mock_http_put):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "msg": "Insufficient funds"
        }
        mock_http_put.return_value = mock_response

        # Capture stdout
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            prepay__instance(self.args)

        # Verify error message
        self.assertEqual(captured_output.getvalue(), "Insufficient funds\n")

    @patch('vast.http_put')
    def test_prepay_instance_explain(self, mock_http_put):
        self.args.explain = True
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "timescale": 1.0, "discount_rate": 0.2}
        mock_http_put.return_value = mock_response

        # Capture stdout
        captured_output = StringIO()
        with contextlib.redirect_stdout(captured_output):
            prepay__instance(self.args)

        # Verify explain output includes request JSON
        output = captured_output.getvalue()
        self.assertIn("request json:", output)
        self.assertIn('{"amount": 100.0}', output)

    @patch('vast.http_put')
    def test_prepay_instance_http_error(self, mock_http_put):
        # Setup mock to raise HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_http_put.return_value = mock_response

        # Verify exception is raised
        with self.assertRaises(Exception) as context:
            prepay__instance(self.args)
        
        self.assertEqual(str(context.exception), "HTTP Error")
 

class TestRebootInstance(unittest.TestCase):
    def setUp(self):
        # Create args mock with required ID
        self.args = MagicMock()
        self.args.ID = 12345
        self.args.api_key = "fake_key"
        self.args.url = "https://vast.ai/api/v0"
        
        # Setup stdout capture
        self.held_output = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        sys.stdout = self.old_stdout

    @patch('vast.http_put')
    def test_reboot_instance_success(self, mock_put):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_put.return_value = mock_response

        # Call function
        reboot__instance(self.args)

        # Verify correct URL and payload
        expected_url = f"{self.args.url}/instances/reboot/{self.args.ID}/"
        mock_put.assert_called_once_with(self.args, expected_url, headers=unittest.mock.ANY, json={})

        # Verify output
        self.assertIn(f"Rebooting instance {self.args.ID}", self.held_output.getvalue())

    @patch('vast.http_put')
    def test_reboot_instance_api_error(self, mock_put):
        # Setup mock response with API error
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": False, "msg": "Instance not found"}
        mock_put.return_value = mock_response

        # Call function
        reboot__instance(self.args)

        # Verify output contains error message
        self.assertIn("Instance not found", self.held_output.getvalue())

    @patch('vast.http_put')
    def test_reboot_instance_http_error(self, mock_put):
        # Setup mock response with HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_put.return_value = mock_response

        # Call function
        reboot__instance(self.args)

        # Verify output contains error status
        self.assertIn("failed with error 404", self.held_output.getvalue())
        self.assertIn("Not Found", self.held_output.getvalue())

    @patch('vast.http_put')
    def test_reboot_instance_raises_for_status(self, mock_put):
        # Setup mock to raise HTTPError
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_put.return_value = mock_response

        # Verify exception is raised
        with self.assertRaises(Exception):
            reboot__instance(self.args)
 

class TestRecycleInstance(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace()
        self.args.api_key = "fake_key"
        self.args.raw = False
        self.args.explain = False
        self.args.ID = 12345
        self.args.url = "https://console.vast.ai/api/v0"

    @patch('vast.http_put')
    def test_recycle_instance_success(self, mock_http_put):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_http_put.return_value = mock_response

        # Capture stdout to verify output
        with patch('builtins.print') as mock_print:
            recycle__instance(self.args)

        # Verify correct URL construction and API call
        expected_url = f"{self.args.url}/instances/recycle/{self.args.ID}/"
        mock_http_put.assert_called_once()
        actual_url = mock_http_put.call_args[0][1]
        self.assertEqual(actual_url, expected_url)

        # Verify success message
        mock_print.assert_called_with(f"Recycling instance {self.args.ID}.")

    @patch('vast.http_put')
    def test_recycle_instance_failure_response(self, mock_http_put):
        # Setup mock response with error
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": False, "msg": "Error recycling instance"}
        mock_http_put.return_value = mock_response

        # Capture stdout to verify output
        with patch('builtins.print') as mock_print:
            recycle__instance(self.args)

        # Verify error message
        mock_print.assert_called_with("Error recycling instance")

    @patch('vast.http_put')
    def test_recycle_instance_http_error(self, mock_http_put):
        # Setup mock response with HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_http_put.return_value = mock_response

        # Capture stdout to verify output
        with patch('builtins.print') as mock_print:
            recycle__instance(self.args)

        # Verify error message format
        mock_print.assert_any_call("Not Found")
        mock_print.assert_called_with("failed with error 404")

    @patch('vast.http_put')
    def test_recycle_instance_explain_mode(self, mock_http_put):
        self.args.explain = True
        
        # Capture stdout to verify output
        with patch('builtins.print') as mock_print:
            recycle__instance(self.args)

        # Verify explain output
        mock_print.assert_any_call("request json: ")
        mock_print.assert_any_call({})  # Empty payload for recycle