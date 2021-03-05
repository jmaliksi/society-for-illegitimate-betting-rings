import unittest
from unittest import mock

from sibr import bookie
from sibr import database
from sibr.bet import GameStatBet


class TestBookie(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._db_patch = mock.patch('sibr.database._DB', 'data/test_bookie.db')
        cls._db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls._db_patch.stop()

    def setUp(self):
        database.bootstrap()

    def tearDown(self):
        database.clean()

    def test_stat_bet(self):
        maker = 'maker'
        taker = 'taker'
        nagomi = 'c0732e36-3731-4f1a-abdc-daa9563b6506'

        maker_wallet = bookie.register_wallet(maker)
        self.assertEqual(maker_wallet.money, 420)
        taker_wallet = bookie.register_wallet(taker)
        self.assertEqual(taker_wallet.money, 420)

        proposal = bookie.propose_stat_bet(
            maker,
            12,
            49,
            100, 
            nagomi,
            'over',
            'stolen_bases',
            1,
        )

        maker_wallet.refresh()
        self.assertEqual(maker_wallet.money, 320)
        taker_wallet.refresh()
        self.assertEqual(taker_wallet.money, 420)

        accept = bookie.accept_bet(
            taker,
            proposal.id_,
        )

        maker_wallet.refresh()
        self.assertEqual(maker_wallet.money, 320)
        taker_wallet.refresh()
        self.assertEqual(taker_wallet.money, 320)

        proposal = GameStatBet.load(proposal.id_)
        self.assertEqual(proposal.state, 'ACCEPTED')

        bookie.resolve_bets(12, 49)
        maker_wallet.refresh()
        self.assertEqual(maker_wallet.money, 520)
        taker_wallet.refresh()
        self.assertEqual(taker_wallet.money, 320)

        proposal = GameStatBet.load(proposal.id_)
        self.assertEqual(proposal.state, 'WON')

        accept = GameStatBet.load(accept.id_)
        self.assertEqual(accept.state, 'LOST')


if __name__ == "__main__":
    unittest.main()
