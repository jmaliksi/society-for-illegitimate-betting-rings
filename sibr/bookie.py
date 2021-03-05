import uuid
from sibr.database import get_bets_to_resolve
from sibr.wallet import Wallet
from sibr.bet import (
    Bet,
    GameStatBet,
    BET_STATE_ACCEPTED,
    BET_STATE_CANCELLED,
    BET_STATE_OPEN,
)


def register_wallet(owner_id):
    w = Wallet.new(owner_id)
    w.save()
    return w


def propose_stat_bet(bet_maker, season, day, wager, player_id, overunder, stat, line):
    wallet = Wallet.load_by_owner(bet_maker)
    if not wallet:
        raise ValueError('No wallet found')

    if wallet.money < wager:
        raise ValueError('Not enough funds')

    bet = GameStatBet(
        str(uuid.uuid4()),
        season,
        day,
        bet_maker,
        wager,
        wager * 2,
        resolution_meta={
            'type': 'GameStatBet',
            'player_id': player_id,
            'overunder': overunder,
            'line': line,
            'stat': stat,
        },
    )
    bet.save()
    wallet.adjust(-wager)
    wallet.save()
    return bet


def accept_bet(bet_taker, bet_id):
    # TODO pOlYmOrPhIsM
    bet = GameStatBet.load(bet_id)
    if not bet:
        raise ValueError('Could not find bet')

    wallet = Wallet.load_by_owner(bet_taker)
    if not wallet:
        raise ValueError('No wallet found')

    if wallet.money < bet.wager:
        raise ValueError('Not enough funds')

    bet.set_state(BET_STATE_ACCEPTED)

    accepted_bet = bet.make_accepted_converse(bet_taker)
    accepted_bet.save()
    wallet.adjust(-bet.wager)
    wallet.save()
    return accepted_bet


def cancel_bet(bet_id):
    """
    This will only cancel one bet at a time /shrug
    """
    bet = Bet.load(bet_id)
    if not bet:
        raise ValueError('Could not find bet')

    if bet.state == BET_STATE_OPEN:
        raise ValueError('Bet cannot be cancelled!')

    bet.set_state(BET_STATE_CANCELLED)

    wallet = Wallet.load_by_owner(bet.bet_maker_id)
    if not wallet:
        return  #idk what happened
    wallet.adjust(bet.wager)
    wallet.save()
    return bet


def resolve_bets(season, day):
    bets = get_bets_to_resolve(season, day)
    for bet_sql in bets:
        # TODO pOlYmOrPhIsM
        bet = GameStatBet.load_sql(bet_sql)
        payout = bet.resolve()
        wallet = Wallet.load_by_owner(bet.bet_maker_id)
        if not wallet:
            continue
        wallet.adjust(payout)
        wallet.save()
