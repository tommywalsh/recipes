from neocitizen import NeocitiesApi
from dateutil.parser import parse
import os.path
import pathlib

# Helper file to deal with the neocities.org API


# Holds information we need about a particular file
class FileInfo:
    def __init__(self, path, modification_datetime):
        self.path = path
        self.mod_time = modification_datetime


# Holds information we need in order to decide which files to push/delete from neocities
class FileSyncInfo:
    def __init__(self, local_root, remote_root):
        self.local_root = local_root
        self.remote_root = remote_root
        self.file_index = {}

    # This function should be called once for every file on the remote side.
    def index_remote_file(self, remote_file_obj):
        index_name = remote_file_obj.path[len(self.remote_root) + 1:]
        if index_name in self.file_index:
            self.file_index[index_name]["remote"] = remote_file_obj
        else:
            self.file_index[index_name] = {
                "remote": remote_file_obj
            }

    # This function should be called once for every file in the local "dist" directory.
    def index_local_file(self, local_file_obj):
        index_name = local_file_obj.path[len(self.local_root) + 1:]
        if index_name in self.file_index:
            self.file_index[index_name]["local"] = local_file_obj
        else:
            self.file_index[index_name] = {
                "local": local_file_obj
            }

    # Returns a dict describing which local files need to be pushed, and which remote files need to be deleted.
    def get_sync_worklist(self):
        to_delete = []
        to_push = []
        for ix in self.file_index:
            entry = self.file_index[ix]
            if "local" not in entry:
                # This file does not exist locally
                to_delete.append(entry["remote"].path)
            elif "remote" not in entry:
                # This file does not exist on the remote side
                to_push.append(entry["local"].path)
            else:
                # The file exists on both sides, push only if local is newer
                if entry["local"].mod_time > entry["remote"].mod_time:
                    to_push.append(entry["local"].path)
        return {
            "delete": to_delete,
            "push": to_push
        }

    def local_path_to_remote(self, local_path):
        raw_path = local_path[len(self.local_root):]
        return self.remote_root + raw_path


# Finds and indexes all files on neocities.
def _index_remote_files(syncinfo, napi, basedir):
    for item in napi.fetch_file_list(basedir)["files"]:
        if item["is_directory"]:
            _index_remote_files(syncinfo, napi, item["path"])
        else:
            file_obj = FileInfo(item["path"], parse(item["updated_at"]).timestamp())
            syncinfo.index_remote_file(file_obj)


# Finds and indexes all files in the "dist" directory
def _index_local_files(syncinfo, basedir):
    for root, dirs, files in os.walk(basedir):
        for file in files:
            file_path = os.path.join(root, file)
            modified_time = os.path.getmtime(file_path)
            entry = FileInfo(file_path, modified_time)
            syncinfo.index_local_file(entry)


# Helper function to push a list of files to the remote neocities host.
def _push_files_to_neocities(fsi, api, files_to_push):
    # Neocities offers an API that allows for multiple uploads in one request.
    # However, this will error out when there are "too many" files, or if the
    # total size of the files is "too big".  But, it doesn't seem to define
    # how big is too big.  So, to be safe, we always upload files one-by-one.
    for local_path in files_to_push:
        remote_path = fsi.local_path_to_remote(local_path)
        print("Uploading {} as {}".format(local_path, remote_path))
        api.upload_files({pathlib.Path(local_path): remote_path})


def _get_neocities_api_key():
    with open("NEOCITIES_API_KEY") as file:
        for line in file:
            return line


# Function used in our do-it tasks to sync the remote site.
def sync_neocities(package_dir, api_key, remote_dir):
    napi = NeocitiesApi(api_key)

    # Figure out what exactly needs to be done
    fsi = FileSyncInfo(package_dir, remote_dir)
    _index_remote_files(fsi, napi, remote_dir)
    _index_local_files(fsi, package_dir)
    worklist = fsi.get_sync_worklist()

    # TODO: implement remote-side deletion

    _push_files_to_neocities(fsi, napi, worklist["push"])
