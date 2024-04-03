import random


class Player:
    def __init__(self, player_data):
        self.name = player_data.get("n", "")
        self.chips = player_data.get("c", 0) / 100
        self.hand = []

    def add_chips(self, amount):
        self.chips += amount

    def bet(self, amount):
        if self.chips >= amount:
            self.chips -= amount
            return amount
        else:
            print(f"{self.name}, you don't have enough chips. All-in!")
            all_in = self.chips
            self.chips = 0
            return all_in

    def show_hand(self):
        return [str(card) for card in self.hand]

    # def __del__(self):
    #     print('Inside destructor')

    def __str__(self):
        return f"Player {self.name}, Chips: {self.chips}"


class Card:
    suit_lst = ["c", "d", "h", "s"]  # _eV7He
    rank_lst = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]  # _Efhec
    BACK = "back"  # _mpVLV
    JOKER = "joker"

    card_descriptions = {
        "c": "крестья", "d": "бубны", "h": "червы", "s": "пики",
        "T": "10", "J": "Валет", "Q": "Дама", "K": "Король", "A": "Туз"
    }

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    @classmethod
    def get_card_by_code(cls, b):
        u = int(b)
        result = cls.BACK if u == -1 else cls.JOKER if u == 52 else cls.suit_lst[u % 4] + cls.rank_lst[u // 4]
        card_suit, card_rank = result[:-1], result[-1]
        description = f'{cls.card_descriptions.get(card_rank, card_rank)} {cls.card_descriptions[card_suit]}'
        return description

    def __str__(self):
        return f'{self.card_descriptions.get(self.rank, self.rank)} {self.card_descriptions[self.suit]}'


class Deck:
    def __init__(self):
        self.cards = []

    def initialize_deck(self):
        self.cards = [Card(suit, rank) for suit in Card.suit_lst for rank in Card.rank_lst]

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def deal_cards(self, num_players, num_cards):
        hands = [[] for _ in range(num_players)]
        for i in range(num_players * num_cards):
            hands[i % num_players].append(self.cards.pop())
        return hands


class Table:
    def __init__(self, deck):
        self.deck = deck
        self.community_cards = []
        self.pot = 0

    def add_to_pot(self, amount):
        self.pot += amount

    def reset_table(self):
        self.community_cards = []
        self.pot = 0

    def deal_to_players(self, players, num_cards=2):
        for player in players:
            player.hand.extend(self.deck.deal_cards(1, num_cards)[0])

    def deal_community_cards(self, num_cards):
        self.community_cards.extend(self.deck.deal_cards(1, num_cards)[0])

    def betting_round(self, players):
        for player in players:
            print(f"{player.name}, your turn. Current pot: {self.pot}")
            rate = int(input("Enter your bet: "))
            bet_amount = player.bet(rate)
            self.add_to_pot(bet_amount)

    def start_round(self, players):
        self.reset_table()
        self.deck = Deck()
        self.deck.initialize_deck()
        self.deck.shuffle_deck()

        self.deal_to_players(players)
        self.betting_round(players)

        self.deal_community_cards(3)  # Flop
        self.betting_round(players)

        self.deal_community_cards(1)  # Turn
        self.betting_round(players)

        self.deal_community_cards(1)  # River
        self.betting_round(players)

        self.end_round(players)

    def end_round(self, players):
        print("Community cards:", [str(card) for card in self.community_cards])
        for player in players:
            print(f"{player.name}'s hand:", player.show_hand())
