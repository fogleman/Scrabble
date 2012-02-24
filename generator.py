import struct

def load_dawg(path):
    with open(path, 'rb') as fp:
        data = fp.read()
    groups = {}
    start = 0
    lookup = {}
    for index in xrange(len(data) / 4):
        block = data[index * 4:index * 4 + 4]
        x = struct.unpack('<I', block)[0]
        link = x & 0xffffff
        letter = chr((x >> 24) & 0x7f)
        more = bool((x >> 31) & 1)
        lookup[letter] = link
        if not more:
            groups[start] = lookup
            start = index + 1
            lookup = {}
    for lookup in groups.itervalues():
        for letter, link in lookup.iteritems():
            lookup[letter] = groups[link] if link else None
    return groups[0]

def check_dawg(dawg, word):
    word = '%s$' % word.lower()
    node = dawg
    for letter in word:
        if letter in node:
            node = node[letter]
        else:
            return False
    return True

if __name__ == '__main__':
    dawg = load_dawg('files/twl.dawg')
