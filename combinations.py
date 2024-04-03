from collections import Counter


def is_straight(cards_ranks):
    return max(cards_ranks) - min(cards_ranks) == 4 and len(set(cards_ranks)) == 5


def is_flush(suits):
    return len(set(suits)) == 1


def evaluate_hand(hand):
    # Списки рангов и мастей в руке
    ranks = [card.rank for card in hand]
    suits = [card.suit for card in hand]

    # Подсчет количества карт каждого ранга
    rank_count = Counter(ranks)

    # Определение комбинаций
    if 5 in rank_count.values():
        return "Роял-флэш" if set(ranks) == {10, 11, 12, 13, 14} else "Стрит-флэш"

    if 4 in rank_count.values():
        return "Каре"

    if set(rank_count.values()) == {2, 3}:
        return "Фул-хаус"

    if is_flush(suits):
        return "Флэш"

    if is_straight(sorted(set(ranks), reverse=True)):
        return "Стрит"

    if 3 in rank_count.values():
        return "Тройка"

    if list(rank_count.values()).count(2) == 2:
        return "Две пары"

    if 2 in rank_count.values():
        return "Пара"

    return "Ничего"
