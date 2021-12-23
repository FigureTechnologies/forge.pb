from tests import utils as test_utils, test_variables
from click.testing import CliRunner
from forgepb import utils, global_
from forgepb.cmd import node
import forgepb  # Needed for mocking builder
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, create_autospec
import json
import psutil
import shutil

sys.path.append('.')


class TestNode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_utils.clear_saves(True)

    @classmethod
    def tearDownClass(cls):
        test_utils.clear_saves()

    @patch('forgepb.builder.spawnDaemon')
    def test_node_start(self, mock_spawn_daemon):
        if os.path.exists(global_.CONFIG_PATH):
            shutil.rmtree(os.path.expanduser('~') + '/.pio')
        if os.path.exists(os.path.expanduser('~') + '/forge'):
            shutil.rmtree(os.path.expanduser('~') + '/forge')
        mock_spawn_daemon.return_value = MagicMock()
        runner = CliRunner()
        runner.invoke(node.node_start_cmd)

        self.assertTrue(utils.exists_config())
        config = utils.load_config()
        self.assertTrue('localnet' in config)
        self.assertTrue('main' in config['localnet'])
        self.assertTrue(os.path.exists('{}/forge/localnet/main'.format(
            config['saveDir'])), 'Local folder containing binary and logs not created')

    @patch('forgepb.builder.spawnDaemon')
    def test_node_start_testnet(self, mock_spawn_daemon):
        mock_spawn_daemon.return_value = MagicMock()
        runner = CliRunner()
        runner.invoke(node.node_start_cmd, ['-n', 'testnet'])

        self.assertTrue(utils.exists_config(), 'The config file should have been created')
        config = utils.load_config()
        self.assertTrue('testnet' in config, "Config doesn't contain the correct values")
        self.assertTrue(os.path.exists('{}/forge/pio-testnet-1'.format(
            config['saveDir'])), 'Local folder containing binary and logs not created')

    @patch('forgepb.builder.spawnDaemon')
    def test_node_start_mainnet(self, mock_spawn_daemon):
        mock_spawn_daemon.return_value = MagicMock()
        runner = CliRunner()
        runner.invoke(node.node_start_cmd, ['-n', 'mainnet'])

        self.assertTrue(utils.exists_config(), 'The config file should have been created')
        config = utils.load_config()
        self.assertTrue('mainnet' in config, "Config doesn't contain the correct values")
        self.assertTrue(os.path.exists('{}/forge/pio-mainnet-1'.format(
            config['saveDir'])), 'Local folder containing binary and logs not created')

    @patch('forgepb.builder.spawnDaemon')
    def test_node_start_tag(self, mock_spawn_daemon):
        mock_spawn_daemon.return_value = MagicMock()
        runner = CliRunner()
        runner.invoke(node.node_start_cmd, ['-t', 'v1.7.1'])

        self.assertTrue(utils.exists_config(), 'The config file should have been created')
        config = utils.load_config()
        self.assertTrue('localnet' in config, "Config doesn't contain the correct values")
        self.assertTrue('v1.7.1' in config['localnet'], "Config doesn't contain the correct values")
        self.assertTrue(os.path.exists('{}/forge/localnet/v1.7.1'.format(
            config['saveDir'])), 'Local folder containing binary and logs not created')

    @patch('builtins.input', lambda *args: 'n')
    def test_node_init(self):
        runner = CliRunner()
        runner.invoke(node.node_init_cmd)

        self.assertTrue(utils.exists_config(), 'The config file should have been created')
        config = utils.load_config()
        self.assertTrue('localnet' in config, "Config doesn't contain the correct values")
        self.assertTrue('main' in config['localnet'], "Config doesn't contain the correct values")
        self.assertTrue(os.path.exists('{}/forge/localnet/main'.format(
            config['saveDir'])), 'Local folder containing binary and logs not created')

    @patch('builtins.input', lambda *args: 'n')
    def test_node_init_tag(self):
        runner = CliRunner()
        runner.invoke(node.node_init_cmd, ['-n', 'localnet', '-t', 'v1.7.3'])

        self.assertTrue(utils.exists_config(), 'The config file should have been created')
        config = utils.load_config()
        self.assertTrue('localnet' in config, "Config doesn't contain the correct values")
        self.assertTrue('v1.7.3' in config['localnet'], "Config doesn't contain the correct values")
        self.assertTrue(os.path.exists('{}/forge/localnet/v1.7.3'.format(
            config['saveDir'])), 'Local folder containing binary and logs not created')

    @patch('psutil.Process')
    def test_node_status_running(self, mock_process):
        config = test_variables.CONFIG.format(os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser(
            '~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')))
        config = json.loads(config)
        config['running-node-info'] = test_variables.RUNNING_NODE_CONFIG
        config['running-node'] = True
        utils.save_config(config)
        runner = CliRunner()
        result = runner.invoke(node.node_status_cmd)
        success = 'localnet' in result.output and 'main' in result.output
        self.assertTrue(success, "missing expected keys that should be printed")

    @patch('psutil.Process')
    def test_node_status_unexpected_stop(self, mock_process):
        mock_process.return_value = create_autospec(
            psutil.Process.is_running, return_value=False)
        mock_process.return_value.is_running = MagicMock(return_value=False)

        config = test_variables.CONFIG.format(os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser(
            '~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')))
        config = json.loads(config)
        config['running-node-info'] = test_variables.RUNNING_NODE_CONFIG
        config['running-node-info'] = test_variables.RUNNING_NODE_CONFIG
        config['running-node'] = True
        utils.save_config(config)
        runner = CliRunner()
        result = runner.invoke(node.node_status_cmd)
        self.assertEqual(result.output, 'cannot locate process\n')

    def test_node_status_not_running(self):
        config = test_variables.CONFIG.format(os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser(
            '~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')))
        config = json.loads(config)
        config['running-node-info'] = {}
        config['running-node'] = False
        utils.save_config(config)
        runner = CliRunner()
        result = runner.invoke(node.node_status_cmd)
        self.assertEqual(result.output, 'Could not find a running node\n')

    def test_node_status_no_running_info(self):
        config = test_variables.CONFIG.format(os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser(
            '~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')), os.path.join(os.path.expanduser('~')))
        config = json.loads(config)
        config['running-node-info'] = test_variables.RUNNING_NODE_CONFIG
        config.pop('running-node-info')
        config['running-node'] = False
        utils.save_config(config)
        runner = CliRunner()
        result = runner.invoke(node.node_status_cmd)
        self.assertEqual(result.output, 'node not started\n')

    def test_node_status_no_forge_config(self):
        os.remove(global_.CONFIG_PATH + '/config.json')
        runner = CliRunner()
        result = runner.invoke(node.node_status_cmd)
        self.assertEqual(result.output, 'no forge config\n')

    def test_node_stop_not_running(self):
        runner = CliRunner()
        result = runner.invoke(node.node_stop_cmd)
        self.assertEqual(result.output, 'There is not a node running currently.\n')

    @patch('psutil.Process')
    def test_node_stop_success(self, mock_process):
        runner = CliRunner()
        result = runner.invoke(node.node_stop_cmd)
        self.assertTrue(not result.output, 'There is not a node running currently.\n')

    def test_list_mnemonic(self):
        test_utils.init_config()
        runner = CliRunner()
        result = runner.invoke(node.node_list_mnemonic_cmd)
        self.assertEqual(result.output, 'Localnet version: v1.7.5\nMnemonic: testy1 testy2 testy3 testy4 testy5 testy6 testy7 testy8 testy9 testy10 testy11 testy12 testy13 testy14 testy15 testy16 testy17 testy18 testy19 testy20 testy21 testy22 testy23 testy24\nLocalnet version: main\nMnemonic: test1 test2 test3 test4 test5 test6 test7 test8 test9 test10 test11 test12 test13 test14 test15 test16 test17 test18 test19 test20 test21 test22 test23 test24\n')

    def test_list_mnemonic_tag(self):
        test_utils.init_config()
        runner = CliRunner()
        result = runner.invoke(node.node_list_mnemonic_cmd, ['-t', 'v1.7.5'])
        self.assertEqual(result.output, 'testy1 testy2 testy3 testy4 testy5 testy6 testy7 testy8 testy9 testy10 testy11 testy12 testy13 testy14 testy15 testy16 testy17 testy18 testy19 testy20 testy21 testy22 testy23 testy24\n')

    def test_list_mnemonic_tag_not_exist(self):
        test_utils.init_config()
        runner = CliRunner()
        result = runner.invoke(node.node_list_mnemonic_cmd, [
                               '-t', 'non-existant-tag'])
        self.assertEqual(result.output, "The tag entered doesn't exist in provenance. Please run 'forge provenance tags' to list all tags\n")

    def test_list_mnemonic_branch(self):
        test_utils.init_config()
        runner = CliRunner()
        result = runner.invoke(node.node_list_mnemonic_cmd, ['-b', 'main'])
        self.assertEqual(result.output, 'test1 test2 test3 test4 test5 test6 test7 test8 test9 test10 test11 test12 test13 test14 test15 test16 test17 test18 test19 test20 test21 test22 test23 test24\n')

    def test_list_mnemonic_branch_not_existing(self):
        test_utils.init_config()
        runner = CliRunner()
        result = runner.invoke(node.node_list_mnemonic_cmd, [
                               '-b', 'non-existant-branch'])
        self.assertEqual(result.output, "The branch entered doesn't exist in provenance. Please run 'forge provenance branches' to list all branches\n")

    def test_list_mnemonic_branch_not_initialized(self):
        test_utils.init_config()
        runner = CliRunner()
        result = runner.invoke(node.node_list_mnemonic_cmd, ['-t', 'v1.7.2'])
        self.assertEqual(result.output, 'No nodes found.\n')


if __name__ == '__main__':
    unittest.main()
