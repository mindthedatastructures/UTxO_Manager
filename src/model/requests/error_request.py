
from src.model.requests.processed_request_model import ProcessedRequestModel

class ErrorRequest(ProcessedRequestModel):
    def __init__(self, utxo, comments):
        self.utxo = utxo
        self.comments = comments
