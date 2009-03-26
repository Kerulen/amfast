import models
from persistent import Schema

class SAObject(object):
    """Handles common operations for persistent objects."""
    def getClassDefByAlias(self, alias):
        return self.gateway.class_def_mapper.getClassDefByAlias(alias)

    def load(self, class_alias, key):
        class_def = self.getClassDefByAlias(class_alias)
        session = Schema().session
        return session.query(class_def.class_).get(key)

    def loadAll(self, class_alias):
        class_def = self.getClassDefByAlias(class_alias)
        session = Schema().session
        return session.query(class_def.class_).all()

    def loadAttr(self, class_alias, key, attr):
        obj = self.load(class_alias, key)
        return getattr(obj, attr)

    def save(self, obj):
        session = Schema().session
        merged_obj = session.merge(obj)
        session.commit()

    def saveList(self, objs):
        for obj in objs:
            self.save(obj)

    def remove(self, class_alias, key):
        class_def = self.getClassDefByAlias(class_alias)
        session = Schema().session
        obj = session.query(class_def.class_).get(key)
        session.delete(obj)
        session.commit()

    def removeList(self, class_alias, keys):
        for key in keys:
            self.remove(class_alias, key)

    def insertDefaultData(self):
        user = models.User()
        user.first_name = 'Bill'
        user.last_name = 'Lumbergh'
        for label, email in {'personal': 'bill@yahoo.com', 'work': 'bill@initech.com'}.iteritems():
            email_obj = models.Email()
            email_obj.label = label
            email_obj.email = email
            user.emails.append(email_obj)

        for label, number in {'personal': '1-800-555-5555', 'work': '1-555-555-5555'}.iteritems():
            phone_obj = models.PhoneNumber()
            phone_obj.label = label
            phone_obj.number = number
            user.phone_numbers.append(phone_obj)

        session = Schema().session
        session.add(user)
        session.commit()

    def raiseException(self):
        raise Exception("Example Exception")

    def echo(self, val):
        """Return what was sent to the client."""
        return val