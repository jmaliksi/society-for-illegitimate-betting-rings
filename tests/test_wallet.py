import unittest
from unittest import mock

from sibr.wallet import database, Wallet, DEFAULT_STARTING_MONEY


class TestWallet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._db_patch = mock.patch('sibr.wallet.database._DB', 'data/test_wallet.db')
        cls._db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls._db_patch.stop()

    def setUp(self):
        database.bootstrap()

    def tearDown(self):
        database.clean()

    def test_new(self):
        w = Wallet.new('me')
        self.assertEqual(w.money, DEFAULT_STARTING_MONEY)

    def test_save(self):
        w = Wallet.new('me', money=9001)
        w.save()

        fetched1 = Wallet.load_by_owner('me')
        self.assertEqual(fetched1.money, w.money)

        fetched2 = Wallet.load_by_id(w.id_)
        self.assertEqual(fetched2.money, w.money)

    def test_load_missing_id(self):
        self.assertIsNone(Wallet.load_by_id('asdf'))

    def test_load_missing_owner(self):
        self.assertIsNone(Wallet.load_by_owner('asdf'))

    def test_adjust(self):
        w = Wallet.new('me')
        w.adjust(-9001)
        w.save()

        fetched = Wallet.load_by_owner('me')
        self.assertEqual(fetched.money, 420 - 9001)


if __name__ == "__main__":
    unittest.main()
