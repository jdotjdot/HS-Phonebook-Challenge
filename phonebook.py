#!/usr/bin/env python

import re, os, csv, argparse

# have to stick in a context manager to make sure it saves on exit

# for reverse-lookup, implement a tree node search by number?

class Phonebook(object):
    """Usage: with Phonebook(filename) as pb:

    Phonebook object
    """

    def __init__(self, filename):
        self.filename = filename
        self._phonebook = {}

    def __enter__(self):
        self._load_pb()
        return self

    def __exit__(self, type, value, traceback):
        # is it efficient to save on every exit?
        self.__save_pb()

    #### Loading and saving

    def __file_exists(self):
        return os.path.isfile(self.filename)

    def _create_pb(self):
        if self.__file_exists():
            raise Exception, "Phonebook {} already exists.".format(self.filename)
        else:
            # touch the file
            with open(self.filename, 'w'):
                pass
            print "created phonebook {} in the current directory".format(self.filename)

    def _load_pb(self):
        if os.path.isfile(self.filename):

            with open(self.filename, 'r') as inputfile:
                reader = csv.reader(inputfile)
                for key, value in reader: # each row just has key/value
                    self._phonebook[key] = value

        else:
            raise Exception, "No such phonebook exists."

    def __save_pb(self):
        with open(self.filename, 'w') as outputfile:
            writer = csv.writer(outputfile)
            for item in self._phonebook.iteritems():
                writer.writerow(item)

    #### Functionality

    def number_parse(self, number):
        number = re.sub(r'[\.\-\(\) \+]', '', number)

        if number[0] == '1':
            number = number[1:]

        if not re.match(r'^\d{10}$', number):
            raise TypeError, "Phone number {} is not of the correct length.".format(number)
        else:
            return ' '.join((number[:3], number[3:6], number[6:]))

    def name_sanitize(self, name):
        return name.strip()

    def exists(self, name):
        # Case-sensitive
        return self.name_sanitize(name) in self._phonebook

    def __fuzzy_name_lookup(self, name):
        # Not case sensitive
        ret = []
        name = self.name_sanitize(name)
        for key, value in self._phonebook.iteritems():
            if name.strip().lower() in key.lower():
                ret.append((key, value))

        return ret

    # def __number_lookup(self, number):
    #     pass

    def __item_add(self, name, number):
        self._phonebook[name] = self.number_parse(number)

    def __item_delete(self, name):
        del self._phonebook[name]

    ### Publicly available functions

    def lookup(self, name):
        ret = self.__fuzzy_name_lookup(name)
        print '\n'.join(' '.join(item) for item in ret)

    def add(self, name, number):
        name = self.name_sanitize(name)
        if self.exists(name):
            raise KeyError, "The name \"{}\" already exists in your phonebook! ".format(name) + \
                "Please use the 'change' argument to change his/her information."
        else:
            self.__item_add(name, number)

    def change(self, name, number):
        name = self.name_sanitize(name)
        if not self.exists(name):
            raise KeyError, "The name \"{}\" does not exist in your phonebook.".format(name)
        else:
            self.__item_add(name, number)

    def remove(self, name):
        name = self.name_sanitize(name)
        if not self.exists(name):
            raise KeyError, "The name \"{}\" already does not exist in your phonebook.".format(name)
        else:
            self.__item_delete(name)

    def reverse_lookup(self, number):
        number = self.number_parse(number)
        found = 0
        # is this inefficient?
        for name, pb_telephone in self._phonebook.iteritems():
            # Returns all names if same number attached to multiple contacts
            if number == pb_telephone:
                print name
                found += 1

        if not found:
            raise KeyError, "The number \"{}\" does not appear in your phonebook.".format(number)

    def create(self):
        # pb = Phonebook(filename)
        self._create_pb()


# >>> Phonebook.check_i_numbers

# argparse: make all - to _

def getargs():
    parser = argparse.ArgumentParser(description="Create or manipulate a Phonebook")

    parser.add_argument('function', action='store', nargs="+",)
                        # choices=['create', 'lookup', 'add', 'change', 'remove', 'reverse-lookup'])
    parser.add_argument('-b', action="store", dest="phonebook")

    args = parser.parse_args()


    if args.function[0] == 'create':
        Phonebook(args.function[1]).create()
    elif not args.phonebook:
        parser.error("-b <phonebook> must be provided unless using 'create' command")
    else:
        with Phonebook(args.phonebook) as pb:
            getattr(pb, args.function[0].replace('-', '_'))(*args.function[1:])

def main():
    getargs()

if __name__ == '__main__':
    main()

