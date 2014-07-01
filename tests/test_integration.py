from __future__ import unicode_literals
import unittest

import webtest
from pyramid.config import Configurator


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

    def test_simple(self):
        def foobar(request):
            return dict(name='foobar')

        def add_config(config):
            config.add_view(foobar, renderer='fixtures/simple.genshi')

        testapp = self.make_app(add_config)
        resp = testapp.get('/')
        self.assertEqual(resp.body, '<div>\nfoobar\n</div>')
