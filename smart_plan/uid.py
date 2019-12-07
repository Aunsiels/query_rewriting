class UID(object):

    def __init__(self, body, head):
        self.body = body
        self.head = head

    def get_body(self):
        return self.body

    def get_head(self):
        return self.head

    def __hash__(self):
        return hash(self.body) + hash(self.head)

    def __eq__(self, other):
        return isinstance(other, UID) and other.get_body() == self.get_body() and other.get_head() == self.get_head()

    def __str__(self):
        return str(self.body) + " -> " + str(self.head)