import pytest

@pytest.fixture
def texts():
    return [
        ('Olá como vai ?  Tudo bem ! ', 'Olá como vai? Tudo bem!'),
        ('somente uMA fRaÇÃo', 'Somente uma fração.'),
        ('O olho da cara , VIU ISSO ?', 'O olho da cara, viu isso?'),   
        ('banana,batata e beterraba', 'Banana, batata e beterraba.'),  
        ('fez Ótimas Escolhas.,! que tal trocar a batata por feijão??', 'Fez ótimas escolhas! Que tal trocar a batata por feijão?'),
    ]