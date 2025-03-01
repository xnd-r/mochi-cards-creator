from concurrent.futures import ThreadPoolExecutor
import platform

import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm


class BablaTranslator:
    def __init__(self, ntranslations=3, npractical_examples=2, nmonoeamples=2, nsynonyms=2, nthreads=1, ntries=5):
        self.ntranslations = ntranslations
        self.npractical_examples = npractical_examples
        self.nmonoeamples = nmonoeamples
        self.nsynonyms = nsynonyms
        self.nthreads = nthreads
        self.ntries = ntries
        self.scraper = cloudscraper.create_scraper()
        self.scraper.headers = self._get_headers_for_platform()

    def _get_headers_for_platform(self):
        """Returns appropriate headers based on the operating system."""
        platform_info = platform.system()
        if platform_info == "Windows":
            return {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            }
        elif platform_info == "Linux":
            return {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            }
        else:
            raise NotImplementedError(f"Platform '{platform_info}' is not supported.")

    @staticmethod
    def parse_translations(soup, ntranslations):
        """Parses translation data from the soup."""
        translations_section = soup.find('div', class_='quick-results container')
        if not translations_section:
            return None

        translations_md = "### Translations:\n"
        for category in translations_section.find_all('h3'):
            part_of_speech = category.text.strip()
            translations_list = category.find_next('ul')
            if translations_list:
                translations = translations_list.text.split('\n')
                translations = [t for t in translations if t][1:ntranslations + 1]
                translations_md += f"- **{part_of_speech}**: {', '.join(translations)}\n"
        return translations_md

    @staticmethod
    def parse_practical_examples(soup, npractical_examples):
        """Parses practical examples from the soup."""
        examples_section = soup.find("div", class_="content", id="practicalexamples")
        if not examples_section:
            return ""

        examples = examples_section.find_all("div", class_="dict-source")[:npractical_examples]
        examples = [example.text for example in examples]
        return "\n### Practical Examples:\n" + "\n".join(f"- {example}" for example in examples)

    @staticmethod
    def parse_monoexamples(soup, nmonoeamples):
        """Parses mono-lingual examples from the soup."""
        mono_section = soup.find("div", class_="content", id="monoexample_anchor")
        if not mono_section:
            return ""

        examples = mono_section.find_all("div", class_="mono-examples")[:nmonoeamples]
        examples = [' '.join(example.contents[-1].split("\n")[1].split()) for example in examples]
        return "\n### Mono-lingual Examples:\n" + "\n".join(f"- {example}" for example in examples)

    @staticmethod
    def parse_synonyms(soup, nsynonyms):
        """Parses synonyms from the soup."""
        synonyms_section = soup.find("div", class_="content", id="synonyms")
        if not synonyms_section:
            return ""

        synonyms = synonyms_section.find("div").find_all("div", class_="quick-result-entry")[:nsynonyms]
        synonyms_md = "\n### Synonyms:\n"
        for synonym_entry in synonyms:
            word = synonym_entry.find("div", class_="quick-result-option").text
            synonym_list = synonym_entry.find("ul").contents[:nsynonyms]
            synonyms = [syn.text for syn in synonym_list]
            synonyms_md += f"- **{word}**: {', '.join(synonyms)}\n"
        return synonyms_md

    def fetch_translation(self, word):
        url = f"https://www.babla.ru/английский-русский/{word}"
        response = None
        ntries = self.ntries
        while ntries > 0:
            response = self.scraper.get(url)
            if response.status_code == 200:
                break
            ntries -= 1
        if response is None or response.status_code != 200:
            print(f"Unable to fetch translation for word: {word}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        result_md = f"# {word}\n\n---\n\n"
        translations = self.parse_translations(soup, self.ntranslations)
        if translations is None:
            return None
        result_md += translations
        result_md += self.parse_practical_examples(soup, self.npractical_examples)
        result_md += self.parse_monoexamples(soup, self.nmonoeamples)
        result_md += self.parse_synonyms(soup, self.nsynonyms)

        return result_md

    def fetch_translations_parallel(self, words):
        results = []
        with ThreadPoolExecutor(max_workers=self.nthreads) as executor:
            for result in tqdm(executor.map(lambda word: self.fetch_translation(word), words), total=len(words)):
                results.append(result)
        return results

    def get_translation(self, words, known_words):
        words = [word for word in words if word not in known_words]
        if self.nthreads > 1:
            print(f"Fetching translations for {len(words)} words using {self.nthreads} threads.")
            translations = self.fetch_translations_parallel(words)
        else:
            translations = []
            for word in tqdm(words):
                translations.append(self.fetch_translation(word))
        return translations
