"""Docstring for module."""
from flask_sqlalchemy import SQLAlchemy

# def get_db():
#     """Get database object from the Flask globals.
#
#     NOTE: This is an expectation of every Flask App that uses this blueprint to
#         set the `_db` attribute as the Flask-SQLAlchemy object.
#     """
#     db = current_app._db
#
#     if db is None:
#         raise AttributeError("Job Status blueprint needs `_db` attribute set in `flask.current_app`.")
#     else:
#         return db
#
#
# db = get_db()

db = SQLAlchemy()


class Base(db.Model):
    """Base class for all the tables.

    Consists of two default columns `created_at` and `modified_at` .
    """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime,
                            default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


class Job(Base):
    """A generic Job db data structure that has sub-tasks."""

    __tablename__ = 'job'

    tasks = db.relationship("Task", backref="job")

    uuid = db.Column(db.String(120), nullable=True, index=True)
    name = db.Column(db.String(256), nullable=True)
    payload_text = db.Column(db.Text(), nullable=True)
    status = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        """String representation of the class."""
        return '<Job %r>' % self.id

    def as_json(self):
        """."""
        json_repr = {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'status': self.status,
            'payload_text': self.payload_text,
            'tasks': [task.as_json() for task in self.tasks]
        }
        return json_repr


class Task(Base):
    """A task that is a sub-task of a Job."""

    __tablename__ = 'task'

    # 'job' from backref
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))

    uuid = db.Column(db.String(120), nullable=True, index=True)
    name = db.Column(db.String(256), nullable=True)
    payload_text = db.Column(db.Text())
    status = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        """String representation of the class."""
        return '<Task %r>' % self.id

    def as_json(self):
        """."""
        json_repr = {
            'job_id': self.job_id,
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'payload_text': self.payload_text,
            'status': self.status,
        }
        return json_repr
