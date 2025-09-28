from .correct_text import CorrectText

def test_texts(texts):
    for incorrect, correct in texts:
        print(incorrect, correct)
        assert CorrectText().transform(incorrect)==correct

def test_sent_tokenizer():
    assert 'Olá Como Vai' == CorrectText().captalize(
        'olá como vai', lambda _: _.split(' ')
    )
