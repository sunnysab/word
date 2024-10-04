
import httpx



class AnkiConnect:
    def __init__(self, url_prefix: str = 'http://localhost:8765'):
        self.url_prefix = url_prefix

    @staticmethod
    def _request(action, **params):
        return {'action': action, 'params': params, 'version': 6}

    def invoke(self, action, **params):
        payload = AnkiConnect._request(action, **params)
        response = httpx.post(self.url_prefix, json=payload).json()
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
    
    def list_deck(self) -> list[str]:
        """
        列出所有deck名称
        """
        return self.invoke('deckNames')
    
    def list_deck_name_and_id(self) -> list[tuple[str, int]]:
        """
        列出所有deck名称和id
        """
        return list(self.invoke('deckNamesAndIds').items())
    
    def create_deck(self, deck_name: str) -> int:
        """
        创建一个新deck并返回deck id。
        """
        return self.invoke('createDeck', deck=deck_name)
    
    def delete_deck(self, decks: list[str], delete_cards: bool = False):
        """
        删除一个deck。
        """
        return self.invoke('deleteDeck', decks=decks, cardsToo=delete_cards)
    
    def open_deck(self, deck_name: str):
        """
        打开一个deck。
        """
        return Deck(self, deck_name)


class Deck:
    def __init__(self, anki: AnkiConnect, deck_name: str):
        self.anki = anki
        self.deck_name = deck_name

    def get_ease_factors(self, cards: list[int]) -> list[int]:
        """
        获取给定卡片的难度因子。
        """
        return self.anki.invoke('getEaseFactors', cards=cards)

    def set_ease_factors(self, cards: list[int], ease_factors: list[int]) -> list[bool]:
        """
        设置给定卡片的难度因子。
        """
        return self.anki.invoke('setEaseFactors', cards=cards, easeFactors=ease_factors)

    def set_specific_value_of_card(self, card: int, keys: list[str], new_values: list[str]) -> list[bool]:
        """
        设置单张卡片的特定值。
        """
        return self.anki.invoke('setSpecificValueOfCard', card=card, keys=keys, newValues=new_values)

    def suspend_cards(self, cards: list[int]) -> bool:
        """
        暂停卡片。
        """
        return self.anki.invoke('suspend', cards=cards)

    def unsuspend_cards(self, cards: list[int]) -> bool:
        """
        取消暂停卡片。
        """
        return self.anki.invoke('unsuspend', cards=cards)

    def is_suspended(self, card: int) -> bool:
        """
        检查卡片是否被暂停。
        """
        return self.anki.invoke('suspended', card=card)

    def are_suspended(self, cards: list[int]) -> list[bool | None]:
        """
        检查多张卡片是否被暂停。
        """
        return self.anki.invoke('areSuspended', cards=cards)

    def are_due(self, cards: list[int]) -> list[bool]:
        """
        检查卡片是否到期。
        """
        return self.anki.invoke('areDue', cards=cards)

    def get_intervals(self, cards: list[int], complete: bool = False) -> list[int] | list[list[int]]:
        """
        获取卡片的间隔。
        """
        return self.anki.invoke('getIntervals', cards=cards, complete=complete)

    def find_cards(self, query: str) -> list[int]:
        """
        根据查询找到卡片ID。
        """
        return self.anki.invoke('findCards', query=query)

    def cards_to_notes(self, cards: list[int]) -> list[int]:
        """
        将卡片ID转换为笔记ID。
        """
        return self.anki.invoke('cardsToNotes', cards=cards)

    def cards_mod_time(self, cards: list[int]) -> list[dict]:
        """
        获取卡片的修改时间。
        """
        return self.anki.invoke('cardsModTime', cards=cards)

    def cards_info(self, cards: list[int]) -> list[dict]:
        """
        获取卡片的详细信息。
        """
        return self.anki.invoke('cardsInfo', cards=cards)

    def forget_cards(self, cards: list[int]) -> None:
        """
        重置卡片为新卡片。
        """
        return self.anki.invoke('forgetCards', cards=cards)

    def relearn_cards(self, cards: list[int]) -> None:
        """
        将卡片设置为"重新学习"状态。
        """
        return self.anki.invoke('relearnCards', cards=cards)

    def answer_cards(self, answers: list[dict]) -> list[bool]:
        """
        回答卡片。
        """
        return self.anki.invoke('answerCards', answers=answers)

    def add_note(self, model_name: str, fields: dict, tags: list[str] = None, audio: list[dict] = None) -> int | None:
        """
        创建一个新笔记并返回笔记ID。如果创建失败则返回None。

        参数:
        - model_name: 笔记模型名称
        - fields: 字段内容的字典
        - tags: 标签列表

        每个媒体文件（音频、视频、图片）应该是一个字典，包含以下字段：
        - url 或 path 或 data: 文件的来源
        - filename: 文件名
        - skipHash: (可选) 用于跳过特定哈希值的文件
        - fields: 应该播放/显示该媒体的字段列表
        """
        note = {
            "deckName": self.deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or [],
            "options": {
                "allowDuplicate": True,
                "duplicateScope": "deck",
            },
        }
        if audio:
            note["audio"] = audio
        
        return self.anki.invoke('addNote', note=note)

    def add_notes(self, notes: list[dict]) -> list[int | None]:
        """
        创建多个笔记并返回笔记ID列表。
        """
        for note in notes:
            note["deckName"] = self.deck_name
        return self.anki.invoke('addNotes', notes=notes)

    def can_add_notes(self, notes: list[dict]) -> list[bool]:
        """
        检查是否可以添加笔记。
        """
        for note in notes:
            note["deckName"] = self.deck_name
        return self.anki.invoke('canAddNotes', notes=notes)

    def can_add_notes_with_error_detail(self, notes: list[dict]) -> list[dict]:
        """
        检查是否可以添加笔记，并返回详细错误信息。
        """
        for note in notes:
            note["deckName"] = self.deck_name
        return self.anki.invoke('canAddNotesWithErrorDetail', notes=notes)

    def update_note_fields(self, note_id: int, fields: dict, audio: list[dict] = None, video: list[dict] = None, picture: list[dict] = None) -> None:
        """
        更新笔记字段。
        """
        note = {
            "id": note_id,
            "fields": fields,
        }
        if audio:
            note["audio"] = audio
        if video:
            note["video"] = video
        if picture:
            note["picture"] = picture
        return self.anki.invoke('updateNoteFields', note=note)

    def update_note(self, note_id: int, fields: dict = None, tags: list[str] = None, audio: list[dict] = None, video: list[dict] = None, picture: list[dict] = None) -> None:
        """
        更新笔记字段和/或标签。
        """
        note = {"id": note_id}
        if fields:
            note["fields"] = fields
        if tags is not None:
            note["tags"] = tags
        if audio:
            note["audio"] = audio
        if video:
            note["video"] = video
        if picture:
            note["picture"] = picture
        return self.anki.invoke('updateNote', note=note)

    def update_note_tags(self, note_id: int, tags: list[str]) -> None:
        """
        更新笔记标签。
        """
        return self.anki.invoke('updateNoteTags', note=note_id, tags=tags)

    def get_note_tags(self, note_id: int) -> list[str]:
        """
        获取笔记标签。
        """
        return self.anki.invoke('getNoteTags', note=note_id)

    def add_tags(self, note_ids: list[int], tags: str) -> None:
        """
        为笔记添加标签。
        """
        return self.anki.invoke('addTags', notes=note_ids, tags=tags)

    def remove_tags(self, note_ids: list[int], tags: str) -> None:
        """
        从笔记中移除标签。
        """
        return self.anki.invoke('removeTags', notes=note_ids, tags=tags)

    def get_tags(self) -> list[str]:
        """
        获取所有标签。
        """
        return self.anki.invoke('getTags')

    def clear_unused_tags(self) -> None:
        """
        清除未使用的标签。
        """
        return self.anki.invoke('clearUnusedTags')

    def replace_tags(self, note_ids: list[int], tag_to_replace: str, replace_with_tag: str) -> None:
        """
        替换笔记中的标签。
        """
        return self.anki.invoke('replaceTags', notes=note_ids, tag_to_replace=tag_to_replace, replace_with_tag=replace_with_tag)

    def replace_tags_in_all_notes(self, tag_to_replace: str, replace_with_tag: str) -> None:
        """
        替换所有笔记中的标签。
        """
        return self.anki.invoke('replaceTagsInAllNotes', tag_to_replace=tag_to_replace, replace_with_tag=replace_with_tag)

    def find_notes(self, query: str) -> list[int]:
        """
        根据查询查找笔记ID。
        """
        return self.anki.invoke('findNotes', query=query)

    def notes_info(self, note_ids: list[int]) -> list[dict]:
        """
        获取笔记详细信息。
        """
        return self.anki.invoke('notesInfo', notes=note_ids)

    def delete_notes(self, note_ids: list[int]) -> None:
        """
        删除笔记。
        """
        return self.anki.invoke('deleteNotes', notes=note_ids)

    def remove_empty_notes(self) -> None:
        """
        移除空笔记。
        """
        return self.anki.invoke('removeEmptyNotes')