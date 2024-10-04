
"""
Import IELTS cards to Anki.
"""

import json
import ielts
from anki import AnkiConnect

anki = AnkiConnect()
english_deck = anki.open_deck('英语单词')

parsed_vocabularies = ielts.parse_vocabulary()
for word in parsed_vocabularies:
    audio_name = word.__dict__['audio']
    audio_path = f'/home/sunnysab/Projects/word/data/ielts/audio/{audio_name.replace('_', '/')}'
    try:
        english_deck.add_note('问答-英语单词', fields=word.__dict__, audio=[{
            'path': audio_path,
            'filename': audio_name,
            'fields': ['audio'],
        }])
    except Exception as e:
        print(word, e)

