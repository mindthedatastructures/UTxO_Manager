import codecs

class TokenModel():

    def encode(name):
        encoded_name = bytes(name, 'utf-8').hex().upper()
        return encoded_name
    def decode(encoded_name):
        name = codecs.decode(encoded_name,'hex_codec').decode('utf-8')
        return name


    def __init__(self, name, policy_id):
        self.name = name
        self.encoded_name = ''
        self.policy_id = policy_id
        if type(policy_id) != str:
            raise Exception("SADKj")

    def listToCommandString(tokens):
        res = '"'
        for t in tokens:
            if t != tokens[0]:
                res += ' + '
            res += f"{t.amount} {t.policy_id}.{TokenModel.encode(t.name)}"
        res +='"'
        return res

    def getString(self):
        return f'{self.policy_id}:{self.name}'


    def toDisplayableString(self):
        return f'{self.policy_id[:10]}..:{self.name}'

    def toFullString(self):
        raise Exception('TODO')
        return f'{self.policy_id}:{self.name}:{self.amount}'
