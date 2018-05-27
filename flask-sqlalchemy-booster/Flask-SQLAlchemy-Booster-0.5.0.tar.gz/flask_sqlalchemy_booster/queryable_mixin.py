# from sqlalchemy import func
from toolspy import subdict, remove_and_mark_duplicate_dicts, merge
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.ext.orderinglist import OrderingList
from sqlalchemy.orm import class_mapper


class QueryableMixin(object):

    """Contains all querying methods. Used for common ORM operations

    Attributes:
        _no_overwrite_(list): The list of attributes that should not be overwritten.

    """

    _no_overwrite_ = []

    _prevent_primary_key_initialization_ = True
    _prevent_primary_key_updation_ = True
    _fields_forbidden_from_being_set_ = None

    @classmethod
    def is_a_to_many_rel(cls, attr):
        return attr in cls.__mapper__.relationships and cls.__mapper__.relationships[attr].uselist

    @classmethod
    def is_a_to_one_rel(cls, attr):
        return attr in cls.__mapper__.relationships and not cls.__mapper__.relationships[attr].uselist

    @classmethod
    def primary_key_name(cls):
        return cls.__mapper__.primary_key[0].key

    @classmethod
    def primary_key(cls):
        return getattr(cls, cls.primary_key_name())

    def primary_key_value(self):
        return getattr(self, self.primary_key().name)

    @classmethod
    def column_names(cls):
        return cls.__mapper__.columns.keys()

    @classmethod
    def is_the_primary_key(cls, attr):
        return attr == cls.primary_key_name()

    @classmethod
    def mapped_rel_class(cls, attr):
        mapped_rel = next(
            r for r in cls.__mapper__.relationships
            if r.key == attr)
        return mapped_rel.mapper.class_

    def preprocess_kwargs_before_update(self, kwargs):
        return kwargs

    def update_without_commit(self, **kwargs):
        kwargs = self._preprocess_params(kwargs)
        kwargs = self.preprocess_kwargs_before_update(kwargs)
        for key, value in kwargs.iteritems():
            cls = type(self)
            if key not in cls.all_settable_keys():
                continue
            if not hasattr(cls, key) or isinstance(getattr(cls, key), property):
                continue
            if key not in self._no_overwrite_:
                setattr(self, key, value)
            if isinstance(getattr(self, key), OrderingList):
                getattr(self, key).reorder()
            elif isinstance(getattr(cls, key), AssociationProxy):
                target_name = getattr(cls, key).target_collection
                target_rel = getattr(self, target_name)
                if isinstance(target_rel, OrderingList):
                    target_rel.reorder()
        return self

    def commit(self):
        """Commits a transaction.
        """
        self.session.commit()

    def save(self):
        """Saves a model instance to db.

        Examples:
            >>> customer = Customer.new(name="hari")
            >>> customer.save()

        """
        self.session.add(self)
        self.session.commit()

    def delete(self, commit=True):
        """Deletes a model instance.

        Examples:

            >>> customer.delete()

        """
        self.session.delete(self)
        if commit:
            self.session.commit()

    def _isinstance(self, model, raise_error=True):
        """Checks if the specified model instance matches the class model.
        By default this method will raise a `ValueError` if the model is not of
        expected type.

        Args:

            model (Model) : The instance to be type checked

            raise_error (bool) : Flag to specify whether to raise error on
                type check failure

        Raises:

            ValueError: If `model` is not an instance of the respective Model
                class
        """
        rv = isinstance(model, self.__model__)
        if not rv and raise_error:
            raise ValueError('%s is not of type %s' % (model, self.__model__))
        return rv

    @classmethod
    def rollback_session(cls):
        cls.session.rollback()

    @classmethod
    def _preprocess_params(cls, kwargs):
        """Returns a preprocessed dictionary of parameters.
        Use this to filter the kwargs passed to `new`, `create`,
        `build` methods.

        Args:

            **kwargs: a dictionary of parameters
        """
        # kwargs.pop('csrf_token', None)
        for attr, val in kwargs.items():
            if cls.is_the_primary_key(attr) and cls._prevent_primary_key_initialization_:
                del kwargs[attr]
                continue
            if val == "":
                # Making an assumption that there is no good usecase
                # for setting an empty string. This will help prevent
                # cases where empty string is sent because of client
                # not clearing form fields to null
                kwargs[attr] = None
                continue
            if attr in class_mapper(cls).relationships and attr not in cls._no_overwrite_:
                rel = class_mapper(cls).relationships[attr]
                if rel.uselist:
                    if isinstance(val, list):
                        if all(isinstance(v, dict) for v in val):
                            rel_cls = cls.mapped_rel_class(attr)
                            kwargs[attr] = rel_cls.update_or_new_all(
                                list_of_kwargs=val, keys=[rel_cls.primary_key_name()])
                    elif isinstance(val, dict):
                        rel_cls = cls.mapped_rel_class(attr)
                        mapping_col = rel.collection_class().keyfunc.name
                        list_of_kwargs = [merge(v, {mapping_col: k}) for k, v in val.items()]
                        kwargs[attr] = {getattr(obj, mapping_col): obj for obj in rel_cls.update_or_new_all(
                            list_of_kwargs=list_of_kwargs, keys=[rel_cls.primary_key_name()])}
                elif isinstance(val, dict):
                    rel_cls = cls.mapped_rel_class(attr)
                    kwargs[attr] = rel_cls.update_or_new(
                        **merge(val, {'keys': [rel_cls.primary_key_name()]}))
        return kwargs

    @classmethod
    def preprocess_kwargs_before_new(cls, kwargs):
        return kwargs

    def clone(self, dict_struct=None, commit=True):
        def remove_primary_keys_from_dict_struct(klass, ds):
            pk = klass.primary_key_name()
            if "attrs" not in ds:
                ds['attrs'] = class_mapper(klass).columns.keys()
            if 'attrs' in ds and pk in ds['attrs']:
                ds['attrs'].remove(pk)
            if 'rels' in ds:
                for rel_name in ds['rels']:
                    mapped_rel = next(
                        r for r in class_mapper(klass).relationships
                        if r.key == rel_name)
                    rel_class = mapped_rel.mapper.class_
                    ds['rels'][rel_name] = remove_primary_keys_from_dict_struct(
                        rel_class, ds['rels'][rel_name])
            return ds
        cls = self.__class__
        if dict_struct is None:
            dict_struct = {}
        dict_struct = remove_primary_keys_from_dict_struct(cls, dict_struct)
        return cls.add(
            cls.new(**self.todict(dict_struct=dict_struct)), commit=commit)

    def update(self, **kwargs):
        """Updates an instance.

        Args:
            **kwargs  :  Arbitrary keyword arguments. Column names are
                keywords and their new values are the values.

        Examples:

            >>> customer.update(email="newemail@x.com", name="new")

        """
        kwargs = self._preprocess_params(kwargs)
        kwargs = self.preprocess_kwargs_before_update(kwargs)
        for key, value in kwargs.iteritems():
            cls = type(self)
            if not hasattr(cls, key) or isinstance(getattr(cls, key), property):
                continue
            if key not in self._no_overwrite_:
                setattr(self, key, value)
            if isinstance(getattr(self, key), OrderingList):
                getattr(self, key).reorder()
            elif isinstance(getattr(cls, key), AssociationProxy):
                target_name = getattr(cls, key).target_collection
                target_rel = getattr(self, target_name)
                if isinstance(target_rel, OrderingList):
                    target_rel.reorder()
        try:
            self.session.commit()
            return self
        except Exception as e:
            self.session.rollback()
            raise e

    @classmethod
    def filter_by(cls, **kwargs):
        """Same as SQLAlchemy's filter_by. Additionally this accepts
        two special keyword arguments `limit` and `reverse` for limiting
        the results and reversing the order respectively.

        Args:

            **kwargs: filter parameters

        Examples:

            >>> user = User.filter_by(email="new@x.com")

            >>> shipments = Shipment.filter_by(country="India", limit=3, reverse=True)

        """
        limit = kwargs.pop('limit', None)
        reverse = kwargs.pop('reverse', False)
        q = cls.query.filter_by(**kwargs)
        if reverse:
            q = q.order_by(cls.id.desc())
        if limit:
            q = q.limit(limit)
        return q

    @classmethod
    def filter(cls, *criterion, **kwargs):
        """Same as SQLAlchemy's filter. Additionally this accepts
        two special keyword arguments `limit` and `reverse` for limiting
        the results and reversing the order respectively.

        Args:

            **kwargs: filter parameters

        Examples:

            >>> user = User.filter(User.email=="new@x.com")

            >>> shipments = Order.filter(Order.price < 500, limit=3, reverse=True)

        """
        limit = kwargs.pop('limit', None)
        reverse = kwargs.pop('reverse', False)
        q = cls.query.filter_by(**kwargs).filter(*criterion)
        if reverse:
            q = q.order_by(cls.id.desc())
        if limit:
            q = q.limit(limit)
        return q

    @classmethod
    def count(cls, *criterion, **kwargs):
        """Returns a count of the instances meeting the specified
        filter criterion and kwargs.

        Examples:

            >>> User.count()
            500

            >>> User.count(country="India")
            300

            >>> User.count(User.age > 50, country="India")
            39

        """
        if criterion or kwargs:
            return cls.filter(
                *criterion,
                **kwargs).count()
        else:
            return cls.query.count()

    @classmethod
    def all(cls, *criterion, **kwargs):
        """Returns all the instances which fulfil the filtering
        criterion and kwargs if any given.

        Examples:

            >>> Tshirt.all()
            [tee1, tee2, tee4, tee5]

            >> Tshirt.all(reverse=True, limit=3)
            [tee5, tee4, tee2]

            >> Tshirt.all(color="Red")
            [tee4, tee2]
        """
        return cls.filter(*criterion, **kwargs).all()

    @classmethod
    def first(cls, *criterion, **kwargs):
        """Returns the first instance found of the model class
        filtered by the specified criterion and/or key word arguments.
        Return None if no result found.

        Examples:

            >>> will = User.first(name="Will")

        """
        return cls.filter(*criterion, **kwargs).first()

    @classmethod
    def one(cls, *criterion, **kwargs):
        """Similar to `first`. But throws an exception if 
        no result is found.

        Examples:

            >>> user = User.one(name="here")

        Raises:
            NoResultFound: No row was found for one()
        """
        return cls.filter(*criterion, **kwargs).one()

    @classmethod
    def last(cls, *criterion, **kwargs):
        """Returns the last instance matching the criterion and/or
        keyword arguments.

        Examples:

            last_male_user = User.last(gender="male")
        """
        kwargs['reverse'] = True
        return cls.first(*criterion, **kwargs)

    @classmethod
    def new(cls, **kwargs):
        """Returns a new, unsaved instance of the model class.

        """
        kwargs = cls.preprocess_kwargs_before_new(kwargs)
        if cls.__mapper__.polymorphic_on is not None:
            discriminator_key = cls.__mapper__.polymorphic_on.name
            discriminator_val = kwargs.get(discriminator_key)
            if discriminator_val is not None and discriminator_val in cls.__mapper__.polymorphic_map:
                actual_cls = cls.__mapper__.polymorphic_map[discriminator_val].class_
                return actual_cls(
                    **subdict(
                        actual_cls._preprocess_params(kwargs),
                        actual_cls.all_settable_keys())
                )
        return cls(**subdict(cls._preprocess_params(kwargs), cls.all_settable_keys()))

    @classmethod
    def add(cls, model, commit=True):
        """Adds a model instance to session and commits the
        transaction.

        Args:

            model: The instance to add.

        Examples:

            >>> customer = Customer.new(name="hari", email="hari@gmail.com")

            >>> Customer.add(customer)
            hari@gmail.com
        """
        if not isinstance(model, cls):
            raise ValueError('%s is not of type %s' % (model, cls))
        cls.session.add(model)
        try:
            if commit:
                cls.session.commit()
            return model
        except:
            cls.session.rollback()
            raise

    @classmethod
    def add_all(cls, models, commit=True, check_type=False):
        """Batch method for adding a list of model instances
        to the db in one get_or_404.

        Args:

            models (list): A list of the instances to add.
            commit (bool, optional): Defaults to True. If False, the
                transaction won't get committed.
            check_type (bool, optional) :  If True, each instance
                is type checked and exception is thrown if it is
                not an instance of the model. By default, False.

        Returns:
            list: A list of `Model` instances

        """
        if check_type:
            for model in models:
                if not isinstance(model, cls):
                    raise ValueError('%s is not of type %s' (model, cls))
        if None in models:
            cls.session.add_all([m for m in models if m is not None])
        else:
            cls.session.add_all(models)
        try:
            if commit:
                cls.session.commit()
            return models
        except:
            cls.session.rollback()
            raise

    @classmethod
    def _get(cls, key, keyval, user_id=None):
        result = cls.query.filter(
            getattr(cls, key) == keyval)
        if user_id and hasattr(cls, 'user_id'):
            result = result.filter(cls.user_id == user_id)
        return result.one()

    @classmethod
    def get(cls, keyval, key='id', user_id=None):
        """Fetches a single instance which has value `keyval`
        for the attribute `key`.

        Args:

            keyval: The value of the attribute.

            key (str, optional):  The attribute to search by. By default,
                it is 'id'.

        Returns:

            A model instance if found. Else None.

        Examples:

            >>> User.get(35)
            user35@i.com

            >>> User.get('user35@i.com', key='email')
            user35@i.com

        """
        if keyval is None:
            return None
        if (key in cls.__table__.columns
                and cls.__table__.columns[key].primary_key):
            # if user_id and hasattr(cls, 'user_id'):
            #     return cls.query.filter_by(id=keyval, user_id=user_id).first()
            return cls.query.get(keyval)
        else:
            result = cls.query.filter(
                getattr(cls, key) == keyval)
            # if user_id and hasattr(cls, 'user_id'):
            #     result = result.filter(cls.user_id == user_id)
            return result.first()

    @classmethod
    def get_all(cls, keyvals, key='id', user_id=None):
        """Works like a map function from keyvals to instances.


        Args:

            keyvals(list):  The list of values of the attribute.

            key (str, optional): The attribute to search by. By default, it is
                'id'.


        Returns:

            list: A list of model instances, in the same order as the list of
                keyvals.


        Examples:


            >>> User.get_all([2,5,7, 8000, 11])
            user2@i.com, user5@i.com, user7@i.com, None, user11@i.com

            >>> User.get_all(['user35@i.com', 'user5@i.com'], key='email')
            user35@i.com, user5@i.com

        """
        if len(keyvals) == 0:
            return []
        original_keyvals = keyvals
        keyvals_set = list(set(keyvals))
        resultset = cls.query.filter(getattr(cls, key).in_(keyvals_set))
        # This is ridiculous. user_id check cannot be here. A hangover
        # from the time this lib was inside our app codebase
        # if user_id and hasattr(cls, 'user_id'):
        #     resultset = resultset.filter(cls.user_id == user_id)
        # We need the results in the same order as the input keyvals
        # So order by field in SQL
        key_result_mapping = {getattr(result, key): result for result in resultset.all()}
        return [key_result_mapping.get(kv) for kv in original_keyvals]

        # if len(keyvals) == 0:
        #     return []
        # resultset = cls.query.filter(getattr(cls, key).in_(keyvals))
        # # This is ridiculous. user_id check cannot be here. A hangover
        # # from the time this lib was inside our app codebase
        # if user_id and hasattr(cls, 'user_id'):
        #     resultset = resultset.filter(cls.user_id == user_id)
        # # We need the results in the same order as the input keyvals
        # # So order by field in SQL
        # resultset = resultset.order_by(
        #     func.field(getattr(cls, key), *keyvals))
        # return place_nulls(key, keyvals, resultset.all())

    @classmethod
    def get_or_404(cls, id):
        """Same as Flask-SQLAlchemy's `get_or_404`.
        """
        return cls.query.get_or_404(id)

    @classmethod
    def create(cls, **kwargs):
        """Initializes a new instance, adds it to the db and commits
        the transaction.

        Args:

            **kwargs: The keyword arguments for the init constructor.

        Examples:

            >>> user = User.create(name="Vicky", email="vicky@h.com")
            >>> user.id
            35
        """
        try:
            return cls.add(cls.new(**kwargs))
        except:
            cls.session.rollback()
            raise

    @classmethod
    def find_or_create(cls, **kwargs):
        """Checks if an instance already exists by filtering with the
        kwargs. If yes, returns that instance. If not, creates a new
        instance with kwargs and returns it

        Args:

            **kwargs: The keyword arguments which are used for filtering
                and initialization.
            keys(list, optional): A special keyword argument.
                If passed, only the set of keys mentioned here will be used
                for filtering. Useful when we want to 'find' based on a subset
                of the keys and create with all the keys

        Examples:

            >>> customer = Customer.find_or_create(
            ...     name="vicky", email="vicky@h.com", country="India")
            >>> customer.id
            45
            >>> customer1 = Customer.find_or_create(
            ...     name="vicky", email="vicky@h.com", country="India")
            >>> customer1==customer
            True
            >>> customer2 = Customer.find_or_create(
            ...     name="vicky", email="vicky@h.com", country="Russia")
            >>> customer2==customer
            False
            >>> customer3 = Customer.find_or_create(
            ...      name="vicky", email="vicky@h.com", country="Russia",
            ...      keys=['name', 'email'])
            >>> customer3==customer
            True
        """
        keys = kwargs.pop('keys') if 'keys' in kwargs else []
        return cls.first(**subdict(kwargs, keys)) or cls.create(**kwargs)

    @classmethod
    def get_updated_or_new_obj(cls, kwargs=None, filter_keys=None):
        if filter_keys is None:
            filter_keys = []
        if kwargs is None:
            kwargs = {}
        filter_kwargs = subdict(kwargs, filter_keys)
        if filter_kwargs == {}:
            obj = None
        else:
            obj = cls.first(**filter_kwargs)
        if obj is not None:
            update_kwargs = {
                k: v for k, v in kwargs.iteritems()
                if k not in filter_keys and k not in cls._no_overwrite_}
            obj.update_without_commit(**update_kwargs)
            # for key, value in kwargs.iteritems():
            #     if (key not in filter_keys and
            #             key not in cls._no_overwrite_):
            #         setattr(obj, key, value)
        else:
            obj = cls.new(**kwargs)
        return obj

    @classmethod
    def update_or_new(cls, **kwargs):
        keys = kwargs.pop('keys') if 'keys' in kwargs else []
        return cls.get_updated_or_new_obj(kwargs, keys)

    @classmethod
    def update_or_new_all(cls, list_of_kwargs, keys=[]):
        objs = []
        for kwargs in list_of_kwargs:
            objs.append(cls.get_updated_or_new_obj(kwargs, keys))
        return objs

    @classmethod
    def update_or_build(cls, **kwargs):
        keys = kwargs.pop('keys') if 'keys' in kwargs else []
        filter_kwargs = subdict(kwargs, keys)
        if filter_kwargs == {}:
            obj = None
        else:
            obj = cls.first(**filter_kwargs)
        if obj is not None:
            for key, value in kwargs.iteritems():
                if (key not in keys and
                        key not in cls._no_overwrite_):
                    setattr(obj, key, value)
        else:
            obj = cls.build(**kwargs)
        return obj

    @classmethod
    def update_or_create(cls, **kwargs):
        """Checks if an instance already exists by filtering with the
        kwargs. If yes, updates the instance with new kwargs and
        returns that instance. If not, creates a new
        instance with kwargs and returns it.

        Args:

            **kwargs: The keyword arguments which are used for filtering
                and initialization.

            keys (list, optional): A special keyword argument. If passed,
                only the set of keys mentioned here will be used for filtering.
                Useful when we want to 'filter' based on a subset of the keys
                and create with all the keys.

        Examples:

            >>> customer = Customer.update_or_create(
            ...     name="vicky", email="vicky@h.com", country="India")
            >>> customer.id
            45
            >>> customer1 = Customer.update_or_create(
            ...     name="vicky", email="vicky@h.com", country="India")
            >>> customer1==customer
            True
            >>> customer2 = Customer.update_or_create(
            ...     name="vicky", email="vicky@h.com", country="Russia")
            >>> customer2==customer
            False
            >>> customer3 = Customer.update_or_create(
            ...      name="vicky", email="vicky@h.com", country="Russia",
            ...      keys=['name', 'email'])
            >>> customer3==customer
            True
        """
        keys = kwargs.pop('keys') if 'keys' in kwargs else []
        filter_kwargs = subdict(kwargs, keys)
        if filter_kwargs == {}:
            obj = None
        else:
            obj = cls.first(**filter_kwargs)
        if obj is not None:
            for key, value in kwargs.iteritems():
                if (key not in keys and
                        key not in cls._no_overwrite_):
                    setattr(obj, key, value)
            try:
                cls.session.commit()
            except:
                cls.session.rollback()
                raise
        else:
            obj = cls.create(**kwargs)
        return obj

    @classmethod
    def create_all(cls, list_of_kwargs):
        """Batch method for creating a list of instances

        Args:
            list_of_kwargs(list of dicts): hereA list of dicts where
                each dict denotes the keyword args that you would pass
                to the create method separately

        Examples:

            >>> Customer.create_all([
            ... {'name': 'Vicky', 'age': 34, 'user_id': 1},
            ... {'name': 'Ron', 'age': 40, 'user_id': 1, 'gender': 'Male'}])
        """
        try:
            return cls.add_all([
                cls.new(**kwargs) if kwargs is not None else None for kwargs in list_of_kwargs])
        except:
            cls.session.rollback()
            raise

    @classmethod
    def find_or_create_all(cls, list_of_kwargs, keys=[]):
        """Batch method for querying for a list of instances and
        creating them if required

        Args:
            list_of_kwargs(list of dicts): A list of dicts where
                each dict denotes the keyword args that you would pass
                to the create method separately

            keys (list, optional): A list of keys to use for the 
                initial finding step. Matching is done only on these
                attributes.

        Examples:

            >>> Customer.find_or_create_all([
            ... {'name': 'Vicky', 'email': 'vicky@x.com', 'age': 34},
            ... {'name': 'Ron', 'age': 40, 'email': 'ron@x.com',
            ... 'gender': 'Male'}], keys=['name', 'email'])
        """
        list_of_kwargs_wo_dupes, markers = remove_and_mark_duplicate_dicts(
            list_of_kwargs, keys)
        added_objs = cls.add_all([
            cls.first(**subdict(kwargs, keys)) or cls.new(**kwargs)
            for kwargs in list_of_kwargs_wo_dupes])
        result_objs = []
        iterator_of_added_objs = iter(added_objs)
        for idx in range(len(list_of_kwargs)):
            if idx in markers:
                result_objs.append(added_objs[markers[idx]])
            else:
                result_objs.append(next(
                    iterator_of_added_objs))
        return result_objs

    @classmethod
    def update_or_create_all(cls, list_of_kwargs, keys=[]):
        """Batch method for updating a list of instances and
        creating them if required

        Args:
            list_of_kwargs(list of dicts): A list of dicts where
                each dict denotes the keyword args that you would pass
                to the create method separately

            keys (list, optional): A list of keys to use for the 
                initial finding step. Matching is done only on these
                attributes.

        Examples:

            >>> Customer.update_or_create_all([
            ... {'name': 'Vicky', 'email': 'vicky@x.com', 'age': 34},
            ... {'name': 'Ron', 'age': 40, 'email': 'ron@x.com',
            ... 'gender': 'Male'}], keys=['name', 'email'])
        """
        objs = []
        for kwargs in list_of_kwargs:
            filter_kwargs = subdict(kwargs, keys)
            if filter_kwargs == {}:
                obj = None
            else:
                obj = cls.first(**filter_kwargs)
            if obj is not None:
                for key, value in kwargs.iteritems():
                    if (key not in keys and
                            key not in cls._no_overwrite_):
                        setattr(obj, key, value)
            else:
                obj = cls.new(**kwargs)
            objs.append(obj)
        try:
            return cls.add_all(objs)
        except:
            cls.session.rollback()
            raise

    @classmethod
    def update_or_build_all(cls, list_of_kwargs, keys=[]):
        """Batch method for updating a list of instances and
        creating them if required

        Args:
            list_of_kwargs(list of dicts): A list of dicts where
                each dict denotes the keyword args that you would pass
                to the create method separately

            keys (list, optional): A list of keys to use for the 
                initial finding step. Matching is done only on these
                attributes.

        Examples:

            >>> Customer.update_or_create_all([
            ... {'name': 'Vicky', 'email': 'vicky@x.com', 'age': 34},
            ... {'name': 'Ron', 'age': 40, 'email': 'ron@x.com',
            ... 'gender': 'Male'}], keys=['name', 'email'])
        """
        objs = []
        for kwargs in list_of_kwargs:
            filter_kwargs = subdict(kwargs, keys)
            if filter_kwargs == {}:
                obj = None
            else:
                obj = cls.first(**filter_kwargs)
            if obj is not None:
                for key, value in kwargs.iteritems():
                    if (key not in keys and
                            key not in cls._no_overwrite_):
                        setattr(obj, key, value)
            else:
                obj = cls.new(**kwargs)
            objs.append(obj)
        try:
            return cls.add_all(objs, commit=False)
        except:
            cls.session.rollback()
            raise

    @classmethod
    def build(cls, **kwargs):
        """Similar to create. But the transaction is not committed

        Args:

            **kwargs : The keyword arguments for the constructor

        Returns:

            A model instance which has been added to db session. But session
            transaction has not been committed yet.
        """
        return cls.add(cls.new(**kwargs), commit=False)

    @classmethod
    def find_or_build(cls, **kwargs):
        """Checks if an instance already exists in db with these kwargs else
        returns a new, saved instance of the service's model class.

        Args:
            **kwargs: instance parameters
        """
        keys = kwargs.pop('keys') if 'keys' in kwargs else []
        return cls.first(**subdict(kwargs, keys)) or cls.build(**kwargs)

    @classmethod
    def find_or_new(cls, **kwargs):
        keys = kwargs.pop('keys') if 'keys' in kwargs else []
        return cls.first(**subdict(kwargs, keys)) or cls.new(**kwargs)

    @classmethod
    def new_all(cls, list_of_kwargs):
        return [cls.new(**kwargs) for kwargs in list_of_kwargs]

    @classmethod
    def find_or_new_all(cls, list_of_kwargs, keys=[]):
        return [cls.first(**subdict(kwargs, keys)) or cls.new(**kwargs) for kwargs in list_of_kwargs]

    @classmethod
    def build_all(cls, list_of_kwargs):
        """Similar to `create_all`. But transaction is not committed.
        """
        return cls.add_all([
            cls.new(**kwargs) for kwargs in list_of_kwargs], commit=False)

    @classmethod
    def find_or_build_all(cls, list_of_kwargs):
        """Similar to `find_or_create_all`. But transaction is not committed.
        """
        return cls.add_all([cls.first(**kwargs) or cls.new(**kwargs)
                            for kwargs in list_of_kwargs], commit=False)

    @classmethod
    def update_all(cls, *criterion, **kwargs):
        """Batch method for updating all instances obeying the criterion

        Args:
            *criterion: SQLAlchemy query criterion for filtering what
                instances to update
            **kwargs: The parameters to be updated

        Examples:

            >>> User.update_all(active=True)

            >>> Customer.update_all(Customer.country=='India', active=True)

        The second example sets active=True for all customers with
        country India.
        """
        try:
            r = cls.query.filter(*criterion).update(kwargs, 'fetch')
            cls.session.commit()
            return r
        except:
            cls.session.rollback()
            raise

    @classmethod
    def get_and_update(cls, id, **kwargs):
        """Returns an updated instance of the service's model class.

        Args:
            model: the model to update
            **kwargs: update parameters
        """
        model = cls.get(id)
        for k, v in cls._preprocess_params(kwargs).items():
            setattr(model, k, v)
        cls.session.commit()
        return model

    @classmethod
    def get_and_setattr(cls, id, **kwargs):
        """Returns an updated instance of the service's model class.

        Args:
            model: the model to update
            **kwargs: update parameters
        """
        model = cls.get(id)
        for k, v in cls._preprocess_params(kwargs).items():
            setattr(model, k, v)
        return model

    @classmethod
    def buckets(cls, bucket_size=None):
    	return cls.query.buckets(bucket_size=bucket_size)