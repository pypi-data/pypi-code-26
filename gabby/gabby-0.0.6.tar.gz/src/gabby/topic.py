from collections import namedtuple


Topic = namedtuple('Topic', ['name', 'fmt'])


class TopicCollection(list):
    """
    Collection to handler Topic groups operations
    """
    def __init__(self, *args):
        if args and isinstance(args[0], Topic):
            self.extend(args)
        else:
            self.extend(args[0])

    def append(self, topic):
        if isinstance(topic, Topic):
            if list(filter(lambda x: x.name == topic.name, self)) == []:
                super().append(topic)
            else:
                raise AttributeError("Topic must be unique")
        else:
            raise TypeError("You can only add Topic objects")

    def extend(self, topics):
        for t in topics:
            self.append(t)

    def find_by(self, **kwargs):
        """
        Get topic by any attribute.

        Return:
            First that matches

        Example:
            >>> TopicCollection(Topic('a', 'b')).find_by(name='a')
            ... Topic(name='a', fmt='b')
        """
        match_topics = self.filter_by(**kwargs)
        return match_topics[0] if match_topics else None

    def filter_by(self, **kwargs):
        """
        Filter by any topic attribute

        Example:
            >>> TopicCollection(Topic('a', 'b')).filter_by(name='a')
            ... [Topic(name='a', fmt='b')]
        """
        return list(filter(
            lambda x: all([getattr(x, attr) == value
                           for attr, value in kwargs.items()]), self
        ))
