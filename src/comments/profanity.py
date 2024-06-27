from src.comments import comment_blueprint
from wtforms import Form, Field, ValidationError

# Very basic functions used to remove profanity from comments.

# List sourced from https://github.com/whomwah/language-timothy/blob/99a5df41a2fee49b929ec996ffac051db44e3174/profanity-list.txt
BAD_WORDS_FILE = "lists/bad_words.txt"
BAD_SYMBOLS_FILE = "lists/bad_symbols.txt"

bad_words_f = comment_blueprint.open_resource(BAD_WORDS_FILE, "r")

good_but_bad_words = []
bad_words = []

line: str
for line in bad_words_f.readlines():
    if ":" in line:
        good_but_bad_words.extend(line.strip().split(":")[1].split(","))
    else:
        bad_words.append(line.strip())

bad_words_f.close()

bad_symbols: list[str]
bad_symbols_f = comment_blueprint.open_resource(BAD_SYMBOLS_FILE, "r")

bad_symbols = [symbol.strip() for symbol in bad_symbols_f.readlines()]

bad_symbols_f.close()


def profanity_validator(form: Form, field: Field) -> None:
    """Validator for checking if any form of profanity is present in comments.

    Args:
        form (Form): Not used
        field (Field): The field to be checked. Must be a `StringField` or similar.

    Raises:
        ValidationError: Risen if profanity is detected.
    """
    
    words: list[str] = field.data.split()

    for word in words:
        for bad_word in bad_words:
            if len(bad_word) > len(word):
                continue
            else:
                if not word.lower() in good_but_bad_words and bad_word in word.lower():
                    raise ValidationError("Profanity detected in comment. Please remove.")
        
        for symbol in bad_symbols:
            if symbol in word:
                raise ValidationError("Profanity detected in comment. Please remove.")
