import gzip
import lmdb
from os import listdir
from os.path import isfile, join
import json
import pickle
import multiprocessing as mp

JSON_TAG = "JSON:"
DOCUMENT_ID = "documentId"
LMDB_ENTRIES = "entries"
CLEARLOVE_SEVEN = 7


class ENV_lmdb:
    '''
    lmdb for patent 
    '''

    def __init__(self, db_path):
        self.env = lmdb.open(db_path, map_size=1e12)

    def close(self):
        self.env.close()

    def insert(self, key, value):
        txn = self.env.begin(write=True)
        txn.put(str(key).encode(), json.dumps(value).encode())
        txn.commit()

    def delete(self, key):
        txn = self.env.begin(write=True)
        txn.delete(str(key).encode())
        txn.commit()

    def update(self, key, value):
        txn = self.env.begin(write=True)
        txn.put(str(key).encode(), json.dumps(value).encode())
        txn.commit()

    def search(self, key):
        # print('key:', key)
        txn = self.env.begin()
        value = txn.get(str(key).encode())
        if not value:
            return None
        else:
            return json.loads(value)

    def items(self):
        txn = self.env.begin()
        cur = txn.cursor()
        for key, value in cur:
            yield key, json.loads(value)

    def display(self):
        txn = self.env.begin()
        cur = txn.cursor()
        for key, value in cur:
            print(key, value)

    def display_head(self, max_size):
        txn = self.env.begin()
        cur = txn.cursor()
        for i, (key, value) in enumerate(cur):
            if i >= max_size:
                break
            print(key, value)
            print(type(key))
            print(key.decode('utf-8'))

    def display_head_keys(self, max_size):
        txn = self.env.begin()
        cur = txn.cursor()
        for i, (key, value) in enumerate(cur):
            if i >= max_size:
                break
            print(key)

    def display_count(self):
        txn = self.env.begin()
        cur = txn.cursor()
        return txn.stat()[LMDB_ENTRIES]


def _list_file(path):
    '''
    helper function, list the function under uspto/grangs
    '''
    document_files = [f for f in listdir(path) if isfile(join(path, f))]

    print("document numbers: {}".format(len(document_files)))

    print("list first 10 file names")
    print(document_files[:10])

    json_path = path + "/" + document_files[2]
    print("read first doc, as gzip, json_path {}".format(json_path))
    with gzip.GzipFile(json_path, "r") as jf:
        json_bytes = jf.read().decode("utf-8")
        json_bytes_split = json_bytes.split(JSON_TAG)
        print(len(json_bytes_split))
        print(json_bytes_split[1])
        patent = json.loads(json_bytes_split[1])
        print(patent)
        print(patent[DOCUMENT_ID])


def _build_mapping(path):
    '''
    build the mapping from the doucment id to the name of the file in parallel, and the bytes arrange for that document in the file, for seek
    '''
    document_files = [f for f in listdir(path) if isfile(join(path, f))]
    print("document numbers: {}".format(len(document_files)))


def _tell_seek(path):
    document_files = [f for f in listdir(path) if isfile(join(path, f))]

    print("document numbers: {}".format(len(document_files)))

    print("list first 10 file names")
    print(document_files[:10])

    json_tag_pos = []

    json_path = path + "/" + document_files[2]
    print("get pos")
    print("read first doc, as gzip, json_path {}".format(json_path))
    idx = 0
    with gzip.GzipFile(json_path, "r") as jf:
        idx += 1
        json_bytes_line = jf.readline().decode("utf-8")
        while json_bytes_line:
            if json_bytes_line.strip() == JSON_TAG:
                json_tag_pos.append(jf.tell())
            json_bytes_line = jf.readline().decode("utf-8")
        json_tag_pos.append(jf.tell())  # add the final bytes

    print(json_tag_pos[:5])
    print(json_tag_pos[-5:])

    print("finish read lines and get seek position, start test read from file by seek")
    with gzip.GzipFile(json_path, "r") as jf:
        jf.seek(json_tag_pos[-2])
        #  raw_data = jf.read(json_tag_pos[-1] -
        #  json_tag_pos[-2]).decode("utf-8") # last search, dont need to -7
        raw_data = jf.read(json_tag_pos[-1] -
                           json_tag_pos[-2] - 7).decode("utf-8")  # ordinary search

        json_data = json.loads(raw_data)

        print(json_data[DOCUMENT_ID])


def _create_db(uspto_path, db_path):
    '''
    build the db
    '''
    env_db = ENV_lmdb(db_path=db_path)

    document_files = [f for f in listdir(
        uspto_path) if isfile(join(uspto_path, f))]
    print("document numbers: {}".format(len(document_files)))

    for document_file_path in document_files:
        json_gz_path = uspto_path + "/" + document_file_path
        print("read first doc, as gzip, json_path {}".format(json_gz_path))
        with gzip.GzipFile(json_gz_path, "r") as jf:
            json_bytes = jf.read().decode("utf-8")
            json_bytes_splits = json_bytes.split(JSON_TAG)

            for json_bytes_split in json_bytes_splits:
                json_bytes_split_strip = json_bytes_split.strip()

                if len(json_bytes_split_strip) != 0:
                    patent = json.loads(json_bytes_split_strip)

                    env_db.insert(key=patent[DOCUMENT_ID], value=patent)


def _test_db_find(db_path):
    env_db = ENV_lmdb(db_path=db_path)
    test_id = "US329729S"

    patent = env_db.search(key=test_id)

    print("patent for {} is {}".format(test_id, patent))


def _test_db_count(db_path):
    env_db = ENV_lmdb(db_path=db_path)
    print(env_db.display_count())


def _test_db_display(db_path):
    env_db = ENV_lmdb(db_path=db_path)

    idx = 0
    for p in env_db.items():
        idx += 1
        print(p)
        if idx == 10:
            break


if __name__ == "__main__":
    #  _list_file("/pylon5/sez3a3p/javide/uspto/grants")
    #  _create_db(uspto_path="/pylon5/sez3a3p/javide/uspto/grants",
    #  db_path="/pylon5/sez3a3p/yyn1228/data/patent_lmdb")
    #  _test_db(db_path="/pylon5/sez3a3p/yyn1228/data/patent_lmdb")
    #  _test_db_display(db_path="/pylon5/sez3a3p/yyn1228/data/patent_lmdb")
    #  _test_db_count(db_path="/pylon5/sez3a3p/yyn1228/data/patent_lmdb")
    _tell_seek(path="/pylon5/sez3a3p/javide/uspto/grants")
