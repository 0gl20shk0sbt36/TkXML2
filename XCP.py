from queue import Queue
from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import make_parser
from threading import Thread


def getattr_all(_o, names):
    if isinstance(names, str):
        names = [names]
    if not names:
        return _o
    return getattr_all(getattr(_o, names[0]), names[1:])


class ParserBaseClass(ContentHandler):

    def __init__(self):
        super().__init__()
        self.xml_path = []
        self.queue = Queue()

    def startElement(self, tag, attributes):
        if tag in ['startElement', 'endElement', 'characters']:
            raise SyntaxError('invalid syntax')
        self.xml_path.append(tag)
        self.queue.put(('start', self.xml_path[1:], attributes))

    def endElement(self, tag):
        self.queue.put(('end', self.xml_path[1:]))
        self.xml_path.pop()

    def characters(self, content):
        self.queue.put(('content', self.xml_path[1:], content))


class AllocationIterator:

    def __init__(self, queue, path):
        self.queue = queue
        self.path_num = len(path)
        self.end = False
        self.del_ = False

    def __del__(self):
        self.del_ = True
        if not self.end:
            while not self.end:
                self.__next__()

    def __iter__(self):
        self.path = []
        self.argv = []
        self.content = []
        return self

    def __next__(self):
        while True:
            n = self.queue.get()
            if n[0] == 'start':
                self.path.append(n[1][-1])
                self.argv.append(n[2])
                self.content.append('')
            elif n[0] == 'content':
                if len(n[1][self.path_num:]):
                    self.content[len(n[1][self.path_num:]) - 1] += n[2]
            elif n[0] == 'end':
                if len(self.path):
                    path = self.path.copy()
                    self.path.pop()
                    return path, self.argv.pop(), self.content.pop()
                self.end = True
                if self.del_:
                    return
                raise StopIteration


class CallTag:

    def __init__(self, obj, path, args):
        self.obj = obj
        self.path = path
        self.args = args
        self.content = ''

    def __call__(self, not_content=False):
        if not_content:
            return self.obj([self.path, self.args, None])
        else:
            return self.obj([self.path, self.args, self.content])

    def callable(self):
        return callable(self.obj)

    def content_add(self, content):
        self.content += content


class Allocation:

    def __init__(self, obj=None, queue: Queue = None):
        self.queue: Queue = queue
        if obj is None:
            self.obj = self
        else:
            self.obj = obj

    def bind_class(self, obg):
        self.obj = obg

    def bind_queue(self, queue: Queue):
        self.queue: Queue = queue

    def main(self):
        tag = []
        call = []
        while True:
            n = self.queue.get()
            if n[0] == 'start':
                if not n[1]:
                    if n[2]['versions'] != '1.0':
                        raise
                obj = getattr_all(self.obj, n[1])
                if call and call[-1]:
                    tag[-1](True)
                    call[-1] = False
                if n[1] in self.obj.__dict__.get('__yield__', []):
                    obj([n[1], n[2], None], AllocationIterator(self.queue, n[1]))
                else:
                    if n[1]:
                        tag.append(CallTag(obj, n[1], n[2]))
                        call.append(tag[-1].callable())
            elif n[0] == 'content':
                if n[1]:
                    tag[-1].content_add(n[2])
                    # tag[len(n[1]) - 1].content_add(n[2])
            elif n[0] == 'end':
                if not n[1]:
                    break
                elif call[-1]:
                    tag.pop()()
                else:
                    tag.pop()
                call.pop()


def syntax_check(file, obj):


class XCP:

    def __init__(self, bind_class):
        self.parser = make_parser()
        self.parser.setFeature(feature_namespaces, 0)
        self.parser_class = ParserBaseClass()
        self.allocation = Allocation(bind_class, self.parser_class.queue)
        self.parser.setContentHandler(self.parser_class)

    def run(self, path):
        Thread(target=self.parser.parse, args=(path,), daemon=True).start()
        self.allocation.main()

