# -*- coding: utf-8 -*-
"""
goodreads_api_client.resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Holds classes for each Goodreads API Resource a user can interact with via
the Goodreads API
"""

from goodreads_api_client.resources.author import Author
from goodreads_api_client.resources.author_following import AuthorFollowing
from goodreads_api_client.resources.book import Book
from goodreads_api_client.resources.comment import Comment
from goodreads_api_client.resources.event import Event
from goodreads_api_client.resources.follower import Follower
from goodreads_api_client.resources.friend import Friend
from goodreads_api_client.resources.group import Group
from goodreads_api_client.resources.list import List
from goodreads_api_client.resources.notification import Notification
from goodreads_api_client.resources.owned_book import OwnedBook
from goodreads_api_client.resources.quote import Quote
from goodreads_api_client.resources.rating import Rating
from goodreads_api_client.resources.read_status import ReadStatus
from goodreads_api_client.resources.recommendation import Recommendation
from goodreads_api_client.resources.review import Review
from goodreads_api_client.resources.series import Series
from goodreads_api_client.resources.shelf import Shelf
from goodreads_api_client.resources.topic import Topic
from goodreads_api_client.resources.update import Update
from goodreads_api_client.resources.user import User
from goodreads_api_client.resources.user_shelf import UserShelf
from goodreads_api_client.resources.user_status import UserStatus
from goodreads_api_client.resources.work import Work

__all__ = [
    'Author',
    'AuthorFollowing',
    'Book',
    'Comment',
    'Event',
    'Follower',
    'Friend',
    'Group',
    'List',
    'Notification',
    'OwnedBook',
    'Quote',
    'Rating',
    'ReadStatus',
    'Recommendation',
    'Review',
    'Series',
    'Shelf',
    'Topic',
    'Update',
    'User',
    'UserShelf',
    'UserStatus',
    'Work',
]
