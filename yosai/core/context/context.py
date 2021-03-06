"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from yosai.core import (
    serialize_abcs,
    InvalidArgumentException,
)
from marshmallow import Schema, fields, post_load


class MapContext(serialize_abcs.Serializable):
    """
    a dict with a few more features
    """
    def __init__(self, context_map={}):
        """
        :type context_map: dict
        """
        self.context = dict(context_map)

    # entrySet:
    @property
    def attributes(self):
        return list(self.context.items())

    # keySet:
    @property
    def attribute_keys(self):
        return list(self.context.keys())

    @property
    def is_empty(self):
        return len(self.context) == 0

    @property
    def values(self):
        return tuple(self.context.values())

    # yosai.core.omits getTypedValue because of Python's dynamic typing and to
    # defer validation/exception handling up the stack

    def clear(self):
        self.context.clear()

    def size(self):
        return len(self.context)

    # key-based membership check:
    def __contains__(self, attr):
        return attr in self.context

    # yosai.core.omits the values-based membership version of __contains__  (TBD)

    def put_all(self, contextobj):
        try:
            self.context.update(contextobj.context)
        except AttributeError:
            msg = "passed invalid argument to put_all"
            print(msg)
            # log exception here
            raise InvalidArgumentException(msg)

    def put(self, attr, value):
        self.context[attr] = value

    # shiro nullSafePut:
    def none_safe_put(self, attr, value):
        if value:
            self.context[attr] = value

    # omitting type validation in Yosai (re: getTypedValue)
    def get(self, attr):
        return self.context.get(attr)

    def remove(self, attr):
        return self.context.pop(attr, None)

    def __eq__(self, other):
        try:
            return self.context == other.context
        except:
            return False

    def __repr__(self):
        return "<" + self.__class__.__name__ + "(" + str(self.context) + ")>"

    class ContextSchema(Schema):
        # The ContextSchema is user defined -- no defaults are provided
        # Define key fields here for the context dictionary

        @post_load
        def make_context(self, data):
            return dict(data)

    @classmethod
    def serialization_schema(cls):
        class SerializationSchema(Schema):
            context = fields.Nested(cls.ContextSchema)

            @post_load
            def make_mapcontext(self, data):
                mycls = MapContext
                instance = mycls.__new__(mycls)
                instance.__dict__.update(data)
                return instance

        return SerializationSchema
