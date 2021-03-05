import unittest
from unittest import mock

from sibr.bet import GameStatBet, database

class TestGameStatBet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._db_patch = mock.patch('sibr.bet.database._DB', 'data/test_bet.db')
        cls._db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls._db_patch.stop()

    def setUp(self):
        database.bootstrap()

    def tearDown(self):
        database.clean()

    def test_resolve(self):
        b = GameStatBet(
            'bluh',
            12,
            49,
            'me',
            42,
            84,
            resolution_meta={
                'player_id': 'c0732e36-3731-4f1a-abdc-daa9563b6506',
                'overunder': 'over',
                'stat': 'stolen_bases',
                'line': '1',
                'type': 'GameStatBet',
            },
        )
        b.save()
        self.assertEqual(b.state, 'OPEN')

        res = b.resolve()
        self.assertEqual(res, 84)
        self.assertEqual(b.state, 'WON')

    def test_load(self):
        b = GameStatBet(
            'bluh',
            12,
            49,
            'me',
            42,
            84,
            resolution_meta={
                'player_id': 'c0732e36-3731-4f1a-abdc-daa9563b6506',
                'overunder': 'over',
                'stat': 'stolen_bases',
                'line': '1',
                'type': 'GameStatBet',
            },
        )
        b.save()

        b2 = GameStatBet.load('bluh')
        self.assertEqual(b2.resolution_meta['overunder'], 'over')
        self.assertEqual(b2.state, 'OPEN')


if __name__ == "__main__":
    unittest.main()
