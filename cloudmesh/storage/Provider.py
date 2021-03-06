from cloudmesh.storage.provider.awss3.Provider import Provider as AwsProvider
from cloudmesh.storage.provider.azureblob.Provider import \
    Provider as AzureblobProvider
from cloudmesh.storage.provider.box.Provider import Provider as BoxProvider
from cloudmesh.storage.provider.local.Provider import Provider as LocalProvider
from cloudmesh.storage.StorageABC import StorageABC
from cloudmesh.storage.provider.gdrive.Provider import Provider as GdriveProvider

from cloudmesh.DEBUG import VERBOSE
from cloudmesh.common.console import Console
import warnings


class Provider(StorageABC):

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):

        super(Provider, self).__init__(service=service, config=config)

        Console.error("PLEASE USE cloudmesh.storage.Provider")

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        if self.kind == "local":
            self.provider = LocalProvider(service=service, config=config)
        elif self.kind == "box":
            self.provider = BoxProvider(service=service, config=config)
        elif self.kind == "gdrive":
            self.provider = GdriveProvider(service=service, config=config)
        elif self.kind == "azureblob":
            self.provider = AzureblobProvider(service=service, config=config)
        elif self.kind == "awss3":
            self.provider = AwsProvider(service=service, config=config)
        else:
            raise ValueError(f"Storage provider '{self.kind}' not yet supported")

    def get(self, service=None, source=None, destination=None, recursive=False):

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"get {source} {destination} {recursive}")
        d = self.provider.get(source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    def put(self, service=None, source=None, destination=None, recursive=False):

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"put {service} {source}")
        d = self.provider.put(source=source,
                              destination=destination,
                              recursive=recursive)
        return d

    def createdir(self, service=None, directory=None):

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"create_dir {directory}")
        VERBOSE(directory)
        d = self.provider.create_dir(service=service, directory=directory)
        return d

    def delete(self, service=None, source=None):

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        VERBOSE(f"delete filename {service} {source}")
        d = self.provider.delete(service=service, source=source)
        #raise ValueError("must return a value")
        return d

    def search(self, service=None, directory=None, filename=None, recursive=False):

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"search {directory}")
        d = self.provider.search(directory=directory,
                                 filename=filename,
                                 recursive=recursive)
        return d

    def list(self, service=None, source=None, recursive=None):

        warnings.warn("deprecated: use cloudmesh.storage.Provider instead", DeprecationWarning)

        # BUG DOES NOT FOLLOW SPEC
        VERBOSE(f"list {source}")
        VERBOSE(locals())
        d = self.provider.list(source=source,
                               recursive=recursive)
        return d

