import os
import re
from pprint import pprint

from azure.storage.blob import BlockBlobService
from cloudmesh.common.console import Console
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand
from cloudmesh.storage.StorageABC import StorageABC


class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super().__init__(service=service, config=config)
        self.storage_service = BlockBlobService(
            account_name=self.credentials['account_name'],
            account_key=self.credentials['account_key'])
        self.container = self.credentials['container']
        self.cloud = service
        self.service = service

    def update_dict(self, elements, kind=None):
        # this is an internal function for building dict object
        d = []
        for element in elements:
            entry = element.__dict__
            entry["cm"] = {
                "kind": "storage",
                "cloud": self.cloud,
                "name": element.name
            }
            element.properties = element.properties.__dict__
            entry["cm"]["created"] = \
                element.properties["creation_time"].isoformat()[0]
            entry["cm"]["updated"] = \
                element.properties["last_modified"].isoformat()[0]
            entry["cm"]["size"] = element.properties["content_length"]
            del element.properties["copy"]
            del element.properties["lease"]
            del element.properties["content_settings"]
            del element.properties["creation_time"]
            del element.properties["last_modified"]
            if element.properties["deleted_time"] is not None:
                entry["cm"]["deleted"] = element.properties[
                    "deleted_time"].isoformat()
                del element.properties["deleted_time"]
            d.append(entry)
        return d

    def cloud_path(self, srv_path):
        # Internal function to determine if the cloud path specified is file or folder or mix
        b_folder = None
        b_file = None
        src_file = srv_path
        if srv_path.startswith('/'):
            src_file = srv_path[1:]
        if self.storage_service.exists(self.container, src_file):
            b_file = os.path.basename(srv_path)
            if srv_path.startswith('/'):
                b_folder = os.path.dirname(src_file)
        else:
            if srv_path.startswith('/'):
                b_folder = src_file
            else:
                b_file = os.path.basename(srv_path)
        return b_file, b_folder

    def local_path(self, source_path):
        src_path = path_expand(source_path)
        if src_path[0] not in [".", "/", "~"]:
            src_path = os.path.join(os.getcwd(), source_path)
        return src_path

    def get(self, service=None, source=None, destination=None, recursive=False):
        """
        Downloads file from Destination(Service) to Source(local)

        :param source: the source can be a directory or file
        :param destination: the destination can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        HEADING()
        # Determine service path - file or folder
        blob_file, blob_folder = self.cloud_path(destination)
        print("File  : ", blob_file)
        print("Folder: ", blob_folder)

        # Determine local path i.e. download-to-folder
        src_path = self.local_path(source)

        if not os.path.isdir(src_path):
            return Console.error(
                "Directory not found: {directory}".format(directory=src_path))
        else:
            obj_list = []
            if blob_folder is None:
                # file only specified
                if not recursive:
                    if self.storage_service.exists(self.container, blob_file):
                        download_path = os.path.join(src_path, blob_file)
                        obj_list.append(
                            self.storage_service.get_blob_to_path(self.container,
                                                          blob_file,
                                                          download_path))
                    else:
                        return Console.error(
                            "File does not exist: {file}".format(
                                file=blob_file))
                else:
                    file_found = False
                    get_gen = self.storage_service.list_blobs(self.container)
                    for blob in get_gen:
                        if os.path.basename(blob.name) == blob_file:
                            download_path = os.path.join(src_path, blob_file)
                            obj_list.append(
                                self.storage_service.get_blob_to_path(self.container,
                                                              blob.name,
                                                              download_path))
                            file_found = True
                    if not file_found:
                        return Console.error(
                            "File does not exist: {file}".format(
                                file=blob_file))
            else:
                if blob_file is None:
                    # Folder only specified
                    if not recursive:
                        file_found = False
                        get_gen = self.storage_service.list_blobs(self.container)
                        for blob in get_gen:
                            if os.path.dirname(blob.name) == blob_folder:
                                download_path = os.path.join(src_path,
                                                             os.path.basename(
                                                                 blob.name))
                                obj_list.append(self.storage_service.get_blob_to_path(
                                    self.container, blob.name, download_path))
                                file_found = True
                        if not file_found:
                            return Console.error(
                                "Directory does not exist: {directory}".format(
                                    directory=blob_folder))
                    else:
                        file_found = False
                        srch_gen = self.storage_service.list_blobs(self.container)
                        for blob in srch_gen:
                            if (os.path.dirname(blob.name) == blob_folder) or \
                                (os.path.commonpath([blob.name,
                                                     blob_folder]) == blob_folder):
                                download_path = os.path.join(src_path,
                                                             os.path.basename(
                                                                 blob.name))
                                obj_list.append(self.storage_service.get_blob_to_path(
                                    self.container, blob.name, download_path))
                                file_found = True
                        if not file_found:
                            return Console.error(
                                "Directory does not exist: {directory}".format(
                                    directory=blob_folder))
                else:
                    # SOURCE is specified with Directory and file
                    if not recursive:
                        if self.storage_service.exists(self.container, destination[1:]):
                            download_path = os.path.join(src_path, blob_file)
                            obj_list.append(
                                self.storage_service.get_blob_to_path(self.container,
                                                              destination[1:],
                                                              download_path))
                        else:
                            return Console.error(
                                "File does not exist: {file}".format(
                                    file=destination[1:]))
                    else:
                        return Console.error(
                            "Invalid arguments, recursive not applicable")
        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj

    def put(self, service=None, source=None, destination=None, recursive=False):
        """
        Uploads file from Source(local) to Destination(Service)

        :param source: the source can be a directory or file
        :param destination: the destination can be a directory or file
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        HEADING()
        # Determine service path - file or folder
        if self.storage_service.exists(self.container, destination[1:]):
            return Console.error("Directory does not exist: {directory}".format(
                directory=destination))
        else:
            blob_folder = destination[1:]
            blob_file = None

        # Determine local path i.e. upload-from-folder
        src_path = self.local_path(source)

        if os.path.isdir(src_path) or os.path.isfile(src_path):
            dict_obj = []
            if os.path.isfile(src_path):
                # File only specified
                upl_path = src_path
                if blob_folder == '':
                    upl_file = os.path.basename(src_path)
                else:
                    upl_file = blob_folder + '/' + os.path.basename(src_path)
                obj = self.storage_service.create_blob_from_path(self.container,
                                                         upl_file, upl_path)
                # Build dict object here with local file properties
                entry = obj.__dict__
                entry["cm"] = {}
                entry["cm"]["kind"] = "storage"
                entry["cm"]["cloud"] = self.cloud
                entry["cm"]["name"] = upl_file
                entry["cm"]["created"] = obj.last_modified.isoformat()
                entry["cm"]["updated"] = obj.last_modified.isoformat()
                entry["cm"]["size"] = os.stat(upl_path).st_size
                del obj.last_modified
                dict_obj.append(entry)
            else:
                # Folder only specified - Upload all files from folder
                if recursive:
                    for file in os.listdir(src_path):
                        if os.path.isfile(os.path.join(src_path, file)):
                            upl_path = os.path.join(src_path, file)
                            if blob_folder == '':
                                upl_file = file
                            else:
                                upl_file = blob_folder + '/' + file
                            obj = self.storage_service.create_blob_from_path(
                                self.container, upl_file, upl_path)
                            # Build dict object here with local file properties
                            entry = obj.__dict__
                            entry["cm"] = {}
                            entry["cm"]["kind"] = "storage"
                            entry["cm"]["cloud"] = self.cloud
                            entry["cm"]["name"] = upl_file
                            entry["cm"][
                                "created"] = obj.last_modified.isoformat()
                            entry["cm"][
                                "updated"] = obj.last_modified.isoformat()
                            entry["cm"]["size"] = os.stat(upl_path).st_size
                            del obj.last_modified
                            dict_obj.append(entry)
                else:
                    return Console.error(
                        "Source is a folder, recursive expected in arguments")
        else:
            return Console.error(
                "Directory or File does not exist: {directory}".format(
                    directory=src_path))
        pprint(dict_obj)
        return dict_obj

    def delete(self, service=None, source=None, recursive=False):
        """
        Deletes the source from cloud service

        :param source: the source can be a directory or file
        :return: None

        """
        HEADING()

        blob_file, blob_folder = self.cloud_path(source)
        print("File  : ", blob_file)
        print("Folder: ", blob_folder)

        obj_list = []
        if blob_folder is None:
            # SOURCE specified is File only
            if self.storage_service.exists(self.container, blob_file):
                blob_prop = self.storage_service.get_blob_properties(self.container,
                                                             blob_file)
                obj_list.append(blob_prop)
                self.storage_service.delete_blob(self.container, blob_file)
            else:
                return Console.error(
                    "File does not exist: {file}".format(file=blob_file))
        else:
            if blob_file is None:
                # SOURCE specified is Folder only
                del_gen = self.storage_service.list_blobs(self.container)
                file_del = False
                for blob in del_gen:
                    if os.path.commonpath([blob.name, blob_folder]) == blob_folder:
                        obj_list.append(blob)
                        self.storage_service.delete_blob(self.container, blob.name)
                        file_del = True
                if not file_del:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_folder))
            else:
                # Source specified is both file and directory
                if self.storage_service.exists(self.container, source[1:]):
                    blob_prop = self.storage_service.get_blob_properties(self.container,
                                                                 source[1:])
                    obj_list.append(blob_prop)
                    self.storage_service.delete_blob(self.container, source[1:])
                else:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_file))
        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj

    def create_dir(self, service=None, directory=None):
        """
        Creates a directory in the cloud service

        :param directory: directory is a folder
        :return: dict

        """

        HEADING()
        if self.storage_service.exists(self.container):
            blob_cre = []
            data = b' '
            blob_name = directory[1:] + '/dummy.txt'
            self.storage_service.create_blob_from_bytes(self.container, blob_name, data)
            blob_cre.append(
                self.storage_service.get_blob_to_bytes(self.container, blob_name))
            dict_obj = self.update_dict(blob_cre)
            pprint(dict_obj[0])
        return dict_obj[0]

    def search(self, service=None, directory=None, filename=None,
               recursive=False):
        """
        searches the filename in the directory

        :param directory: directory on cloud service
        :param filename: filename to be searched
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified directory
        :return: dict

        """

        HEADING()
        srch_gen = self.storage_service.list_blobs(self.container)
        obj_list = []
        if not recursive:
            srch_file = os.path.join(directory[1:], filename)
            file_found = False
            for blob in srch_gen:
                if blob.name == srch_file:
                    obj_list.append(blob)
                    file_found = True
            if not file_found:
                return Console.error(
                    "File does not exist: {file}".format(file=srch_file))
        else:
            file_found = False
            for blob in srch_gen:
                if re.search('/', blob.name) is not None:
                    if os.path.basename(blob.name) == filename:
                        if os.path.commonpath([blob.name, directory[1:]]) == directory[1:]:
                            obj_list.append(blob)
                            file_found = True
                else:
                    if blob.name == os.path.join(directory[1:], filename):
                        obj_list.append(blob)
                        file_found = True
            if not file_found:
                return Console.error(
                    "File does not exist: {file}".format(file=filename))
        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        return dict_obj

    def list(self, service=None, source=None, recursive=False):
        """
        lists all files specified in the source

        :param source: this can be a file or directory
        :param recursive: in case of directory the recursive refers to all
                          subdirectories in the specified source
        :return: dict

        """

        HEADING()

        blob_file, blob_folder = self.cloud_path(source)

        print("File  : ", blob_file)
        print("Folder: ", blob_folder)

        obj_list = []
        fold_list = []
        if blob_folder is None:
            # SOURCE specified is File only
            if not recursive:
                if self.storage_service.exists(self.container, blob_file):
                    blob_prop = self.storage_service.get_blob_properties(self.container,
                                                                 blob_file)
                    blob_size = self.storage_service.get_blob_properties(self.container,
                                                                 blob_file).properties.content_length
                    obj_list.append(blob_prop)
                else:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_file))
            else:
                file_found = False
                srch_gen = self.storage_service.list_blobs(self.container)
                for blob in srch_gen:
                    if os.path.basename(blob.name) == blob_file:
                        obj_list.append(blob)
                        file_found = True
                if not file_found:
                    return Console.error(
                        "File does not exist: {file}".format(file=blob_file))
        else:
            if blob_file is None:
                # SOURCE specified is Directory only
                if not recursive:
                    file_found = False
                    srch_gen = self.storage_service.list_blobs(self.container)
                    for blob in srch_gen:
                        if os.path.dirname(blob.name) == blob_folder:
                            obj_list.append(blob)
                            file_found = True
                        if blob_folder == '' and re.search('/', blob.name):
                            srch_fold = os.path.dirname(blob.name).split('/')[0]
                            file_found = True
                            if srch_fold not in fold_list:
                                fold_list.append(srch_fold)
                    if not file_found:
                        return Console.error(
                            "Directory does not exist: {directory}".format(
                                directory=blob_folder))
                else:
                    file_found = False
                    srch_gen = self.storage_service.list_blobs(self.container)
                    for blob in srch_gen:
                        if (os.path.dirname(blob.name) == blob_folder) or \
                            (os.path.commonpath(
                                [blob.name, blob_folder]) == blob_folder):
                            obj_list.append(blob)
                            file_found = True
                    if not file_found:
                        return Console.error(
                            "Directory does not exist: {directory}".format(
                                directory=blob_folder))
            else:
                # SOURCE is specified with Directory and file
                if not recursive:
                    if self.storage_service.exists(self.container, source[1:]):
                        blob_prop = self.storage_service.get_blob_properties(
                            self.container, source[1:])
                        blob_size = self.storage_service.get_blob_properties(
                            self.container,
                            source[1:]).properties.content_length
                        obj_list.append(blob_prop)
                    else:
                        return Console.error(
                            "File does not exist: {file}".format(
                                file=source[1:]))
                else:
                    return Console.error(
                        "Invalid arguments, recursive not applicable")
        dict_obj = self.update_dict(obj_list)
        pprint(dict_obj)
        if len(fold_list) > 0:
            pprint(fold_list)
        return dict_obj
