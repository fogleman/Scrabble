import struct

SENTINEL = '$'

class Trie(object):
    def __init__(self, letter):
        self.letter = letter
        self.children = {}
    def __iter__(self):
        yield self
        for key in sorted(self.children):
            child = self.children[key]
            for node in child:
                yield node
    def add(self, word):
        word = '%s%s' % (word, SENTINEL)
        node = self
        for letter in word:
            if letter in node.children:
                child = node.children[letter]
            else:
                child = Trie(letter)
                node.children[letter] = child
            node = child

class Markov(object):
    def __init__(self, order=1):
        self.order = order
        self.table = {}
    def add(self, word):
        word = '%s%s' % (word, SENTINEL)
        previous = []
        for letter in word:
            key = tuple(previous)
            states = self.table.setdefault(key, {})
            states[letter] = states.get(letter, 0) + 1
            previous.append(letter)
            if len(previous) > self.order:
                del previous[0]

class Record(object):
    def __init__(self, more, letter, frequency, link):
        self.more = more
        self.letter = letter
        self.frequency = frequency
        self.link = link
    @property
    def key(self):
        return (self.letter, self.frequency, self.link)

class Group(object):
    def __init__(self, records):
        if len(records) == 1 and records[0].frequency != 0:
            records[0].frequency = 1
        self.records = records
    @property
    def key(self):
        return tuple(record.key for record in self.records)

def load_object(obj, path, reverse):
    with open(path) as fp:
        for line in fp:
            word = line.strip().lower()
            if reverse:
                word = ''.join(reversed(word))
            obj.add(word)
    return obj

def load_trie(path, reverse):
    print 'Constructing trie...'
    obj = Trie(None)
    return load_object(obj, path, reverse)

def load_markov(path, order, reverse):
    print 'Constructing Markov chain...'
    obj = Markov(order)
    return load_object(obj, path, reverse)

def trie_to_records(trie):
    print 'Converting trie to record table...'
    nodes = list(trie)
    index = 0
    node_index = {}
    for node in nodes:
        node_index[node] = index
        index += len(node.children)
    records = []
    for node in nodes:
        count = len(node.children)
        for i, letter in enumerate(sorted(node.children)):
            more = int(i < count - 1)
            if letter == SENTINEL:
                link = 0
            else:
                link = node_index[node.children[letter]]
            record = Record(more, letter, 0, link)
            records.append(record)
    return records

def markov_to_records(chain):
    print 'Converting Markov chain to record table...'
    table = chain.table
    order = chain.order
    # determine key indexes
    index = 0
    key_index = {}
    for key in sorted(table):
        key_index[key] = index
        index += len(table[key])
    # generate records
    records = []
    for key in sorted(table):
        frequencies = table[key]
        count = len(frequencies)
        for i, letter in enumerate(sorted(frequencies)):
            more = int(i < count - 1)
            frequency = min(frequencies[letter], 0xffff)
            if letter == SENTINEL:
                link = 0
            else:
                next_key = list(key)
                next_key.append(letter)
                if len(next_key) > order:
                    del next_key[0]
                next_key = tuple(next_key)
                link = key_index[next_key]
            record = Record(more, letter, frequency, link)
            records.append(record)
    return records

def group_records(records):
    groups = []
    group = []
    for record in records:
        group.append(record)
        if not record.more:
            group = Group(group)
            groups.append(group)
            group = []
    return groups

def compress_groups(groups):
    # track prior links
    link_key = {}
    index = 0
    for group in groups:
        link_key[index] = group.key
        index += len(group.records)
    # find duplicates
    key_link = {}
    index = 0
    seen = set()
    new_groups = []
    for group in groups:
        key = group.key
        if key in seen:
            continue
        seen.add(key)
        new_groups.append(group)
        key_link[key] = index
        index += len(group.records)
    # update links
    for group in new_groups:
        for record in group.records:
            if record.link == 0:
                continue
            key = link_key[record.link]
            record.link = key_link[key]
    return new_groups

def compress_records(records):
    print 'Eliminating duplicate record groups...'
    groups = group_records(records)
    previous = 0
    while len(groups) != previous:
        previous = len(groups)
        groups = compress_groups(groups)
        print '%d groups -> %d groups' % (previous, len(groups))
    result = []
    for group in groups:
        result.extend(group.records)
    return result

def write_dawg(path, records):
    print 'Writing to disk...'
    blocks = []
    for record in records:
        x = record.link
        x |= ord(record.letter) << 24
        x |= record.more << 31
        block = struct.pack('<I', x)
        blocks.append(block)
    data = ''.join(blocks)
    with open(path, 'wb') as fp:
        fp.write(data)

def write_markov(path, records):
    print 'Writing to disk...'
    blocks = []
    for record in records:
        block = struct.pack('<bcHI', record.more, record.letter, record.frequency, record.link)
        blocks.append(block)
    data = ''.join(blocks)
    with open(path, 'wb') as fp:
        fp.write(data)

def generate_dawg_file(infile, outfile, reverse=False):
    print '"%s" -> "%s"' % (infile, outfile)
    trie = load_trie(infile, reverse)
    records = trie_to_records(trie)
    records = compress_records(records)
    write_dawg(outfile, records)
    print 'Done!'

def generate_markov_file(infile, outfile, order, reverse=False):
    print '"%s" -> "%s"' % (infile, outfile)
    markov = load_markov(infile, order, reverse)
    records = markov_to_records(markov)
    records = compress_records(records)
    write_markov(outfile, records)
    print 'Done!'

if __name__ == '__main__':
    generate_dawg_file('TWL06.txt', 'twl.dawg')
