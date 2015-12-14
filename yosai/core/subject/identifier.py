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

from collections import defaultdict
from yosai.core import (
    InvalidArgumentException,
    serialize_abcs,
    subject_abcs,
)
from marshmallow import Schema, fields, post_load


class SimpleIdentifierCollection(subject_abcs.MutableIdentifierCollection,
                                 serialize_abcs.Serializable):
    """
    A collection of all identifying attributes associated with a corresponding
    Subject. An *identifier*, known in Shiro as a *principal*, is just a
    security term for an identifying attribute, such as a username or user id
    or social security number or anything else that can be considered an
    'identifying' attribute for a Subject.

    The source name that an identifier originates from as a Subject is first
    authenticated serves as key.

    To obtain the identifier for a specific Source, see the from_source method.
    You can also see which sources contributed to this SIC via the
    source_names attribute (property).

    Yosai simplifies the identifier for a realm, changing it from a set
    to a scalar value.
    """

    # yosai.core.re-ordered the argument list:
    def __init__(self, source_name=None, identifier=None,
                 identifier_collection=None):
        """
        :type source_name: String
        :type identifier_collection: a SimpleIdentifierCollection
        """
        self.source_identifiers = defaultdict(set)
        self._primary_identifier = None

        if identifier_collection:
            self.add_collection(identifier_collection=identifier_collection)
        elif (source_name and identifier):
            self.add(source_name=source_name,
                     identifier=identifier)

    # yosai.core.omits get_identifier_lazy because it uses a defaultdict(set)
    # yosai.core.omits asSet, asList, and toString  -- TBD

    @property
    def primary_identifier(self):
        if (not self._primary_identifier):
            try:
                # DG:  shiro arbitrarily selects for missing primary identifier
                identifiers = self.source_identifiers.values()
                primary_identifier = next(iter(identifiers))
            except (AttributeError, TypeError):
                msg = "Failed to arbitrarily obtain primary identifier"
                print(msg)
                # log warning here
                return None
            else:
                self._primary_identifier = primary_identifier
                return primary_identifier
        return self._primary_identifier

    # there is no primary_identifier setter because it should not be manually set

    def add(self, source_name, identifier):
        """
        :type source_name: String
        :type identifiers: String
        """
        self.source_identifiers[source_name] = identifier

    def add_collection(self, identifier_collection):
        """
        an overloaded method that will add a collection ELSE a single identifer

        :type identifier_collection: a SimpleIdentifierCollection
        """
        try:
            new_source_identifiers = identifier_collection.source_identifiers
            self.source_identifiers.update(new_source_identifiers)
        except AttributeError:
            msg = "Invalid identifier collection passed as argument"
            raise InvalidArgumentException(msg)

    # yosai.core.consolidates one_by_type with by_type:
    def by_type(self, identifier_class):
        """
        returns all unique instances of a type of identifier

        :param identifier_class: the class to match identifier with
        :returns: a tuple
        """
        myidentifiers = set()
        for identifier in self.source_identifiers.values():
            if (isinstance(identifier, identifier_class)):
                myidentifiers.update([identifier])
        return frozenset(myidentifiers)

    def from_source(self, source_name):
        return self.source_identifiers.get(source_name)

    @property
    def source_names(self):
        return tuple(self.source_identifiers.keys())  # make immutable

    @property
    def is_empty(self):
        return (not self.source_identifiers.keys())

    def clear(self):
        self.source_identifiers = {}

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, subject_abcs.MutableIdentifierCollection):
            return self.source_identifiers == other.source_identifiers
        return False

    def __repr__(self):
        keyvals = ','.join(str(key) + '=' + str(value) for (key, value) in
                           self.source_identifiers.items())
        return "SimpleIdentifierCollection(" + keyvals + ")"

    @classmethod
    def serialization_schema(cls):
        """
        Note about serialization
        -------------------------
        The following Schema was implemented using the fields.Dict() as its
        default, for flexibility. Since a developer (YOU) *should* know the
        realms that will be used by your application, consider updating this
        Schema, changing from a Dict() field to a concrete Schema implementation
        consisting of the actual realms(sources) used.
        """
        class SerializationSchema(Schema):
            source_identifiers = fields.Dict()

            @post_load
            def make_authz_info(self, data):
                mycls = SimpleIdentifierCollection
                instance = mycls.__new__(mycls)
                instance.__dict__.update(data)
                return instance

        return SerializationSchema
