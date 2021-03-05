from abc import ABC, abstractmethod
import json
import uuid

from blaseball_mike.models import Game

from sibr import database


BET_STATE_OPEN = 'OPEN'
BET_STATE_ACCEPTED = 'ACCEPTED'
BET_STATE_WON = 'WON'
BET_STATE_LOST = 'LOST'
BET_STATE_CANCELLED = 'CANCELLED'


class Bet(ABC):
    # TODO
    def __init__(self, id_, resolution_season, resolution_day, bet_maker, wager, payout, state=BET_STATE_OPEN, resolution_meta=None):
        self.id_ = id_
        self.resolution_season = resolution_season
        self.resolution_day = resolution_day
        self.resolution_meta = resolution_meta or {}
        self.bet_maker_id = bet_maker
        self.wager = wager
        self.payout = payout
        self.state = state

    @classmethod
    def load(cls, id_):
        bet = database.get_bet(id_)
        return cls.load_sql(bet)

    @classmethod
    def load_sql(cls, sql):
        return cls(
            sql['id'],
            sql['resolution_season'],
            sql['resolution_day'],
            sql['bet_maker'],
            int(sql['wager']),
            int(sql['payout']),
            state=sql['state'],
            resolution_meta=json.loads(sql['resolution_meta']),
        )


    def save(self):
        self.validate_meta()
        database.make_bet(
            resolution_season=self.resolution_season,
            resolution_day=self.resolution_day,
            bet_maker=self.bet_maker_id,
            id_=self.id_,
            resolution_meta=self.resolution_meta,
            state=self.state,
            wager=self.wager,
            payout=self.payout,
        )

    def make_accepted_converse(self, bet_taker):
        """
        Return a copy of this bet from the bet taker
        """
        return self.__class__(
            str(uuid.uuid4()),
            self.resolution_season,
            self.resolution_day,
            bet_taker,
            self.wager,
            self.payout,
            state=BET_STATE_ACCEPTED,
            resolution_meta=self.converse_meta(self.resolution_meta),
        )

    @abstractmethod
    def converse_meta(self, meta):
        return self.resolution_meta

    def set_state(self, state):
        self.state = state
        database.update_bet_state(self.id_, state)

    @abstractmethod
    def validate_meta(self):
        return True


    @abstractmethod
    def resolve(self):
        pass


class GameStatBet(Bet):
    """
    Bet for one player's performance for a specific game.
    """

    def validate_meta(self):
        # TODO more stringent validation
        assert self.resolution_meta['player_id']
        assert self.resolution_meta['overunder'] in ('over', 'under')
        assert self.resolution_meta['stat']
        assert self.resolution_meta['line']
        assert self.resolution_meta['type'] == 'GameStatBet'

    def resolve(self):
        stats = self._find_player_statsheet()
        stat = getattr(stats, self.resolution_meta['stat'])
        if self.resolution_meta['overunder'] == 'over':
            op = '>='
        else:
            op = '<'
        win = eval(f'{stat} {op} {self.resolution_meta["line"]}')
        if win:
            self.set_state(BET_STATE_WON)
        else:
            self.set_state(BET_STATE_LOST)

        return self.payout if win else 0

    def _find_player_statsheet(self):
        games = Game.load_by_day(self.resolution_season, self.resolution_day)

        if not games:
            raise ValueError('Could not find game!')

        # crawl through the day's stat sheets to find the player
        for game in games.values():
            for team in game.statsheet.team_stats().values():
                for player in team.player_stats:
                    if player.player_id == self.resolution_meta['player_id']:
                        return player
        # may imply incineration, auto lose bet?
        raise ValueError('Could not find player statsheet')

    def converse_meta(self, meta):
        return {
            'player_id': meta['player_id'],
            'overunder': 'over' if meta['overunder'] == 'under' else 'under',
            'stat': meta['stat'],
            'line': meta['line'],
            'type': 'GameStatBet',
        }
