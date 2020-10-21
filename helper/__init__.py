from .database import DataBase, Word

_db = DataBase()
Anc = _db.ancestors
Dec = _db.decendants
Add = _db.add
Del = _db.delete
Has = _db.has
Get = _db.get
Find = _db.find
