import datetime
import sqlite3
import sys
import uuid
import json

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
                resolution_season INTEGER NOT NULL,
                resolution_day INTEGER NOT NULL,
                resolution_meta json,
                state TEXT DEFAULT 'OPEN',
                bet_maker TEXT NOT NULL,
                created_at DATETIME DEFAULT current_timestamp,
                wager INTEGER NOT NULL DEFAULT 1,
                payout INTEGER NOT NULL DEFAULT 2
            )''')
            c.execute('CREATE INDEX idx_bet_resolution ON bets (resolution_season, resolution_day)')
            c.execute('CREATE INDEX idx_bet_maker ON bets (bet_maker)')
            c.execute('CREATE INDEX idx_bet_state ON bets (state)')
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


def make_bet(resolution_season,
             resolution_day,
             bet_maker,
             id_=None,
             resolution_meta=None,
             state='OPEN',
             created_at=None,
             wager=1,
             payout=2):
    id_ = id_ or str(uuid.uuid4())
    resolution_meta = resolution_meta or {}
    created_at = created_at or datetime.datetime.utcnow()
    with connect() as c:
        c.execute(
            '''
            INSERT INTO bets (
                id,
                resolution_season,
                resolution_day,
                resolution_meta,
                state,
                bet_maker,
                created_at,
                wager,
                payout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                id_,
                resolution_season,
                resolution_day,
                json.dumps(resolution_meta),
                state,
                bet_maker,
                created_at,
                wager,
                payout,
            )
        )


def get_bet(id_):
    with connect() as c:
        return c.execute('SELECT * FROM bets WHERE id=?', (id_,)).fetchone()


def update_bet_state(id_, state):
    with connect() as c:
        c.execute(
            '''
            UPDATE bets SET state = ?
            WHERE id = ?
            ''',
            (state, id_),
        )


def get_bets_to_resolve(season, day):
    with connect() as c:
        return c.execute(
            '''
            SELECT * FROM bets
            WHERE
                state = ? AND (
                    resolution_season > ? OR (
                        resolution_season = ? AND
                        resolution_day >= ?
                    )
                )
            ''',
            (
                'ACCEPTED',
                season,
                season,
                day,
            )
        ).fetchall()


if __name__ == "__main__":
    for arg in sys.argv:
        if arg == 'bootstrap':
            bootstrap()
        if arg == 'clean':
            clean()
