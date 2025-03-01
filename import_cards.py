import argparse
import os

from tqdm import tqdm

from src.mochi_deck import MochiDeck
from src.babla_translator import BablaTranslator


def parse_args():
    parser = argparse.ArgumentParser(description="Import words to Mochi")
    parser.add_argument("--deck_name", type=str, default="babla", help="Name of the deck to import the words to.")
    parser.add_argument(
        "--words",
        nargs="?",
        type=str,
        help="list of words to import. Options: file path or 'word1 word2 ... wordn'",
    )
    parser.add_argument("--mochi_token", type=str, help="Mochi API token.")
    parser.add_argument("--nthreads", type=int, default=4, help="Number of threads to use for translation.")
    args = parser.parse_args()
    return args


def parse_input_words(words):
    if not isinstance(words, str):
        raise ValueError(f"Unsupported input type: {type(words)}")
    if os.path.isfile(words):
        print(f"Reading words from file: {words}")
        with open(words, "r") as f:
            words = f.read().split()
    else:
        words = words.split()
    words = [word.lower() for word in words]
    return words


def main():
    args = parse_args()
    translator = BablaTranslator(nthreads=args.nthreads)
    deck = MochiDeck(args)
    # known_words = deck.get_words()
    print("Importing translations...")
    words = parse_input_words(args.words)
    translations = translator.get_translation(words, [])
    untranslated = []
    print("Adding cards to deck...")
    for i in tqdm(range(len(translations))):
        if translations[i] is None:
            print(f"Unable to fetch translation for word: {words[i]}")
            untranslated.append(words[i])
        else:
            deck.add_card(words[i], translations[i])
    print("Import complete.")
    if untranslated:
        print("Untranslated words:")
        print("\n".join(untranslated))


if __name__ == "__main__":
    main()
