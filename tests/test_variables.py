RUNNING_NODE_CONFIG = {
        "pid": 58701,
        "version": "main",
        "network": "localnet"
    }
LOG_PATH = "{}/forge/localnet/main/logs/2021-12-22-10:21:00.884707.txt"
MNEMONIC_INFO = """
name: validator
  type: local
  address: pb14rclwq9xych9t0vqzdf7flw2dmhmqv3sxjjru8
  pubkey: '{"@type":"/cosmos.crypto.secp256k1.PubKey","key":"AgElKM8a4Tw6JNJkx7t2+HZ8p3OTtIpJ+/NE18sSH6vc"}'
  mnemonic: ""


**Important** write this mnemonic phrase in a safe place.
It is the only way to recover your account if you ever forget your password.

tester1 tester2 tester3 tester4 tester5 tester6 tester7 tester8 tester9 tester10 tester11 tester12 tester13 tester14 tester15 tester16 tester17 tester18 tester19 tester20 tester21 tester22 tester23 tester24
"""
CONFIG = """
{{
    "saveDir": "{}/",
    "running-node": true,
    "localnet": {{
        "v1.7.5": {{
            "moniker": "test1",
            "chainId": "test1",
            "mnemonic": [
                "testy1",
                "testy2",
                "testy3",
                "testy4",
                "testy5",
                "testy6",
                "testy7",
                "testy8",
                "testy9",
                "testy10",
                "testy11",
                "testy12",
                "testy13",
                "testy14",
                "testy15",
                "testy16",
                "testy17",
                "testy18",
                "testy19",
                "testy20",
                "testy21",
                "testy22",
                "testy23",
                "testy24"
            ],
            "validator-information": [
                {{
                    "name": "validator",
                    "type": "local",
                    "address": "pb1zamg2vejk48z8pma0thgxy50dhy3nr30el8pck",
                    "pubkey": {{
                        "@type": "/cosmos.crypto.secp256k1.PubKey",
                        "key": "AuFzQYjwynoayJksWfilPjS0D0/ehoMSdwkX3AFucIPG"
                    }},
                    "mnemonic": ""
                }}
            ],
            "run-command": [
                "{}/forge/localnet/v1.7.5/bin/provenanced",
                "start",
                "--home",
                "{}/forge/localnet/v1.7.5"
            ],
            "log-path": "{}/forge/localnet/v1.7.5/logs/2021-12-22-14:51:55.204496.txt"
        }},
        "main": {{
            "moniker": "localnet-main",
            "chainId": "localnet-main",
            "mnemonic": [
                "test1",
                "test2",
                "test3",
                "test4",
                "test5",
                "test6",
                "test7",
                "test8",
                "test9",
                "test10",
                "test11",
                "test12",
                "test13",
                "test14",
                "test15",
                "test16",
                "test17",
                "test18",
                "test19",
                "test20",
                "test21",
                "test22",
                "test23",
                "test24"
            ],
            "validator-information": [
                {{
                    "name": "validator",
                    "type": "local",
                    "address": "pb1555t6m6f7653jd8ht2mz6q5kfe0u2lf8xd9yrm",
                    "pubkey": {{
                        "@type": "/cosmos.crypto.secp256k1.PubKey",
                        "key": "AllqA0+Q/WI2N1yuy4LGBHgMLIEQDyL7cbOsdBbVIpr+"
                    }},
                    "mnemonic": ""
                }}
            ],
            "run-command": [
                "{}/forge/localnet/main/bin/provenanced",
                "start",
                "--home",
                "{}/forge/localnet/main"
            ],
            "log-path": "{}/forge/localnet/main/logs/2021-12-22-10:21:00.884707.txt"
        }}
    }},
    "running-node-info": {{
        "pid": 58701,
        "version": "main",
        "network": "localnet"
    }}
}}"""