from tests import utils as test_utils, test_variables
from click.testing import CliRunner
from forgepb import utils, global_
from forgepb.cmd import node
import forgepb  # Needed for mocking builder
import os
import git
import sys
from io import StringIO
from contextlib import redirect_stdout
import unittest
from unittest.mock import MagicMock, patch, create_autospec
import json
import psutil
import shutil

class TestUtils(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        test_utils.clear_saves()

    @patch('builtins.input', lambda *args: 'v1.7.5')
    def test_get_version_info_localnet(self):
        if not os.path.exists(os.path.expanduser('~') + "/forge" + "/provenance"):
            git.Repo.clone_from(global_.PROVENANCE_REPO, os.path.expanduser('~') + "/forge" + "/provenance")
        version = utils.get_version_info('localnet', global_.CHAIN_ID_STRINGS['localnet'], os.path.expanduser('~') + "/forge" + "/provenance")
        self.assertEqual(version, 'v1.7.5')

    @patch('builtins.input', side_effect=['not existing', 'v1.7.5'])
    def test_get_version_info_localnet_not_existing_path(self, input):
        if not os.path.exists(os.path.expanduser('~') + "/forge" + "/provenance"):
            git.Repo.clone_from(global_.PROVENANCE_REPO, os.path.expanduser('~') + "/forge" + "/provenance")
        version = utils.get_version_info('localnet', global_.CHAIN_ID_STRINGS['localnet'], os.path.expanduser('~') + "/forge" + "/provenance")
        self.assertEqual(version, 'v1.7.5')

    @patch('builtins.input', lambda *args: '')
    def test_get_version_info_localnet_empty(self):
        if not os.path.exists(os.path.expanduser('~') + "/forge" + "/provenance"):
            git.Repo.clone_from(global_.PROVENANCE_REPO, os.path.expanduser('~') + "/forge" + "/provenance")
        version = utils.get_version_info('localnet', global_.CHAIN_ID_STRINGS['localnet'], os.path.expanduser('~') + "/forge" + "/provenance")
        self.assertEqual(version, utils.get_versions()[0])

    def test_get_version_info_testnet(self):
        if not os.path.exists(os.path.expanduser('~') + "/forge" + "/provenance"):
            git.Repo.clone_from(global_.PROVENANCE_REPO, os.path.expanduser('~') + "/forge" + "/provenance")
        version = utils.get_version_info('testnet', global_.CHAIN_ID_STRINGS['testnet'], os.path.expanduser('~') + "/forge" + "/provenance")
        self.assertEqual(version, 'v0.2.0')

    @patch('builtins.input', lambda *args: '1')
    @patch('forgepb.builder.build')
    def test_select_network(self, builder_mock):
        test_utils.init_config()
        utils.select_network()
        self.assertTrue(builder_mock.called)

    @patch('builtins.input', side_effect=['0', 'testnet', '4'])
    @patch('forgepb.builder.build')
    def test_select_network_retry_return(self, input, builder_mock):
        test_utils.init_config()
        utils.select_network()
        self.assertTrue(builder_mock.called)

    @patch('builtins.input', side_effect=['', ''])
    def test_collect_moniker_chain_id_default(self, input):
        config = test_utils.init_config()
        version_data = utils.collect_moniker_chain_id('v1.7.5', config)
        self.assertEqual(version_data['moniker'], 'test1')
        self.assertEqual(version_data['chainId'], 'test1')

    @patch('builtins.input', side_effect=['', ''])
    def test_collect_moniker_chain_id_default_not_existing(self, input):
        config = test_utils.init_config()
        version_data = utils.collect_moniker_chain_id('v1.7.2', config)
        self.assertEqual(version_data['moniker'], 'localnet-v1.7.2')
        self.assertEqual(version_data['chainId'], 'localnet-v1.7.2')

    @patch('builtins.input', side_effect=['test', 'test'])
    def test_collect_moniker_chain_id_custom(self, input):
        config = test_utils.init_config()
        version_data = utils.collect_moniker_chain_id('v1.7.2', config)
        self.assertEqual(version_data['moniker'], 'test')
        self.assertEqual(version_data['chainId'], 'test')

    @patch('builtins.input', side_effect=['test$', 'test', 'test%', 'test'])
    def test_collect_moniker_chain_id_custom_fail(self, input):
        config = test_utils.init_config()
        version_data = utils.collect_moniker_chain_id('v1.7.2', config)
        self.assertEqual(version_data['moniker'], 'test')
        self.assertEqual(version_data['chainId'], 'test')

    @patch('builtins.input', side_effect=[''])
    def test_collect_args_default(self, input):
        args = utils.collect_args([])
        self.assertEqual(args, ['WITH_CLEVELDB=no'])

    @patch('builtins.input', side_effect=['n'])
    def test_collect_args_no_leveldb(self, input):
        args = utils.collect_args([])
        self.assertEqual(args, ['WITH_CLEVELDB=no'])

    @patch('builtins.input', side_effect=['y'])
    def test_collect_args_yes_leveldb(self, input):
        args = utils.collect_args([])
        self.assertEqual(args, ['WITH_CLEVELDB=yes'])

    @patch('builtins.input', side_effect=['fail', 'yes'])
    def test_collect_args_retry(self, input):
        args = utils.collect_args([])
        self.assertEqual(args, ['WITH_CLEVELDB=yes'])
    
    def test_persist_localnet_information(self):
        config = test_utils.init_config()
        utils.persist_localnet_information('{}/forge/localnet/v1.7.5/logs/2021-12-22-14:51:55.204496.txt'.format(os.path.expanduser('~')), config, 'v1.7.5', test_variables.MNEMONIC_INFO)
        config = utils.load_config()
        self.assertEqual(config['localnet']['v1.7.5']['mnemonic'][0], 'tester1')
    
    def test_print_logs(self):
        if not os.path.exists(global_.CONFIG_PATH):
            os.makedirs(global_.CONFIG_PATH)
        test_file_contents = '\n        this\n        is\n        a\n        test\n        '
        utils.save_config(test_file_contents)
        output = StringIO()
        with redirect_stdout(output):
            utils.print_logs(global_.CONFIG_PATH + '/config.json')
        test_file_contents = test_file_contents.replace('\n', "\\n")
        self.assertEqual(output.getvalue(), "\"" + test_file_contents + "\"\n")

    @patch('builtins.input', side_effect=['localnet', 'v1.7.5'])
    @patch('forgepb.builder.spawnDaemon')
    def test_start_node(self, input, mock_spawn_daemon):
        test_utils.init_config()

        utils.start_node()

        self.assertTrue(mock_spawn_daemon.called)

    @patch('builtins.input', side_effect=['localnet', 'v1.7.5'])
    @patch('forgepb.builder.spawnDaemon')
    def test_start_node_no_config(self, input, mock_spawn_daemon):
        if os.path.exists(global_.CONFIG_PATH):
            shutil.rmtree(global_.CONFIG_PATH)

        utils.start_node()

        self.assertTrue(not mock_spawn_daemon.called)