"""
Contains functions and classes for serializing and de-serializing
data.
"""
import typing as ty

from json import JSONEncoder

AS_JSON_PROPERTY = 'as_json'
FROM_JSON_PROPERTY = 'from_json'
TYPE_KEY = '_type_key'

serializable_types = {}


class Encoder(JSONEncoder):
    """
    Encodes object as json
    """
    def default(self, o: ty.Any) -> ty.Any:
        """
        Handles the default serialization case, wherein an object is
        not by default serializable.
        If the object is recognized as a custom serializable object,
        it is converted into a serializable object.
        Otherwise the superclass JSONEncoder default method is used.
        :param o: Any
        :return: Any serializable
        """
        k = _get_type_key(type(o))
        if k in serializable_types:
            d = o.as_serializable
            d[TYPE_KEY] = k
            return d
        return super().default(o)


def hook(o: ty.Any) -> ty.Any:
    """
    Hook taking the default-deserialized object (usually a dictionary)
    and, if the object is recognized as an encoded serializable of
    another type, re-creates the type instance.
    :param o: Any type deserializable by default.
    :return: Any
    """
    try:
        k = o.pop(TYPE_KEY)
    except (KeyError, AttributeError):
        return o
    else:
        object_type = serializable_types[k]
        return object_type.from_serializable(o)


def serializable(clz):
    """
    Decorator for a class marking it as serializable.
    :param clz: Type
    :return: Type
    """
    k = _get_type_key(clz)
    if k in serializable_types:
        raise ValueError(f'Passed type: {clz} name conflicts with previously'
                         f'registered type: {serializable_types[k]}')
    serializable_types[k] = clz
    return clz


def _get_type_key(clz: ty.Type) -> ty.Any:
    """
    Gets key used for storing passed type in dictionary of
    serializable types. Should return a unique value for each passed
    type.
    :param clz: Type
    :return: ty.Any
    """
    return clz.__name__
