from dataclasses import dataclass

@dataclass
class Word:
    word: str
    pos: str
    meaning: str
    category: str
    audio: str
    example: str
    extra: str

def parse_vocabulary() -> list[Word]:
    vocabulary_path = 'data/ielts/vocabulary.txt'
    with open(vocabulary_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    words = []
    for category in content.split('===\n'):
        parts = category.strip().split('+++\n')
        if len(parts) != 2:
            continue
        
        category_name = parts[0].strip()
        for word_group in parts[1].split('---\n'):
            for word_line in word_group.strip().split('\n'):
                if not word_line.strip():
                    continue
                word_parts = word_line.split('|')
                word = Word(
                    word=word_parts[0],
                    pos=word_parts[1] if len(word_parts) > 1 else '',
                    meaning=word_parts[2] if len(word_parts) > 2 else '',
                    category=category_name,
                    example=word_parts[3] if len(word_parts) > 3 else '',
                    extra=word_parts[4] if len(word_parts) > 4 else '',
                    audio=f'{category_name}_{word_parts[0]}.mp3'
                )
                words.append(word)
    
    return words

if __name__ == '__main__':
    print(parse_vocabulary())
