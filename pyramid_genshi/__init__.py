from __future__ import unicode_literals
import os
import logging
import gettext

from pyramid.settings import asbool
from pyramid.path import AssetResolver
from pyramid.i18n import TranslationString
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from genshi.template import TemplateLoader
from genshi.filters import Translator

logger = logging.getLogger(__name__)


class TranslationStringAdaptor(gettext.NullTranslations):
    """An adaptor provides gettext Translation interface for Genshi i18n filter,
    it converts gettext function calls to TranslationString as argument to
    underlying translate and pluralize functions
    
    """
    
    def __init__(self, translate, pluralize=None, default_domain=None):
        """translate is the function to be called with a TranslationString
        argument and return translated string
        
        pluralize is a function to be called with arguments
        
            (singular, plural, n, domain=None, mapping=None)
        
        for pluralize message
        
        """
        gettext.NullTranslations.__init__(self)
        self.translate = translate
        self.pluralize = pluralize
        self.default_domain = default_domain
        
    def ugettext(self, message, domain=None):
        if domain is None:
            domain = self.default_domain
        tmsg = self.translate(TranslationString(message, domain=domain))
        return tmsg

    def dugettext(self, domain, message):
        return self.ugettext(message, domain)
    
    def ungettext(self, msgid1, msgid2, n, domain=None):
        if domain is None:
            domain = self.default_domain
        if self.pluralize is not None:
            tmsg = self.pluralize(msgid1, msgid2, n, domain=domain)
            return tmsg
        if n == 1:
            return msgid1
        else:
            return msgid2
        
    def dungettext(self, domain, msgid1, msgid2, n):
        return self.ungettext(msgid1, msgid2, n, domain)


class GenshiTemplateRendererFactory(object):
    def __call__(self, info):
        resolver = AssetResolver(info.package)
        tmpl_path = resolver.resolve(info.name).abspath()
        return GenshiTemplateRenderer(tmpl_path, info.settings)


class GenshiTemplateRenderer(object):
    
    def __init__(
        self,
        path,
        settings,
        template_class=None,
    ):
        self.path = path
        self.settings = settings
        # self.lookup = lookup
        self.template_class = template_class
        
        self.default_domain = self.settings.get('genshi.default_domain')
        auto_reload = asbool(self.settings.get('genshi.auto_reload', True))
        self._loader = TemplateLoader(
            callback=self._tmpl_loaded,
            auto_reload=auto_reload,
        )
        # TODO: handle i18n here

        # should we enable i18n?
        i18n = asbool(self.settings.get('genshi.i18n', True))
        if i18n:
            self.adaptor = TranslationStringAdaptor(
                self.localizer.translate,
                self.localizer.pluralize,
                default_domain=self.default_domain
            )
            self._translator = Translator(self.adaptor)
        # no i18n available, just use translator with NullTranslations
        else:
            self._translator = Translator()

    @property
    def localizer(self):
        request = get_current_request()
        localizer = get_localizer(request)
        return localizer
                
    def translate(self, *args, **kwargs):
        kwargs.setdefault('domain', self.default_domain)
        ts = TranslationString(*args, **kwargs)
        if self.localizer is not None:
            return self.localizer.translate(ts)
        return ts
        
    def _tmpl_loaded(self, tmpl):
        """Called when a template is loadded by loader
        
        """
        self._translator.setup(tmpl)
        
    @property
    def loader(self):
        """Genshi template loader
        
        """
        return self._loader
        
    @property
    def translator(self):
        """Genshi i18n translator filter
        
        """
        return self._translator

    @property
    def template(self):
        """Loaded Genshi Template
        
        """
        tmpl = self.loader.load(
            os.path.abspath(self.path),
            cls=self.template_class,
        )
        return tmpl
    
    def render(self, **values):
        """Render template with values
        
        """
        values.setdefault('_', self.translate)
        stream = self.template.generate(**values)
        method = self.settings.get('genshi.method', 'html')
        fmt = self.settings.get('genshi.default_format', method)
        encoding = self.settings.get('genshi.default_encoding', 'utf8')
        doctype = self.settings.get('genshi.default_doctype', None)
        kwargs = {}
        if doctype is not None:
            kwargs['doctype'] = doctype
        body = stream.render(method=fmt, encoding=encoding, **kwargs)
        return body
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.render(**system)
        return result


def includeme(config):
    renderer_factory = GenshiTemplateRendererFactory()
    config.add_renderer('.genshi', renderer_factory)
