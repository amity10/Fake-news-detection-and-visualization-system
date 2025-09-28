from string import punctuation
import re

class CorrectText:

    """CorrectText
    Args:
        lower (bool): Transform text to lowercase before capitalize the first letters of the sentences. Default: True
        remove_spaces (bool): Transform text removing double spaces. Default: True
        add_punctuation (bool): Transform text adding dot where is no punctuation. Default: True
        captalize (bool): Transform text captalizing the first letter of each sentence. Default: True
        remove_double_pontuation (bool): Transform text removing double punctuation. Default: True
        sent_tokenizer (function): Function to utilize when capitalizing letters. Default: None
    """

    def __init__(
            self, 
            lower=True,
            remove_spaces=True,
            add_punctuation=True,
            captalize=True,
            remove_double_pontuation=True,
            sent_tokenizer=None):

        self.config = {
            "lower" : lower,
            "remove_spaces": remove_spaces,
            "add_punctuation": add_punctuation,
            "captalize": captalize,
            "remove_double_pontuation": remove_double_pontuation,
            "sent_tokenizer" : sent_tokenizer
        }
        self.end_punctuation = '!.?;'
        self.double_pontuation = '()[]{}'
                
    def remove_spaces(self, text):
        text = re.sub(' {2,}', ' ', text)
        text = re.sub(' ([{}])'.format(
            re.escape(punctuation)), r'\1', text)
        return text.strip()

    def add_punctuation(self, text):
        if list(text)[-1] not in punctuation:
            return text + '.'
        return  text

    def captalize(self, text, sent_tokenizer=None):
        if self.config['lower']:           
            text = self.lower(text)
        
        if sent_tokenizer == None:
            text = re.sub('([{}])'.format(
                re.escape(self.end_punctuation)), r'\1||', text)
            
            text_parts = list(
                filter(lambda _: len(_) > 0,
                text.split('||'))
            )
        else: 
            text_parts = sent_tokenizer(text)

        text_parts_processed = []
        for t in text_parts:
            t = re.sub(',([^ ])', r', \1', t.strip())
            
            words = t.split(' ')
            text_parts_processed.append(
                ' '.join([words[0].title()] + words[1:])
            )
        return ' '.join(text_parts_processed)    

    def remove_double_pontuation(self, text):  
        not_double = punctuation
        for d in self.double_pontuation:
            not_double = not_double.replace(d, '')

        punct = re.escape(not_double)
        pattern = '[{}]+([{}])'.format(
            punct,
            punct
        )
        if re.match(pattern, text) == False:
            return text

        return re.sub(pattern, r'\1', text)
    
    def lower(self, text):
        return text.lower()

    def transform(self, text):
        if self.config['remove_double_pontuation']:
            text = self.remove_double_pontuation(text)
        if self.config['remove_spaces']:
            text = self.remove_spaces(text)
        if self.config['add_punctuation']:           
            text = self.add_punctuation(text)
        if self.config['captalize']:
            text = self.captalize(text, self.config['sent_tokenizer'])
        return text