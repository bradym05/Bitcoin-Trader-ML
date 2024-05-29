# Dependencies
from main.private import key_file_path
from main.services import SingletonBase
from coinbase.rest import RESTClient

# Declare rest client as singleton class
class RestClientService(RESTClient, SingletonBase):
    # Initialize object
    def __init__(self, key_file:str=key_file_path):
        # Initialize from superclass
        super().__init__(key_file=key_file)