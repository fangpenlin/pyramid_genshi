from __future__ import unicode_literals
import unittest


from pyramid_genshi import TranslationStringAdaptor


class TestTranslationStringAdaptor(unittest.TestCase):
    def make_one(self, *args, **kwargs):
        return TranslationStringAdaptor(*args, **kwargs)

    def test_ugettext(self):
        translate_calls = []

        def mock_translate(ts):
            translate_calls.append(ts)

        adaptor = self.make_one(
            mock_translate,
            default_domain='MOCK_DEFAULT_DOMAIN',
        )
        adaptor.ugettext('hello baby')

        self.assertEqual(len(translate_calls), 1)
        ts = translate_calls[0]
        self.assertEqual(ts.domain, 'MOCK_DEFAULT_DOMAIN')

    def test_ugettext_with_domain(self):
        translate_calls = []

        def mock_translate(ts):
            translate_calls.append(ts)

        adaptor = self.make_one(mock_translate)
        adaptor.ugettext('hello baby', domain='MOCK_DOMAIN')

        self.assertEqual(len(translate_calls), 1)
        ts = translate_calls[0]
        self.assertEqual(ts.domain, 'MOCK_DOMAIN')

    def test_dugettext_with_domain(self):
        translate_calls = []

        def mock_translate(ts):
            translate_calls.append(ts)

        adaptor = self.make_one(mock_translate)
        adaptor.dugettext('MOCK_DOMAIN', 'hello baby')

        self.assertEqual(len(translate_calls), 1)
        ts = translate_calls[0]
        self.assertEqual(ts.domain, 'MOCK_DOMAIN')

    def test_ungettext(self):
        pluralize_calls = []

        def mock_pluralize(msgid1, msgid2, n, domain):
            pluralize_calls.append((msgid1, msgid2, n, domain))

        adaptor = self.make_one(lambda ts: ts, 
                                pluralize=mock_pluralize, 
                                default_domain='MOCK_DEFAULT_DOMAIN')
        adaptor.ungettext('hello one baby', 'hello many babies', 5566)

        self.assertEqual(len(pluralize_calls), 1)
        msgid1, msgid2, n, domain = pluralize_calls[0]
        self.assertEqual(msgid1, 'hello one baby')
        self.assertEqual(msgid2, 'hello many babies')
        self.assertEqual(n, 5566)
        self.assertEqual(domain, 'MOCK_DEFAULT_DOMAIN')

    def test_ungettext_without_pluralize(self):
        adaptor = self.make_one(lambda ts: ts, 
                                default_domain='MOCK_DEFAULT_DOMAIN')
        ts = adaptor.ungettext('hello one baby', 'hello many babies', 5566)
        self.assertEqual(ts, 'hello many babies')
        ts = adaptor.ungettext('hello one baby', 'hello many babies', 1)
        self.assertEqual(ts, 'hello one baby')

    def test_dungettext(self):
        pluralize_calls = []

        def mock_pluralize(msgid1, msgid2, n, domain):
            pluralize_calls.append((msgid1, msgid2, n, domain))

        adaptor = self.make_one(lambda ts: ts, 
                                pluralize=mock_pluralize)
        adaptor.dungettext(
            'MOCK_DOMAIN',
            'hello one baby',
            'hello many babies',
            5566,
        )

        self.assertEqual(len(pluralize_calls), 1)
        msgid1, msgid2, n, domain = pluralize_calls[0]
        self.assertEqual(msgid1, 'hello one baby')
        self.assertEqual(msgid2, 'hello many babies')
        self.assertEqual(n, 5566)
        self.assertEqual(domain, 'MOCK_DOMAIN')
