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

    def get_xml_dependency(self):
        from smart_plan.utils import get_inverse_relation
        xml = '<dependency>\n<body>\n'
        if self.body[-1] == '-':
            relation = get_inverse_relation(self.body)
            xml += '<atom name="' + relation + '">\n'
            xml += '<variable name="y" />\n'
            xml += '<variable name="x" />\n'
        else:
            relation = self.body
            xml += '<atom name="' + relation + '">\n'
            xml += '<variable name="x" />\n'
            xml += '<variable name="y" />\n'
        xml += '</atom>\n</body>\n<head>\n'
        if self.head[-1] == '-':
            relation = get_inverse_relation(self.head)
            xml += '<atom name="' + relation + '">\n'
            xml += '<variable name="z" />\n'
            xml += '<variable name="x" />\n'
        else:
            relation = self.head
            xml += '<atom name="' + relation + '">\n'
            xml += '<variable name="x" />\n'
            xml += '<variable name="z" />\n'
        xml += '</atom>\n</head>\n</dependency>\n'
        return xml