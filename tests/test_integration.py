from __future__ import unicode_literals
import unittest

import mock
import webtest
from pyramid.config import Configurator

NOT_SET = object()


class TestGenshiTemplateRendererIntegration(unittest.TestCase):

    def make_app(self, config_decorator=None, settings=None):
        settings = settings or {}
        config = Configurator(settings=settings)
        config.include('pyramid_genshi')
        if config_decorator is not None:
            config.include(config_decorator)
        app = config.make_wsgi_app()
        testapp = webtest.TestApp(app)
        return testapp

    def make_minimal_app(
        self,
        template='fixtures/minimal.genshi',
        values=NOT_SET,
    ):
        """Make a minimal app for rendering given template and values

        """
        if values is NOT_SET:
            values = {}

        def minimal(request):
            return values

        def add_config(config):
            config.add_view(minimal, renderer=template)

        testapp = self.make_app(add_config)
        return testapp

    def test_simple(self):
        testapp = self.make_minimal_app(
            template='fixtures/simple.genshi',
            values=dict(name='foobar'),
        )
        resp = testapp.get('/')
        self.assertEqual(resp.body, '<div>\nfoobar\n</div>')

    def test_render_method_and_format(self):
        testapp = self.make_minimal_app()

        def assert_render_method(method, expected):
            testapp.app.registry.settings['genshi.method'] = method
            resp = testapp.get('/')
            self.assertEqual(resp.body, expected)
            
        assert_render_method(
            'xml',
            '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>',
        )
        assert_render_method(
            'xhtml',
            '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>',
        )
        assert_render_method('text', '\n')
        
        def assert_render_format(format, expected):
            testapp.app.registry.settings['genshi.default_format'] = format
            resp = testapp.get('/')
            self.assertEqual(resp.body, expected)
            
        assert_render_format(
            'xml',
            '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>',
        )
        assert_render_format(
            'xhtml',
            '<div xmlns="http://www.w3.org/1999/xhtml">\n</div>',
        )
        assert_render_format('text', '\n')

    def test_render_doctype(self):
        testapp = self.make_minimal_app()

        def assert_doctype(doctype, expected):
            testapp.app.registry.settings['genshi.default_doctype'] = doctype
            resp = testapp.get('/')
            self.assertEqual(resp.body, expected)
            
        assert_doctype(
            'html5',
            '<!DOCTYPE html>\n<div>\n</div>'
        )
        assert_doctype(
            'xhtml',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
            ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
            '<div>\n</div>'
        )

    def test_render_encoding(self):
        testapp = self.make_minimal_app('fixtures/chinese.genshi')
        
        def assert_encoding(encoding, expected):
            testapp.app.registry.settings['genshi.default_encoding'] = encoding
            resp = testapp.get('/')
            self.assertEqual(resp.body, expected)
            
        assert_encoding(
            'utf8',
            b'<div>\n\xe4\xb8\xad\xe6\x96\x87\xe5\xad\x97\n</div>',
        )
        assert_encoding(
            'cp950',
            b'<div>\n\xa4\xa4\xa4\xe5\xa6r\n</div>',
        )

    @mock.patch('pyramid.i18n.Localizer.translate')
    def test_i18n_msg(self, translate_method):
        testapp = self.make_minimal_app('fixtures/i18n_msg.genshi')

        def translate(msg):
            if msg == 'Hello':
                return 'Hola'
            return msg

        translate_method.side_effect = translate
        resp = testapp.get('/')
        self.assertEqual(resp.body, '<div>Hola World</div>')

    @mock.patch('pyramid.i18n.Localizer.translate')
    def test_default_domain(self, translate_method):
        translate_method.side_effect = lambda text: text
        testapp = self.make_minimal_app('fixtures/i18n_msg.genshi')
        testapp.app.registry.settings['genshi.default_domain'] = 'test_domain'
        testapp.get('/')

        self.assertEqual(translate_method.call_count, 2)
        ts1 = translate_method.call_args_list[0][0][0]
        ts2 = translate_method.call_args_list[1][0][0]
        self.assertEqual(ts1.domain, 'test_domain')
        self.assertEqual(ts2.domain, 'test_domain')

    @unittest.skip('Known bug, wont fix currently')
    @mock.patch('pyramid.i18n.Localizer.translate')
    def test_i18n_domain(self, translate_method):
        translate_method.side_effect = lambda text: text
        testapp = self.make_minimal_app('fixtures/i18n_domain.genshi')
        testapp.app.registry.settings['genshi.default_domain'] = 'my_domain'
        testapp.get('/')
        
        self.assertEqual(translate_method.call_count, 2)
        ts1 = translate_method.call_args_list[0][0][0]
        ts2 = translate_method.call_args_list[1][0][0]
        self.assertEqual(ts1.domain, 'test_domain')
        # TODO: this _('xxx') call should also be in test_domain
        # but since our _ method cannot access genshi context,
        # so that its is wrong, maybe we should address this issue later
        #
        # A temporary solution would be
        #
        #     _('xxx', domain='test_domain')
        #
        self.assertEqual(ts2.domain, 'test_domain')

    def test_render_with_wrong_argument(self):
        testapp = self.make_minimal_app(values=None)
        with self.assertRaises(ValueError):
            testapp.get('/')
