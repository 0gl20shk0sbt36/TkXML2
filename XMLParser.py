from queue import Queue
from threading import Thread
from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import make_parser


# class ParserBaseClass(ContentHandler):
#
#     def setDocumentLocator(self, locator):
#         super().setDocumentLocator(locator)
#
#     def startDocument(self):
#         super().startDocument()
#
#     def endDocument(self):
#         super().endDocument()
#
#     def startPrefixMapping(self, prefix, uri):
#         super().startPrefixMapping(prefix, uri)
#
#     def endPrefixMapping(self, prefix):
#         super().endPrefixMapping(prefix)
#
#     def startElement(self, name, attrs):
#         super().startElement(name, attrs)
#
#     def endElement(self, name):
#         super().endElement(name)
#
#     def startElementNS(self, name, qname, attrs):
#         super().startElementNS(name, qname, attrs)
#
#     def endElementNS(self, name, qname):
#         super().endElementNS(name, qname)
#
#     def characters(self, content):
#         super().characters(content)
#
#     def ignorableWhitespace(self, whitespace):
#         super().ignorableWhitespace(whitespace)
#
#     def processingInstruction(self, target, data):
#         super().processingInstruction(target, data)
#
#     def skippedEntity(self, name):
#         super().skippedEntity(name)


class ParserBaseClass(ContentHandler):

    def __init__(self):
        super().__init__()
        self.xml_path = []
        self.queue = Queue()

    def setDocumentLocator(self, locator):
        super().__init__()
        print(locator)

    def startDocument(self):
        print('startDocument')

    def endDocument(self):
        print('endDocument')

    def startPrefixMapping(self, prefix, uri):
        print('startPrefixMapping', (prefix, uri))

    def endPrefixMapping(self, prefix):
        print('endPrefixMapping', prefix)

    def startElement(self, tag, attributes):
        self.xml_path.append(tag)
        # self.queue.put(('start', self.xml_path[1:], attributes))
        print('startElement', ('start', self.xml_path, attributes))

    def endElement(self, tag):
        # self.queue.put(('end', self.xml_path[1:]))
        print('endElement', ('end', self.xml_path))
        self.xml_path.pop()

    def startElementNS(self, name, qname, attrs):
        print('startElementNS', (name, qname, attrs))

    def endElementNS(self, name, qname):
        print('endElementNS', (name, qname))

    def characters(self, content):
        print('characters', ('content', self.xml_path[1:], content))
        # self.queue.put(('content', self.xml_path[1:], content))

    def ignorableWhitespace(self, whitespace):
        print('ignorableWhitespace', whitespace)

    def processingInstruction(self, target, data):
        print('processingInstruction', (target, data))

    def skippedEntity(self, name):
        print('skippedEntity', name)


def main1():
    path = '1.xml'
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    parser_class = ParserBaseClass()
    parser.setContentHandler(parser_class)
    parser.parse(path)
    # Thread(target=parser.parse, args=(path,), daemon=True).start()


class XMLFormatError(BaseException):

    def __init__(self, error, file, row=None, columns=None):
        self.error = error
        self.file = file
        self.row = row
        if row is None:
            self.columns = None
        else:
            self.columns = columns

    def __str__(self):
        error_message = f'''
error message: {self.error}
error file: {self.file}'''
        if self.row is None:
            return error_message
        elif self.columns is None:
            error_message += f'''
error row: {self.row}'''
        else:
            error_message += f'''
error columns: {self.columns}'''
        if self.row is not None:
            with open(self.file) as f:
                for i in range(self.row):
                    n = f.readline()
            error_message += '''
Traceback file:
''' + n


class ParserXML:
    def __init__(self, path):
        self.path = path
        self.file = open(path)

    def __iter__(self):
        self.row = 1
        self.columns = 0
        self.start_angle_brackets = False
        self.string = []
        return self

    def __next__(self):
        string = ''
        while True:
            n = self.file.read(1)
            if not n:
                raise StopIteration
            if n == '<' and self.string:
                string = ''.join(self.string)
                self.string = ['<']
                self.start_angle_brackets = True
                break
            if n == '>' and self.string:
                if not self.start_angle_brackets:
                    raise XMLFormatError('Angle brackets are not paired', self.file, self.row)
                self.string.append('>')
                string = ''.join(self.string)
                self.string = []
                break
            if n == '\n':
                self.columns += 1
                self.row = 0
                continue
            self.string.append(n)
            self.row += 1
        if not string and self.row == 1:
            raise
        return string


def main2():
    f = ParserXML('1.xml')
    # f = open('1.xml')
    for i in f:
        # pass
        print(i)
    # while True:
    #     print(f.read(1), end='')


if __name__ == '__main__':
    main2()
