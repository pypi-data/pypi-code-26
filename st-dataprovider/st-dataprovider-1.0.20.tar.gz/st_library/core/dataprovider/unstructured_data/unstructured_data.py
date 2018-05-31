from st_library.core.dataprovider.unstructured_data.item import Item


class UnstructuredData(object):
    """
    A Category for work with unstructured data

    Attributes
    ----------
    Item : object
        The :class:`~st_library.core.dataprovider.unstructured_data.item.Item` class itself

    """

    def __init__(self):
        self.Item = Item

    def download_file(self, dataset_id, filename):
        """
        Download a file to disk.

        Parameters
        ----------
        dataset_id : str
        filename : str

        Returns
        -------
        str
            Local file path

        """
        item = self.Item(dataset_id=dataset_id)
        return item.download_file(filename)

    def upload_file(self, dataset_id, filename, filepath):
        """
        Upload a file.

        Parameters
        ----------
        dataset_id : str
        filename : str
        filepath : str

        """
        item = self.Item(dataset_id=dataset_id)
        item.upload_file(filename, filepath)

    def delete_file(self, dataset_id, filename):
        """
        Delete a file.

        Parameters
        ----------
        dataset_id : str
        filename : str

        """
        item = self.Item(dataset_id=dataset_id)
        item.delete_file(filename)
