import gspread
from oauth2client.service_account import ServiceAccountCredentials

db_dict = {
    "uid":1,
    "level":2,
    "gs":3,
    "primary":4,
    "secondary":5,
    "img":6,
    "date":7,
    "name":8,
    "ign":9,
    "company":10,
    "armor":11
}

class Database():
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('keys.json',self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open('nwdb-gear').sheet1

    async def find_index(self, uid):
        """return the index of the found uid"""
        index = 1
        for cell in self.sheet.col_values(1):
            if str(cell) == str(uid):
                return index
            index += 1
        raise ValueError

    async def pull_by_uid(self, uid, field):
        """pull data from database using uid"""
        row = self.sheet.row_values(await self.find_index(uid))
        return row[db_dict[field] - 1]

    async def pull_by_index(self, index, field):
        """pull data from database using index"""
        row = self.sheet.row_values(index)
        return row[db_dict[field] - 1]

    async def push(self, uid, key, value):
        """push data to database"""
        try:
            #find cell coords
            row = await self.find_index(uid)
            col = db_dict[key]

            #push new value to cell
            self.sheet.update_cell(row,col,str(value))
            return row
        except ValueError:
            # populate new entry with data
            col = db_dict[key] - 1
            row_data = [0] * len(db_dict)
            row_data[0] = str(uid)
            row_data[col] = str(value)
            self.sheet.append_row(row_data)
            return await self.find_index(uid)