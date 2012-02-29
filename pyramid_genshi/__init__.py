import os
import logging
import types
import gettext
import locale

import pkg_resources
from zope.interface import implements
from pyramid import renderers
from pyramid.interfaces import ITemplateRenderer
from pyramid.decorator import reify
from pyramid.i18n import TranslationString
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from genshi.template import TemplateLoader
from genshi.filters import Translator

class TranslationStringAdaptor(gettext.NullTranslations):
    """An adaptor provide gettext Translation interface for Genshi i18n filter, 
    it converts gettext function calls to TranslationString as argument to 
    under-layer translate and pluralize functions
    
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
        
class GenshiTemplateRenderer(object):
    implements(ITemplateRenderer)
    
    def __init__(self, path, lookup, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.path = path
        self.lookup = lookup
        
        # XXX: This is dirty, the IChameleonLookup doesn't provide this
        # attribute, but the implement ChameleonRendererLookup
        # unfortunately, the API is not perfect, we need to do this little 
        # hack
        self.settings = lookup.registry.settings
        self.default_domain = self.settings.get('genshi.default_domain')
        
        # the i18n is available
        if lookup.translate is not None:
            # XXX: This is a very dirty hack, too
            # but this is how Pyramid does - getting request from local thread
            # IChameleonLookup doesn't provide pluralize there, so we need to
            # get by it ourself
            request = get_current_request()
            localizer = get_localizer(request)
            
            self.adaptor = TranslationStringAdaptor(
                lookup.translate, 
                localizer.pluralize,
                default_domain=self.default_domain
            )
            self.translator = Translator(self.adaptor)
        # no i18n available, just use translator with NullTranslations
        else:
            self.translator = Translator()
        
    def translate(self, *args, **kwargs):
        kwargs.setdefault('domain', self.default_domain)
        ts = TranslationString(*args, **kwargs)
        if self.lookup.translate is not None:
            return self.lookup.translate(ts)
        return ts
        
    def _tmpl_loaded(self, tmpl):
        """Called when a template is loadded by loader
        
        """
        self.translator.setup(tmpl)
        
    #@reify # avoid looking up reload_templates before manager pushed
    @property
    def template(self):
        # TODO: handle auto reload here
        loader = TemplateLoader(callback=self._tmpl_loaded)
        
        tmpl = loader.load(self.path)
        
        def render(**values):
            values.setdefault('_', self.translate)
            stream = tmpl.generate(**values)
            method = self.settings.get('genshi.method', 'html')
            body = stream.render(method=method)
            return body
        
        return render

    def implement(self):
        return self.template
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.template(**system)
        return result
    
def renderer_factory(path):
    return renderers.template_renderer_factory(path, GenshiTemplateRenderer)

def includeme(config):
    config.add_renderer('.genshi', renderer_factory)