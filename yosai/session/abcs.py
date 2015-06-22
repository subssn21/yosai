from abc import ABCMeta, abstractmethod
from yosai import (
    IllegalStateException,
    UnknownSessionException,
)
import uuid

class Session(metaclass=ABCMeta):
    """
    A Session is a stateful data context associated with a single 
    Subject's (user, daemon process, etc) interaction with a software system 
    over a period of time.

    A Session is intended to be managed by the business tier and accessible via
    other tiers without being tied to any given client technology.  This is a
    great benefit to Python systems, since until now the only viable session 
    mechanisms were those highly-coupled and deeply embedded in web application 
    frameworks.
    """

    @property
    @abstractmethod
    def session_id(self):
        """
        The unique identifier assigned by the system upon session creation.
        """
        pass
    
    @property
    @abstractmethod
    def start_timestamp(self):
        """ 
        The time that the session started (the time that the system created 
        the instance )
        """
        pass

    @property
    @abstractmethod
    def last_access_time(self):
        """ 
        Returns the last time the application received a request or method 
        invocation from THE USER associated with this session.  Application 
        calls to this method do not affect this access time.
        """
        pass

    @property
    @abstractmethod
    def absolute_timeout(self):
        """ 
        Returns the time, in milliseconds, that the session may 
        exist before it expires
        """    
        pass

    @absolute_timeout.setter
    @abstractmethod
    def absolute_timeout(self, abs_timeout): 
        """ 
        Sets the time in milliseconds that the session may exist 
        before expiring.

        - A negative value means the session will never expire
        - A non-negative value (0 or greater) means the session expiration will
          occur if idle for that length of time.
        """
        pass

    @property
    @abstractmethod
    def idle_timeout(self):
        """ 
        Returns the time, in milliseconds, that the session may 
        remain idle before it expires
        """    
        pass

    @idle_timeout.setter
    @abstractmethod
    def idle_timeout(self, idle_timeout): 
        """ 
        Sets the time in milliseconds that the session may remain idle 
        before expiring.

        - A negative value means the session will never expire
        - A non-negative value (0 or greater) means the session expiration will
          occur if idle for that length of time.
        """
        pass

    @property
    @abstractmethod
    def host(self):
        """
        Returns the host name or IP string of the host that originated this
        session, or None if the host is unknown.
        """
        pass

    @abstractmethod
    def touch(self):
        """
        Explicitly updates the last_access_time of this session to the
        current time when this method is invoked.  This method can be used to
        ensure a session does not time out.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Explicitly stops (invalidates) this session and releases all associated
        resources.  
        """
        pass

    @property
    @abstractmethod
    def attribute_keys(self):
        """
        Returns the keys of all the attributes stored under this session.  If
        there are no attributes, this returns an empty collection.
        """
        pass

    @abstractmethod
    def get_attribute(self, key):
        """
        Returns the object bound to this session identified by the specified
        key.  If there is no object bound under the key, None is returned.
        """
        pass

    @abstractmethod
    def set_attribute(self, key, value):
        """
        Binds the specified value to this session, uniquely identified by the
        specifed key name.  If there is already an object bound under
        the key name, that existing object will be replaced by the new 
        value.  
        """
        pass

    @abstractmethod
    def remove_attribute(self, key):
        """
        Removes (unbinds) the object bound to this session under the specified
        key name.  
        """
        pass


class SessionListener(metaclass=ABCMeta):
    """
    Interface to be implemented by components that wish to be notified of
    events that occur during a Session's life cycle.
    """

    @abstractmethod
    def on_start(self, session):
        """
        Notification callback that occurs when the corresponding Session has
        started.  
        
        :param session: the session that has started
        """
        pass

    @abstractmethod
    def on_stop(self, session):
        """ 
        Notification callback that occurs when the corresponding Session has
        stopped, either programmatically via {@link Session#stop} or
        automatically upon a subject logging out.

        :param session: the session that has stopped
        """ 
        pass

    @abstractmethod
    def on_expiration(self, session):
        """
        Notification callback that occurs when the corresponding Session has
        expired.
 
        Note: this method is almost never called at the exact instant that the
        Session expires.  Almost all session management systems, including
        Yosai's implementations, lazily validate sessions - either when they
        are accessed or during a regular validation interval.  It would be too
        resource intensive to monitor every single session instance to know the
        exact instant it expires.

        If you need to perform time-based logic when a session expires, it
        is best to write it based on the session's last_access_time and
        NOT the time when this method is called.
     
        :param session: the session that has expired
        """
        pass


class SessionStorageEvaluator(metaclass=ABCMeta):

    @abstractmethod
    def is_session_storage_enabled(self, subject):
        pass


class ValidatingSession(Session):

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def validate(self):
        pass


class SessionFactory(metaclass=ABCMeta):
    """
    A simple factory class that instantiates concrete Session instances.  This
    is mainly a mechanism to allow instances to be created at runtime if they
    need to be different than the defaults.  It is not used by end-users of the
    framework, but rather those configuring Yosai to work in an application,
    and is typically injected into a SecurityManager or SessionManager.
    """

    @abstractmethod
    def create_session(self, init_data):
        """
        Creates a new Session instance based on the specified contextual 
        initialization data.
     
        :param init_data: the initialization data to be used during 
                          Session creation.
        :type init_data: SessionContext 
        :returns: a new Session instance
        """
        pass


class SessionIDGenerator(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def generate_id(self, session):
        pass


class SessionManager(metaclass=ABCMeta):
    """ 
    A SessionManager manages the creation, maintenance, and clean-up of all
    application Sessions
    """
    
    @abstractmethod
    def start(self, session_context):
        pass
        """
        Starts a new session based on the specified contextual initialization
        data, which can be used by the underlying implementation to determine
        how exactly to create the internal Session instance.
        """
     
    @abstractmethod
    def get_session(self, session_key):
        """
        Retrieves the session corresponding to the specified contextual
        data (such as a session ID if applicable), or None if no
        Session could be found.  If a session is found but invalid (stopped
        or expired), an exception will raise
        """
        pass


class NativeSessionManager(SessionManager):
    """
    A Native session manager is one that manages sessions natively - that is,
    it is directly responsible * for the creation, persistence and removal of
    Session instances and their lifecycles.
    """

    @abstractmethod
    def get_start_timestamp(self, session_key):
        """ 
        Returns the time the associated Session started (was created).
        """
        pass

    @abstractmethod
    def get_last_access_time(self, session_key):
        """
        Returns the time the associated {@code Session} last interacted with
        the system.  
        """
        pass

    @abstractmethod
    def is_valid(self, session_key):
        """
        Returns True if the associated session is valid (it exists and is 
        not stopped nor expired), False otherwise.
        """
        pass

    @abstractmethod
    def check_valid(self, session_key):
        """ 
        Returns quietly if the associated session is valid (it exists and is
        not stopped or expired) or raises an InvalidSessionException 
        indicating that the session_id is invalid.  This might be preferred 
        to be used instead of is_valid since any exception thrown will 
        definitively explain the reason for invalidation.
        """
        pass

    @abstractmethod
    def get_idle_timeout(self, session_key):
        """
        Returns the time that the associated session may remain idle before 
        expiring.

        - A negative return value means the session will never expire.
        - A non-negative return value (0 or greater) means the session 
          expiration will occur if idle for that length of time.

        raises InvalidSessionException if the session has been stopped or 
        expired prior to calling this method
        """
        pass

    @abstractmethod
    def get_absolute_timeout(self, session_key):
        """ 
        Returns the time that the associated session may remain idle before 
        expiring.
        """
        pass

    @abstractmethod
    def set_idle_timeout(self, session_key, idle_timeout):
        """
        Sets the time, as a datetime.timedelta, that the associated session may
        remain idle before expiring.
        
        - A negative return value means the session will never expire.
        - A non-negative return value (0 or greater) means the session
          expiration will occur if idle for that * length of time.

        raises InvalidSessionException if the session has been stopped or 
        expired prior to calling this method
        """
        pass

    @abstractmethod
    def set_absolute_timeout(self, session_key, absolute_timeout):
        """
        Sets the time, as a datetime.timedelta, that the associated session may
        exist before expiring.
        
        raises InvalidSessionException if the session has been stopped or 
        expired prior to calling this method
        """
        pass

    @abstractmethod
    def touch(self, session_key):
        """
        Updates the last accessed time of the session identified by
        session_id.  This can be used to explicitly ensure that a
        session does not time out.
        
        raises InvalidSessionException if the session has been stopped or 
        expired prior to calling this method
        """
        pass

    @abstractmethod
    def get_host(self, session_key):
        """
        Returns the host name or IP string of the host where the session was
        started, if known.  If no host name or IP was specified when starting
        the session, this method returns None 
        """
        pass

    @abstractmethod
    def stop(self, session_key):
        """
        Explicitly stops the associated session, thereby releasing all of its
        resources.  
        """
        pass

    @abstractmethod
    def get_attribute_keys(self, session_key):
        """
        Returns all attribute keys maintained by the target session or an empty
        collection if there are no attributes.  
     
        raises InvalidSessionException if the associated session has stopped or
        expired prior to calling this method
        """
        pass

    @abstractmethod
    def get_attribute(self, session_key, attribute_key):
        """
        Returns the object bound to the associated session identified by the
        specified attribute key.  If there is no object bound under the
        attribute key for the given session, None is returned.
        
        raises InvalidSessionException if the specified session has stopped 
        or expired prior to calling this method
        """ 
        pass

    @abstractmethod
    def set_attribute(self, session_key, attribute_key, value):
        """
        Binds the specified value to the associated session uniquely identified
        by the attribute_key.  If there is already a session attribute
        bound under the attribute_key, that existing object will be
        replaced by the new value.
        
        If the value parameter is None, it has the same effect as if the
        remove_attribute(session_key, attribute_key) method was called.
        
        raises InvalidSessionException if the specified session has stopped or
        expired prior to calling this method
        """
        pass

    @abstractmethod
    def remove_attribute(self, session_key, attribute_key):
        """
        Removes (unbinds) the object bound to associated Session under 
        the given attribute_key

        raises InvalidSessionException if the specified session has stopped 
        or expired prior to calling this method
        """ 
        pass


class SessionContext(metaclass=ABCMeta):
    """
    A SessionContext is a 'bucket' of data presented to a SessionFactory, which 
    interprets its contents to construct Session instances.  It is essentially 
    a map of data with a few additional methods for easy retrieval of 
    objects commonly used to construct Subject instances.
    """
    
    @property
    @abstractmethod
    def host(self):
        """
        Returns the originating host name or IP address (as a String) from
        where the Subject is initiating the Session.

        :returns: the originating host name or IP address (as a String) from 
                  where the Subject is initiating the Session
        """ 
        pass

    @host.setter
    @abstractmethod
    def host(self, host):
        """
        Sets the originating host name or IP address (as a String) from where
        the Subject is initiating the Session.

        In web-based systems, this host can be inferred from the incoming 
        request, or in socket-based systems, it can be obtained via inspecting
        the socket initiator's host IP.

        Most secure environments *should* specify a valid, non-None host, 
        since knowing the host allows for more flexibility when securing a 
        system: by requiring an host, access control policies can also ensure 
        access is restricted to specific client *locations* in addition to 
        Subject principals, if so desired.

        Caveat - if clients to your system are on a public network (as would 
        be the case for a public web site), odds are high the clients can be
        behind a NAT (Network Address Translation) router or HTTP proxy server.
        If so, all clients accessing your system behind that router or proxy 
        will have the same originating host.  If your system is configured to 
        allow only one session per host, then the next request from a different 
        NAT or proxy client will fail and access will be denied for that client.  
        Just be aware that host-based security policies are best utilized 
        in LAN or private WAN environments when you can be ensure clients 
        will not share IPs or be behind such NAT routers or proxy servers.
     
        :param host: the originating host name or IP address (as a String) 
                     from where the Subject is initiating the Session
        """
        pass

    @property
    @abstractmethod
    def session_id(self):
        pass

    @session_id.setter
    @abstractmethod
    def session_id(self, session_id):
        pass


class SessionKey(metaclass=ABCMeta):

    @property
    @abstractmethod
    def session_id(self):
        pass

    @session_id.setter
    @abstractmethod
    def session_id(self, session_id):
        pass