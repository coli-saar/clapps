
class User():
    def __init__(self, id, name, passwd):
        self.id = id
        self.name = name
        self.passwd = passwd

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


    def __str__(self):
        return "%s: %s (pw %s)" % (self.id, self.name, self.passwd)