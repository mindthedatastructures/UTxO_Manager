
from src.model.tx.token_model import TokenModel

class UtxoModel():
    def from_json(key, vals):
        res = UtxoModel()
        res.hash = key
        res.address = vals['address']
        res.datum = vals['datum']
        res.datumHash = vals['datumhash']
        res.value = {}
        for policy, tokens in vals["value"].items():
            if policy == 'lovelace':
                res.value[policy] = tokens
                continue
            res.value[policy] = {}
            for tok, value in tokens.items():
                decoded = TokenModel.decode(tok)
                res.value[policy][decoded] = value
        return res

    def __init__(self):
        self.hash = ''
        self.address = ''
        self.datum = ''
        self.datumHash = ''
        self.value = ''
        self.decorators = {}


    def adaValue(self):
        return self.value['lovelace']/10.0**6

    def toString(self):
        res= f'{self.hash[:8]}..{self.hash[-8:]}'
        res += f':{self.address[:15]}'
        res += f':{self.datum}:{self.datumHash}:{self.value}'
        return res

    def toStringNoDatum(self):
        res= f'{self.hash[:8]}..{self.hash[-8:]}'
        res += f':{self.address[:15]}'
        res += f':{self.value}'
        return res

    def uiString(self):
        res = (f"{self.decorators['user'].name}:" if 'user' in self.decorators.keys() else '')+f':{self.address[:20]}..:{self.value["lovelace"]}'
        for policy, tokens in self.value.items():
            if policy == 'lovelace':
                continue
            for name, value in tokens.items():
                res += f"+ {policy} {name} {value}"
        return res


    def toJson(self):
        res = {}
        res['key'] = self.hash
        res['vals'] = {
            'address' : self.address,
            'datum' : self.datum,
            'datumhash' : self.datumHash,
            "value": {
                'lovelace': self.value['lovelace']
            }
        }
        for policy, tokens in self.value.items():
            if policy == 'lovelace':
                continue
            res['vals'][policy] = {}
            for tok, value in tokens.items():
                if type(tok) == str:
                    name = tok
                else:
                    name = tok.name
                res['vals'][policy][TokenModel.encode(name)] = value
        return res

