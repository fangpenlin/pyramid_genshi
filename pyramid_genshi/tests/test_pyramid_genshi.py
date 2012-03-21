import unittest

class DummyLookup(object):
    auto_reload=True
    debug = True
    def translate(self, msg):
        return msg

class GenshiTemplateRendererTests(unittest.TestCase):
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
        
    def _register_utility(self, utility, iface, name=''):
        from pyramid.threadlocal import get_current_registry
        reg = get_current_registry()
        reg.registerUtility(utility, iface, name=name)
        return reg

    def _register_renderer(self):
        from pyramid_chameleon_genshi import renderer_factory
        self.config.add_renderer('.genshi', renderer_factory)
    
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
            
        test_method('xml', 
                    '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        test_method('xhtml', 
                    '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>')
        test_method('text', 
                    '\n')
        
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
            
        test_doctype('html5', 
                    '<!DOCTYPE html>\n<div>\n</div>')
        test_doctype('xhtml', 
                    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"' \
                    ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n' \
                    '<div>\n</div>')
        
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
        
        from translationstring import Translator
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