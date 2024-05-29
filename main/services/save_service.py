# Dependencies
import pickle

from main.services import SingletonBase
from typing import List, Optional

# SETTINGS
SAVE_PATH = "main\\private\\save"

# Declare save service
class SaveService(SingletonBase):
    # Initialize
    def __init__(self, version:Optional[str]="0", path:Optional[str]=SAVE_PATH) -> None:
        # Reconcile path
        if path == None:
            path = SAVE_PATH
        # Initialize data
        self._data = {}
        self._loaded = False
        self._path = f"{path}_v{version}.pkl"
        # Attempt to load
        try:
            # Get existing save
            with open(self._path, 'rb') as f:
                self._data = pickle.load(f)
                print(self._data)
                self._loaded = True
        except FileNotFoundError:
            pass
    # Main save method
    def save(self) -> None:
        open_text_mode = 'w' if self._loaded == True else 'x'
        with open(self._path, f"{open_text_mode}b") as f:
            pickle.dump(self._data, f)
            self._loaded = True
    # Get data
    def get(self, keys:List, name:str):
        if name in self._data:
            data = {}
            for key in keys:
                if key in self._data[name]:
                    data[key] = self._data[name][key]
            return data
        else:
            self._data[name] = {}
            return {}
    # Load data into the given object
    def load_into(self, keys:List, name:str, to:any):
        data = self.get(keys, name)
        for key, val in data.items():
            setattr(to, key, val)
    # Save data from the given object
    def save_from(self, keys:List, name:str, frm:any):
        if not name in self._data:
            self._data[name] = {}
        for key in keys:
            val = getattr(frm, key, None)
            if val != None:
                self._data[name][key] = val
        self.save()