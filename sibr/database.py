import sqlite3
import sys
import uuid

_DB = 'data/tortuga.db'


def connect():
    conn = sqlite3.connect(_DB)
    conn.row_factory = sqlite3.Row
    return conn


def bootstrap():
    with connect() as c:
        try:
            c.execute('''CREATE TABLE wallets (
                id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                money INTEGER DEFAULT 0
            )''')
            c.execute('CREATE UNIQUE INDEX idx_wallet_owner ON wallets (owner)')
        except Exception:
            pass

        try:
            c.execute('''CREATE TABLE bets (
                id TEXT PRIMARY KEY,
                resolution_key TEXT NOT NULL,
                resolution_type TEXT NOT NULL,
                status TEXT,
                bet_maker TEXT NOT NULL,
                bet_taker TEXT,
                created_at TEXT NOT NULL
            )''')
            c.execute('CREATE UNIQUE INDEX idx_bet_resolution_key ON bets (resolution_key)')
            c.execute('CREATE INDEX idx_bet_maker ON bets (bet_maker)')
            c.execute('CREATE INDEX idx_bet_taker ON bets (bet_taker)')
        except Exception:
            pass


def clean():
    with connect() as c:
        try:
            c.execute('DROP TABLE wallets')
        except Exception:
            pass

        try:
            c.execute('DROP TABLE bets')
        except Exception:
            pass


def get_wallet(id_=None, owner=None):
    if id_:
        with connect() as c:
            return c.execute('SELECT * FROM wallets WHERE id=?', (id_,)).fetchone()

    if owner:
        with connect() as c:
            return c.execute('SELECT * FROM wallets WHERE owner=?', (owner,)).fetchone()

    raise ValueError('Need an ID')


def set_wallet(id_, owner, money):
    with connect() as c:
        c.execute(
            '''
            INSERT INTO wallets (id, owner, money)
            VALUES (?, ?, ?)
            ON CONFLICT (owner)
            DO UPDATE SET money = ?
            ''',
            (id_, owner, money, money)
        )


if __name__ == "__main__":
    for arg in sys.argv:
        if arg == 'bootstrap':
            bootstrap()
