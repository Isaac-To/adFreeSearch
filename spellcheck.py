from spellchecker import SpellChecker
import asyncio


async def sentenceBreakDown(sentence):
    """
    It takes a sentence as input and returns a boolean
    value indicating whether the sentence
    is spelled correctly or not
    :param word: The word to check
    :return: A boolean value.
    """
    async def check(word):
        """
        It takes a word as input and returns a boolean value
        indicating whether the word is spelled
        correctly or not
        :param word: The word to check
        :return: A boolean value.
        """
        spell = SpellChecker()
        corrected = spell.correction(word)
        if corrected:
            return corrected
        else:
            return word
    individualWords = sentence.split(" ")
    correctedWords = [asyncio.create_task(check(word))
                      for word in individualWords
                      ]
    return ' '.join(await asyncio.gather(*correctedWords))
