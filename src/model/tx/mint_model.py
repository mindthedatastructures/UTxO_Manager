class MintModel():
    def __init__(self):
        self.tokens = []
        self.policy = None

    def toFullString(self):
        res = ''
        for t in self.tokens:
            res += f"{t['token'].getString()}:{t['value']}"
        return res

    def addToken(self, token, value):
        self.tokens.append({'token':token,'value':value})

    def getCommandStringOfTokens(self):
        res = '"'
        for t in self.tokens:
            if t != self.tokens[0]:
                res += ' + '
            res += f"{t['value']} {t['token'].policy_id}.{bytes(t['token'].name, 'utf-8').hex().upper()}"
        res +='"'
        return res


