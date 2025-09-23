class ChatState:
    tokens = {}
    @classmethod
    def get_query(cls, chat_id: int) -> str: return cls.tokens.get(chat_id, "Weedcoin")
    @classmethod
    def set_query(cls, chat_id: int, q: str): cls.tokens[chat_id] = q
GetQuery = ChatState.get_query
SetQuery = ChatState.set_query
