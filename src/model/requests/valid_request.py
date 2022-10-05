
from src.model.requests.processed_request_model import ProcessedRequestModel

class ValidRequest(ProcessedRequestModel):
    def __init__(self, utxo, beneficiary, comments, value_sent, nft_requested, contains_other_tokens):
        self.utxo = utxo
        self.beneficiary = beneficiary
        self.comments = comments
        self.value_sent = value_sent
        self.nft_requested = nft_requested
        self.contains_other_tokens = contains_other_tokens
        
    def isError(self):
        return False
