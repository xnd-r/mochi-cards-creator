import os

from mochi.client import Mochi
from mochi.auth import Auth


class MochiDeck:
    def __init__(self, args):
        self.deck_name = args.deck_name
        if args.mochi_token is None:
            mochi_token = os.getenv("MOCHI_TOKEN")
        else:
            mochi_token = args.mochi_token
        if mochi_token == "":
            raise ValueError("Mochi token not found.")
        self.mochi = Mochi(auth=Auth.Token(mochi_token))
        self.deck = self._get_deck_by_name(self.deck_name)
        if self.deck is None:
            self.deck = self.mochi.decks.create_deck(self.deck_name)
            print(f"Deck '{self.deck_name}' created with ID: {self.deck['id']}")
        self.deck_id = self.deck["id"]
        # cards = self._get_cards_by_deck_name(self.deck_id)
        # self.cards = {card["content"].split("\n\n---\n")[0][2:]: card for card in cards}  # only 10 returned


    def _get_deck_by_name(self, name: str):
        decks = self.mochi.decks.list_decks()
        for deck in decks:
            if deck["name"] == name:
                return deck
        return None

    def _get_cards_by_deck_name(self, deck_id: str):
        cards = self.mochi.cards.list_cards()
        return [card for card in cards if card["deck-id"] == deck_id]

    def add_card(self, word: str, card_data: str):
        # if word in self.cards:
        #     print(f"Card for '{word}' already exists.")
        #     return
        self.mochi.cards.create_card(card_data, self.deck_id)

    def get_words(self):
        raise NotImplementedError
        return list(self.cards.keys())
