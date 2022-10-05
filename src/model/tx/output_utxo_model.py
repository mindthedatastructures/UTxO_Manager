from src.model.tx.token_model import TokenModel

class OutputUtxoModel():
    def from_json(utxo_json):
        res = OutputUtxoModel(utxo_json['address'],utxo_json['name'],utxo_json['value'])
        for policy_id, tokens in utxo_json['tokens'].items():
            for token_name, value in tokens.items():
                token = TokenModel(token_name, policy_id)
                res.tokens.append({'token':token,'value':value})
        return res

    def __init__(self, address='', name='', value=0):
        self.address = address
        self.name = name
        self.value = value
        self.tokens = []

    def toCommandString(self):
        res = f'{self.address}+{self.value}'
        if len(self.tokens) > 0:
            res += '+'
            res +='"'
            for t in self.tokens:
                if t != self.tokens[0]:
                    res += ' + '
                res += f"{t['value']} {t['token'].policy_id}.{bytes(t['token'].name, 'utf-8').hex().upper()}"
            res +='"'
        return res
    def addToken(self, token, value):
        self.tokens.append({'token':token,'value':value})

    def toString(self):
        return f'{self.address} - {self.name} - {self.value} - {self.tokens}'

    def toJson(self):
        res = {'address':self.address,'name':self.name,'value':self.value}
        res['tokens'] = {}
        for toks in self.tokens:
            t = toks['token']
            value = toks['value']
            if t.policy_id not in res['tokens'].keys():
                res['tokens'][t.policy_id] = {}
            res['tokens'][t.policy_id][t.name] = value
        return res
    def copy(self):
        other = OutputUtxoModel()
        other.address    = self.address
        other.name       = self.name
        other.value      = self.value
        other.tokens     = self.tokens
        return other