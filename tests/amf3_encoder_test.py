# -*- coding: utf-8 -*-
import unittest

import amfast.encoder as encoder
import amfast.class_def as class_def

class Amf3EncoderTestCase(unittest.TestCase):
    class Spam(object):
        def __init__(self):
            self.spam = 'eggs'

    def setUp(self):
        self.class_mapper = class_def.ClassDefMapper()

    def testNull(self):
        buf = encoder.encode(None)
        self.assertEquals('\x01', buf)

    def testFalse(self):
        buf = encoder.encode(False)
        self.assertEquals('\x02', buf)

    def testTrue(self):
        buf = encoder.encode(True)
        self.assertEquals('\x03', buf)

    def testInt(self):
        tests = {
            0: '\x04\x00',
            0x35: '\x04\x35',
            0x7f: '\x04\x7f',
            0x80: '\x04\x81\x00',
            0xd4: '\x04\x81\x54',
            0x3fff: '\x04\xff\x7f',
            0x4000: '\x04\x81\x80\x00',
            0x1a53f: '\x04\x86\xca\x3f',
            0x1fffff: '\x04\xff\xff\x7f',
            0x200000: '\x04\x80\xc0\x80\x00',
            -0x01: '\x04\xff\xff\xff\xff',
            -0x2a: '\x04\xff\xff\xff\xd6',
            0xfffffff: '\x04\xbf\xff\xff\xff'
        }

        for integer, encoding in tests.iteritems():
            buf = encoder.encode(integer)
            self.assertEquals(encoding, buf)

    def testFloat(self):
        tests = {
            0.1: '\x05\x3f\xb9\x99\x99\x99\x99\x99\x9a',
            0.123456789: '\x05\x3f\xbf\x9a\xdd\x37\x39\x63\x5f'
        }

        for number, encoding in tests.iteritems():
            buf = encoder.encode(number)
            self.assertEquals(encoding, buf)

    def testLong(self):
        tests = {
            0x10000000: '\x05\x41\xb0\x00\x00\x00\x00\x00\x00',
            -0x10000001: '\x05\xc1\xb0\x00\x00\x01\x00\x00\x00',
            -0x10000000: '\x04\xc0\x80\x80\x00'
        }

        for number, encoding in tests.iteritems():
            buf = encoder.encode(number)
            self.assertEquals(encoding, buf)

    def testUnicode(self):
        tests = {
            u'': '\x06\x01',
            u'hello': '\x06\x0bhello',
            u'ᚠᛇᚻ': '\x06\x13\xe1\x9a\xa0\xe1\x9b\x87\xe1\x9a\xbb'
        }

        for string, encoding in tests.iteritems():
            buf = encoder.encode(string)
            self.assertEquals(encoding, buf)

    def testUnicodeRefs(self):
        hello = u'hello'
        test = [hello, hello, '', hello]

        result = '\x09\x09\x01' # array header
        result += '\x06\x0bhello' # array element 1 (hello encoded)
        result += '\x06\x00' #array element 2 (reference to hello)
        result += '\x06\x01' #array element 3 (empty string)
        result += '\x06\x00' #array element 4 (reference to hello)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testRefsOff(self):
        hello = u'hello'
        test = [hello, hello, '', hello]

        result = '\x09\x09\x01' # array header
        result += '\x06\x0bhello' # array element 1 (hello encoded)
        result += '\x06\x0bhello' #array element 2 (hello encoded)
        result += '\x06\x01' #array element 3 (empty string)
        result += '\x06\x0bhello' #array element 4 (hello encoded)

        buf = encoder.encode(test, use_references=False)
        self.assertEquals(result, buf)


    def testString(self):
        tests = {
            '': '\x06\x01',
            'hello': '\x06\x0bhello'
        }

        for string, encoding in tests.iteritems():
            buf = encoder.encode(string)
            self.assertEquals(encoding, buf)

    def testStringRefs(self):
        hello = 'hello'
        test = [hello, hello, '', hello]

        result = '\x09\x09\x01' # array header
        result += '\x06\x0bhello' # array element 1 (hello encoded)
        result += '\x06\x00' #array element 2 (reference to hello)
        result += '\x06\x01' #array element 3 (empty string)
        result += '\x06\x00' #array element 4 (reference to hello)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testTuple(self):
        test = (0, 1, 2, 3);

        result = '\x09\x09\x01' #array header
        result += '\x04\x00' #array element 1
        result += '\x04\x01' #array element 2
        result += '\x04\x02' #array element 3
        result += '\x04\x03' #array element 4

        buf = encoder.encode(test);
        self.assertEquals(result, buf);

    def testTupleRefs(self):
        test_tuple = (0, 1, 2, 3);
        test = [test_tuple, test_tuple]

        result = '\x09\x05\x01' # array header
        result += '\x09\x09\x01\x04\x00\x04\x01\x04\x02\x04\x03' # array element 1 (test_tuple encoded)
        result += '\x09\x02' # array element 2 (reference to test_tuple)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testTupleAsCollection(self):
        test = (0, 1, 2, 3);

        result = '\x0A\x07\x43flex.messaging.io.ArrayCollection' # Object header 
        result += '\x09\x09\x01' #array header
        result += '\x04\x00' #array element 1
        result += '\x04\x01' #array element 2
        result += '\x04\x02' #array element 3
        result += '\x04\x03' #array element 4

        buf = encoder.encode(test, use_array_collections=True)
        self.assertEquals(result, buf)

    def testArrayCollectionRef(self):
        test_tuple = (0, 1, 2, 3);
        test = [test_tuple, test_tuple]

        result = '\x0A\x07\x43flex.messaging.io.ArrayCollection\x09\x05\x01' # array header
        result += '\x0A\x01\x09\x09\x01\x04\x00\x04\x01\x04\x02\x04\x03' # array element 1 (test_tuple encoded)
        result += '\x0A\x04' # array element 2 (reference to test_tuple)

        buf = encoder.encode(test, use_array_collections=True)
        self.assertEquals(result, buf)

    def testList(self):
        test = [0, 1, 2, 3];

        result = '\x09\x09\x01' #array header
        result += '\x04\x00' #array element 1
        result += '\x04\x01' #array element 2
        result += '\x04\x02' #array element 3
        result += '\x04\x03' #array element 

        buf = encoder.encode(test); 
        self.assertEquals(result, buf);

    def testListRefs(self):
        test_list = [0, 1, 2, 3];
        test = (test_list, test_list)

        result = '\x09\x05\x01' # array header
        result += '\x09\x09\x01\x04\x00\x04\x01\x04\x02\x04\x03' # array element 1 (test_list encoded)
        result += '\x09\x02' # array element 2 (reference to test_list)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testListAsCollection(self):
        test = [0, 1, 2, 3];

        result = '\x0A\x07\x43flex.messaging.io.ArrayCollection' # Object header 
        result += '\x09\x09\x01' #array header
        result += '\x04\x00' #array element 1
        result += '\x04\x01' #array element 2
        result += '\x04\x02' #array element 3
        result += '\x04\x03' #array element 4

        buf = encoder.encode(test, use_array_collections=True);
        self.assertEquals(result, buf)

    def testDict(self):
        result = '\x0A\x0B\x01' # Object header
        result += '\x09spam' # key
        result += '\x06\x09eggs' #value
        result += '\x01' # empty string terminator

        buf = encoder.encode({'spam': 'eggs'})
        self.assertEquals(result, buf)

    def testDictRef(self):
        test_dict = {'spam': 'eggs'};
        test = (test_dict, test_dict)

        result = '\x09\x05\x01' #array header
        result += '\x0A\x0B\x01\x09spam\x06\x09eggs\x01' #array element 1 (test_dict encoded)
        result += '\x0A\x02' # array element 2 (reference to test_dict)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testDictAsObjectProxy(self):
        result = '\x0A\x07\x3Bflex.messaging.io.ObjectProxy' # Object header 
        result += '\x0A\x0B\x01' # Object header
        result += '\x09spam' # key
        result += '\x06\x09eggs' #value
        result += '\x01' # empty string terminator

        buf = encoder.encode({'spam': 'eggs'}, use_object_proxies=True)
        self.assertEquals(result, buf)

    def testObjectProxyRef(self):
        test_dict = {'spam': 'eggs'}
        test = (test_dict, test_dict)

        result = '\x09\x05\x01' #array header
        result += '\x0A\x07\x3Bflex.messaging.io.ObjectProxy\x0A\x0B\x01\x09spam\x06\x09eggs\x01' #array element 1 (test_dict encoded)
        result += '\x0A\x02' # array element 2 (reference to test_dict)

        buf = encoder.encode(test, use_object_proxies=True)
        self.assertEquals(result, buf)

    def testDictBadKeyRaisesError(self):
        self.assertRaises(encoder.EncodeError, encoder.encode, {1: 'fail'})

    def testDate(self):
        import datetime

        test = datetime.datetime(2005, 3, 18, 1, 58, 31)
        buf = encoder.encode(test)
        self.assertEquals('\x08\x01Bp+6!\x15\x80\x00', buf)

        test = datetime.date(2003, 12, 1)
        buf = encoder.encode(test)
        self.assertEquals('\x08\x01Bo%\xe2\xb2\x80\x00\x00', buf)

    def testDateReferences(self):
        import datetime

        test_date = datetime.datetime(2005, 3, 18, 1, 58, 31)
        test = [test_date, test_date]

        result = '\x09\x05\x01' #array header
        result += '\x08\x01Bp+6!\x15\x80\x00' #array element 1 (test_date encoded)
        result += '\x08\x02' # array element 2 (reference to test_date)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testXml(self):
        import xml.dom.minidom

        document = """
           <test>
            <test_me>tester</test_me>
           </test>
        """

        result = '\x0B' # XML header
        result += '\x81\x2B' # String header
        result += '<?xml version="1.0" ?><test>\n            <test_me>tester</test_me>\n           </test>' # encoded XML

        dom = xml.dom.minidom.parseString(document)
        buf = encoder.encode(dom)
        self.assertEquals(result, buf)

    def testXmlRef(self):
        import xml.dom.minidom

        document = """
           <test>
            <test_me>tester</test_me>
           </test>
        """

        dom = xml.dom.minidom.parseString(document)
        test = [dom, dom]

        result = '\x09\x05\x01' #array header
        result += '\x0B\x81\x2B<?xml version="1.0" ?><test>\n            <test_me>tester</test_me>\n           </test>' # array element 1 (encoded dom)
        result += '\x0B\x02' # array element 2 (reference to dom)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testLegacyXml(self):
        import xml.dom.minidom

        document = """
           <test>
            <test_me>tester</test_me>
           </test>
        """

        result = '\x07' # XML header
        result += '\x81\x2B' # String header
        result += '<?xml version="1.0" ?><test>\n            <test_me>tester</test_me>\n           </test>' # encoded XML

        dom = xml.dom.minidom.parseString(document)
        buf = encoder.encode(dom, use_legacy_xml=True)
        self.assertEquals(result, buf)

    def testAnonObj(self):
        test = self.Spam()

        result = '\x0A\x0B\x01' # Object header
        result += '\x09spam' # key
        result += '\x06\x09eggs' #value
        result += '\x01' # empty string terminator

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testAnonObjRef(self):
        test_obj = self.Spam()
        test = (test_obj, test_obj)

        result = '\x09\x05\x01' #array header
        result += '\x0A\x0B\x01\x09spam\x06\x09eggs\x01' #array element 1 (test_obj encoded)
        result += '\x0A\x02' # array element 2 (reference to test_obj)

        buf = encoder.encode(test)
        self.assertEquals(result, buf)

    def testStaticObj(self):
        self.class_mapper.mapClass(class_def.ClassDef(self.Spam, 'alias.spam', ('spam',)))
        test = self.Spam()

        result = '\x0A\x13\x15alias.spam'
        result += '\x09spam' # static attr definition
        result += '\x06\x09eggs' # static attrs

        buf = encoder.encode(test, class_def_mapper=self.class_mapper)
        self.class_mapper.unmapClass(self.Spam)

        self.assertEquals(result, buf)

    def testClassRef(self):
        self.class_mapper.mapClass(class_def.ClassDef(self.Spam, 'alias.spam', ('spam',)))
        test_obj_1 = self.Spam()
        test_obj_2 = self.Spam()
        test_obj_2.spam = 'foo'
        test = (test_obj_1, test_obj_2)

        result = '\x09\x05\x01' #array header
        result += '\x0A\x13\x15alias.spam\x09spam\x06\x09eggs' # array element 1
        result += '\x0A\x01\x06\x07foo' # array element 2

        buf = encoder.encode(test, class_def_mapper=self.class_mapper)
        self.class_mapper.unmapClass(self.Spam)

        self.assertEquals(result, buf)

    def testTypedObjectRef(self):
        self.class_mapper.mapClass(class_def.ClassDef(self.Spam, 'alias.spam', ('spam',)))
        test_obj = self.Spam()
        test = (test_obj, test_obj)

        result = '\x09\x05\x01' #array header
        result += '\x0A\x13\x15alias.spam\x09spam\x06\x09eggs' # test_obj_encoded
        result += '\x0A\x02' # array element 2 (reference to test_obj)

        buf = encoder.encode(test, class_def_mapper=self.class_mapper)
        self.class_mapper.unmapClass(self.Spam)

        self.assertEquals(result, buf)

    def testDynamicObj(self):
        self.class_mapper.mapClass(class_def.DynamicClassDef(self.Spam, 'alias.spam', ()))
        test = self.Spam()
        
        result = '\x0A\x0B\x15alias.spam'
        result += '\x09spam\x06\x09eggs\x01' # dynamic attrs

        buf = encoder.encode(test, class_def_mapper=self.class_mapper)
        self.class_mapper.unmapClass(self.Spam)

        self.assertEquals(result, buf)

    def testStaticDynamicObj(self):
        self.class_mapper.mapClass(class_def.DynamicClassDef(self.Spam, 'alias.spam', ('spam',)))
        test = self.Spam()
        test.ham = 'foo'

        result = '\x0A\x1B\x15alias.spam' # obj header
        result += '\x09spam' # static attr definition
        result += '\x06\x09eggs' # static attrs
        result += '\x07ham\x06\x07foo\x01' #dynamic attrs

        buf = encoder.encode(test, class_def_mapper=self.class_mapper)
        self.class_mapper.unmapClass(self.Spam)

        self.assertEquals(result, buf)

    def testExternizeable(self):
        custom_encoding = '\x01\x02\x03\x04\x05'

        class ExternClass(class_def.ExternizeableClassDef):
            def writeByteString(self, obj):
                return custom_encoding

        self.class_mapper.mapClass(ExternClass(self.Spam, 'alias.spam', ('spam',)))
        test = self.Spam()

        result = '\x0A\x07\x15alias.spam'
        result += custom_encoding # raw bytes

        buf = encoder.encode(test, class_def_mapper=self.class_mapper)
        self.class_mapper.unmapClass(self.Spam)

        self.assertEquals(result, buf)


    def testUnknownRaisesError(self):
       import sets
       self.assertRaises(class_def.ClassDefError, encoder.encode, sets.Set())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(Amf3EncoderTestCase)

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
