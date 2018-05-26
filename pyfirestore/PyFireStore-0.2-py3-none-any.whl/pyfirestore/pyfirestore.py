import json
import os
import uuid

from google.cloud import firestore, exceptions


class CustomExceptions:
    class AlreadyPushedException(Exception):
        pass

    class AttributeError(AttributeError):
        pass

    class Forbidden(Exception):
        pass

    class MandatoryArgument(Exception):
        pass

    class TypeError(Exception):
        pass

    class NotFound(Exception):
        pass


def get_client(json_settings_file=None):
    """
    Allows the instanciation of a Firestore client, possibly setting the credential's environment var.
    :param json_settings_file: str Path to the json credential file. If not set, will take the one from the environment
    :return: google.cloud.firestore.Client instance
    """
    if json_settings_file is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_settings_file

    return firestore.Client()


class Collection:
    document = None

    _f_collection = None

    def __init__(self, name, document: "Document" = None):
        """
        Instanciation of a collection.
        :param name: str The name of the collection
        """
        if document is not None and not isinstance(document, Document):
            raise CustomExceptions.TypeError("The document argument should be a Document instance")

        self.db = get_client()
        self.name = name
        if document is None:
            parent = self.db

        else:
            parent = document._f_document
            self.document = document

        self._f_collection = parent.collection(self.name)

    def __eq__(self, other: "Collection") -> bool:
        """
        Two collections with the same name are in fact the same colleciton
        """
        return self.name == other.name

    def get(self, id: str) -> "Document":
        """
        Returns the document with the provided id, inside this collection's data in Firestore's database
        :param id: The id of the document we are looking for
        :return: Document The document
        """
        doc_ref = self._f_collection.document(id)
        try:
            doc = doc_ref.get()
        except exceptions.NotFound:
            raise CustomExceptions.NotFound("No document with id {} was found".format(id))

        document = Document.from_dict(self, doc.to_dict())
        return document

    def get_or_create_doc(self, doc_id: str):
        try:
            doc = self.get(doc_id)
        except CustomExceptions.NotFound:
            doc = Document(collection=self, id=doc_id, is_new=True)
            doc.push()

        return doc

    def search(self, **kwargs) -> ["Collection"]:
        """
        Returns all documents with match the query inside this collection's data in Firestore's database.
        Exemple : col.search(field1="hey", field2="Joe")
        :param kwargs: list of key-values pairs of search elements
        :return: list A list of all corresponding documents
        """
        query = self._f_collection
        for key, value in kwargs.items():
            query = query.where(key, "==", value)

        ret = []
        for doc in query.get():
            the_doc = Document.from_dict(self, doc.to_dict())
            ret.append(the_doc)

        return ret

    @classmethod
    def from_json(cls, json_data: str) -> "Collection":
        """
        Creates a colleciton from its json-like string representation (which might have been produced by col.to_json()).
        :param json_data: The json representation
        :return: Collection The collection
        """
        data = json.loads(json_data)
        if 'document' in data:
            # We construct the parent document
            document = Document.from_json(data['document'])
            return cls(name=data['name'], document=document)

        return cls(name=data['name'])

    def to_json(self) -> str:
        """
        Creates a json-like string-representation of this collection. Can be fed to Colleciton.from_json().
        :return: str The json representation.
        """
        if self.document is not None:
            return json.dumps(
                dict(name=self.name, document=self.document.to_json()))

        return json.dumps(dict(name=self.name))

    def __repr__(self) -> str:
        return "Collection(name={})".format(self.name)


class Document:
    collection = None

    _f_document = None
    _is_new = True
    _constructed = False
    _changed_fields = []

    @staticmethod
    def _get_new_id() -> str:
        return str(uuid.uuid4())

    def __init__(self, collection=None, id=None, is_new=True, **kwargs) -> None:
        """
        Constructs a Document. All keyword args (besides collection and id) will be document properties. The document

        :param collection: Collection The collection this document belongs to
        :param id: str The id of the document. If not set, will be generated automatically with uuid4.
        :param kwargs: The data the document should contain
        """
        if collection is None:
            raise CustomExceptions.MandatoryArgument("A collection should be provided")

        if type(collection) is not Collection:
            raise CustomExceptions.TypeError("The collection argument should be a Collection instance")

        self.collection = collection
        self._is_new = is_new
        self._properties = []
        self._changed_fields = []

        if id is None:
            if not is_new:
                raise CustomExceptions.MandatoryArgument("Existing documents must have an id")

            self.id = self._get_new_id()
        else:
            self.id = id

        for key, value in kwargs.items():
            setattr(self, key, value)
            self._properties.append(key)

        self._f_document = self.collection._f_collection.document(self.id)

        self._constructed = True

    def __setattr__(self, key: str, value: str) -> None:
        if key == "id" and not self._is_new and self._constructed:
            raise CustomExceptions.Forbidden("The id of pushed Documents can't be modified")

        if not key.startswith('_') and key not in ["collection"]:
            if key not in self._properties:
                self._properties.append(key)

        self._changed_fields.append(key)
        super().__setattr__(key, value)

    def __eq__(self, other: "Document") -> bool:
        return self.collection == other.collection and self.id == other.id

    @classmethod
    def from_json(cls, json_data: str) -> "Document":
        """
        Creates a document from a json-encoded string
        :param json_data: str A string created with some_document.to_json()
        :return: The Document instance
        """
        data = json.loads(json_data)
        collection = Collection.from_json(data['collection'])
        return collection.get(id=data['document'])

    def to_json(self) -> str:
        """
        Exports a document to a json-encoded string
        :return: str
        """
        return json.dumps(dict(collection=self.collection.to_json(), document=self.id))

    @classmethod
    def from_dict(cls, collection: Collection, data: dict) -> "Document":
        """
        Creates a document using a dictionnary of data, and places it inside the collection
        :param collection: The Collection to which the object belongs
        :param data: dict A doctionnary of the object's data. We may use the return of some_document.to_dict()
        :return: The Document instance
        """
        data['collection'] = collection
        doc = cls(**data)
        doc._is_new = False
        doc._changed_fields = []
        return doc

    def to_dict(self) -> dict:
        """
        Exports a dictionnary of all of an object's data, except his collection
        :return: dict: The object's data
        """
        ret = dict(id=self.id)
        for prop in self._properties:
            ret[prop] = getattr(self, prop)

        return ret

    def push(self, force: bool = False) -> None:
        """
        Creates the document on Firestore's server
        :param force: bool Set this bool if you have forced the id.
        """
        if self._is_new or force:
            # pushing the document's ancestors (if any) if they haven't been pushed yet
            if self.collection.document:
                try:
                    self.collection.document.push(force=force)
                except CustomExceptions.AlreadyPushedException:
                    pass  # The doc has already been pushed

            self._f_document.set(self.to_dict())
            self._is_new = False
            self._changed_fields = []

        else:
            raise CustomExceptions.AlreadyPushedException("It seems that the document has already been pushed")

    def update(self, **kwargs) -> None:
        """
        Updates a document on Firestore's server. Creates it if it hasn't yet been created.
        :param kwargs: dict Some or all of the fields and their values
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

        if self._is_new:
            self.push()

        else:
            changes = {}
            for changed_field_key in self._changed_fields:
                changes[changed_field_key] = getattr(self, changed_field_key)

            # Making the actual change
            self._f_document.update(changes)
            # Resetting the changed fields list
            self._changed_fields = []

    def delete(self) -> None:
        """
        Deletes a document from Firestore' server, and creates a new id for this one (so we can push it again as a new
        document).
        """
        if not self._is_new:
            # We only need to delete it from the server if it exists there
            self._f_document.delete()
            self._is_new = True

        self.id = self._get_new_id()

    def __repr__(self) -> str:
        print(self.to_dict())
        parameters = ", ".join(['{}="{}"'.format(key, value) for key, value in self.to_dict().items()])
        return "{}(collection={} {})".format(self.__class__.__name__, self.collection.name, parameters)
