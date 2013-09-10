import unittest

from flexmock import flexmock


class DummyLookup(object):
    auto_reload = True
    debug = True

    def translate(self, msg):
        return msg


class TestGenshiTemplateRenderer(unittest.TestCase):
    def setUp(self):
        from pyramid.testing import setUp
        from pyramid.registry import Registry
        registry = Registry()
        self.config = setUp(registry=registry)

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()
        
    def _get_template_path(self, name):
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(here, 'fixtures', name)
        
    def make_one(self, *arg, **kw):
        from pyramid_genshi import GenshiTemplateRenderer
        return GenshiTemplateRenderer(*arg, **kw)
    
    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import ITemplateRenderer
        path = self._get_template_path('minimal.genshi')
        lookup = DummyLookup()
        verifyObject(ITemplateRenderer, self.make_one(path, lookup))
    
    def test_render(self):
        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        result = renderer({}, {})
        self.assertEqual(result, 
                         '<div>\n</div>')
        
    def test_render_method(self):
        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        
        def test_method(method, expected):
            from pyramid.threadlocal import get_current_registry
            reg = get_current_registry()
            reg.settings['genshi.method'] = method
            renderer = self.make_one(path, lookup)
            result = renderer({}, {})
            self.assertEqual(result, expected)
            
        test_method(
            'xml', 
            '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'
        )
        test_method(
            'xhtml', 
            '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>'
        )
        test_method(
            'text', 
            '\n'
        )
        
        def test_format(method, expected):
            from pyramid.threadlocal import get_current_registry
            reg = get_current_registry()
            reg.settings['genshi.default_format'] = method
            renderer = self.make_one(path, lookup)
            result = renderer({}, {})
            self.assertEqual(result, expected)
            
        test_format('xml', 
                    '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        test_format('xhtml', 
                    '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        test_format('text', 
                    '\n')
        
    def test_render_doctype(self):
        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        
        def test_doctype(doctype, expected):
            from pyramid.threadlocal import get_current_registry
            reg = get_current_registry()
            reg.settings['genshi.default_doctype'] = doctype
            renderer = self.make_one(path, lookup)
            result = renderer({}, {})
            self.assertEqual(result, expected)
            
        test_doctype(
            'html5', 
            '<!DOCTYPE html>\n<div>\n</div>'
        )
        test_doctype(
            'xhtml', 
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
            ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
            '<div>\n</div>'
        )
        
    def test_render_encoding(self):
        lookup = DummyLookup()
        path = self._get_template_path('chinese.genshi')
        
        def test_encoding(encoding, expected):
            from pyramid.threadlocal import get_current_registry
            reg = get_current_registry()
            reg.settings['genshi.default_encoding'] = encoding
            renderer = self.make_one(path, lookup)
            result = renderer({}, {})
            self.assertEqual(result, expected)
            
        test_encoding('utf8', 
                      '<div>\n\xe4\xb8\xad\xe6\x96\x87\xe5\xad\x97\n</div>')
        test_encoding('cp950', 
                      '<div>\n\xa4\xa4\xa4\xe5\xa6r\n</div>')
        
    def test_i18n_msg(self):
        lookup = DummyLookup()

        def translate(msg):
            if msg == 'Hello':
                return 'Hola'
            return msg

        lookup.translate = translate
        path = self._get_template_path('i18n_msg.genshi')
        renderer = self.make_one(path, lookup)
        result = renderer({}, {})
        self.assertEqual(result, 
                         '<div>Hola World</div>')
        
    def test_default_domain(self):
        from pyramid.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.settings['genshi.default_domain'] = 'test_domain'
        lookup = DummyLookup()
        translate_calls = []

        def translate(msg):
            translate_calls.append(msg)
            return msg

        lookup.translate = translate
        
        path = self._get_template_path('i18n_msg.genshi')
        renderer = self.make_one(path, lookup)
        renderer({}, {})
        self.assertEqual(len(translate_calls), 2)
        ts1 = translate_calls[0]
        ts2 = translate_calls[1]
        self.assertEqual(ts1.domain, 'test_domain')
        self.assertEqual(ts2.domain, 'test_domain')
        
    def test_i18n_domain(self):
        from pyramid.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.settings['genshi.default_domain'] = 'my_domain'
        
        translated_calls = []
        lookup = DummyLookup()

        def translate(msg):
            translated_calls.append(msg)
            return msg

        lookup.translate = translate
        path = self._get_template_path('i18n_domain.genshi')
        renderer = self.make_one(path, lookup)
        renderer({}, {})
        ts = translated_calls[0]
        self.assertEqual(ts.domain, 'test_domain')

    def test_implementation_method(self):
        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        self.assertEqual(renderer.implementation(), renderer.render)

    def test_render_with_wrong_argument(self):
        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        with self.assertRaises(ValueError):
            renderer(None, {})

    def test_translator(self):
        from genshi.filters import Translator 
        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        self.assertIsInstance(renderer.translator, Translator)

    def test_includeme(self):
        from pyramid_genshi import includeme
        from pyramid_genshi import renderer_factory

        mock_config = (
            flexmock()
            .should_receive('add_renderer')
            .with_args('.genshi', renderer_factory)
            .once()
            .mock()
        )
        includeme(mock_config)

    def test_default_translate(self):
        from pyramid.i18n import TranslationString
        lookup = DummyLookup()
        lookup.translate = None
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        ts = renderer.translate('hello')
        self.assertIsInstance(ts, TranslationString)
        self.assertEqual(ts, TranslationString('hello'))

    def test_lookup_with_pluralize(self):

        def mock_pluralize(): 
            pass

        mock_pluralize()

        lookup = DummyLookup()
        lookup.pluralize = mock_pluralize
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        self.assertEqual(renderer.adaptor.pluralize, mock_pluralize)

    def test_lookup_with_request_pluralize(self):
        from pyramid.threadlocal import manager
        from pyramid.threadlocal import defaults
        from pyramid.testing import DummyRequest
        from pyramid.i18n import get_localizer

        request = DummyRequest()
        localizer = get_localizer(request)

        info = defaults()
        info['request'] = request
        info['registry'].settings = {}
        manager.push(info)

        lookup = DummyLookup()
        path = self._get_template_path('minimal.genshi')
        renderer = self.make_one(path, lookup)
        self.assertEqual(renderer.adaptor.pluralize, localizer.pluralize)

    def test_renderer_factory(self):
        from pyramid_genshi import renderer_factory
        from pyramid_genshi import GenshiTemplateRenderer
        from pyramid.renderers import RendererHelper
        path = self._get_template_path('minimal.genshi')
        info = RendererHelper(path)
        render = renderer_factory(info)
        self.assertEqual(render.path, path)
        self.assertIsInstance(render, GenshiTemplateRenderer)


class TestTranslationStringAdaptor(unittest.TestCase):
    def make_one(self, *args, **kwargs):
        from pyramid_genshi import TranslationStringAdaptor
        return TranslationStringAdaptor(*args, **kwargs)

    def test_ugettext(self):
        translate_calls = []

        def mock_translate(ts):
            translate_calls.append(ts)

        adaptor = self.make_one(mock_translate, 
                                default_domain='MOCK_DEFAULT_DOMAIN')
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
