import hashlib
from src.model.tx.utxo_model import UtxoModel
from src.model.tx.output_utxo_model import OutputUtxoModel
from src.model.tx.mint_model import MintModel

class TransactionModel():
    dummyFee = 300000

    def from_json(tx_json):
        res = TransactionModel()
        res.input_utxos = [UtxoModel.from_json(u_in['key'], u_in['vals']) for u_in in tx_json['input_utxos']]
        res.output_utxos = [OutputUtxoModel.from_json(u_out) for u_out in tx_json['output_utxos']]
        # res.metadata = tx_json['metadata']
        # res.mint = MintModel.fromJson(tx_json['mint'])
        return res

    def __init__(self):
        self.input_utxos = []
        self.output_utxos = []
        self.fee = TransactionModel.dummyFee
        self.metadata = ''
        self.mint = None
        self.generate_metadata = True
        self.generated_metadata = ''

    def getHash(self):
        m = hashlib.sha256()
        for i in self.input_utxos:
            m.update(bytes(i.hash, 'utf-8'))
        for o in self.output_utxos:
            m.update(bytes(f'{o.toCommandString()}', 'utf-8'))
        if self.metadata:
            with open(self.metadata,'r') as f:
                m.update(bytes(f.read(), 'utf-8'))
        m.update(bytes(f'{self.fee}', 'utf-8'))
        if self.mint != None:
            m.update(bytes(self.mint.toFullString(), 'utf-8'))

        return m.digest().hex()[2:15]

    def toJson(self):
        res = {}
        res['input_utxos'] = [u_in.toJson() for u_in in self.input_utxos]
        res['output_utxos'] = [u_in.toJson() for u_in in self.output_utxos]
        return res

    def updateChange(self, change_beneficiary_utxo):
        if not change_beneficiary_utxo in self.output_utxos:
            raise Exception("incorrect change_beneficiary_utxo")

        sum_inputs = sum([u.value['lovelace'] for u in self.input_utxos])
        sum_outputs = sum([u.value for u in list(filter(lambda x: x!= change_beneficiary_utxo, self.output_utxos))])

        change = sum_inputs - sum_outputs - self.fee

        change_beneficiary_utxo.value = change

    def print(self):
        print("##########")
        print("Transaction")
        print("\tInputs")
        for i in self.input_utxos:
            print(f'\t\t{i.toStringNoDatum()}')
        print("\tOutputs")
        for o in self.output_utxos:
            print(f'\t\t{o.toString()}')
        print("\tFee")
        print(f'\t\t{self.fee}')
        print("\tmetadata and mint not implemented")



