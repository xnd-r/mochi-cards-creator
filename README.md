# Mochi Cards Creator

Mochi Cards Creator is a tool designed for Russian-speaking users to effectively learn English vocabulary. This application leverages spaced repetition to optimize the learning process.

## Features

- **Vocabulary Import**: Import your vocabulary using [Bab.la](https://www.babla.ru/английский-русский) to [Mochi](https://mochi.cards/).
- **Customizable Decks**: Create and manage your own flashcard decks.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/xnd-r/mochi-cards-creator.git
    ```
2. Navigate to the project directory:
    ```bash
    cd mochi_cards_creator
    ```
3. Install the required dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```

## Usage

`MOCHI_TOKEN` is required to access the [Mochi API](https://mochi.cards/docs/api/). You can obtain the token in your **Account settings -> API Keys**.
Example of usage:
```bash

MOCHI_TOKEN=YOUR_MOCHI_TOKEN python3 import_cards.py --deck_name test_deck --words "hello world"
python3 import_cards.py --deck_name test_deck --mochi_token MOCHI_TOKEN --words vocab/test_vocab.txt
