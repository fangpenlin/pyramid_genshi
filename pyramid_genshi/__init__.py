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
from pyramid.threadlocal import get_current_registry
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
    
def renderer_factory(path):
    return renderers.template_renderer_factory(path, GenshiTemplateRenderer)
        
class GenshiTemplateRenderer(object):
    implements(ITemplateRenderer)
    
    def __init__(self, path, lookup, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.path = path
        self.lookup = lookup
        
        # XXX: This is dirty
        self.settings = {}
        registry = get_current_registry()
        if registry is not None:
            self.settings = registry.settings
        self.default_domain = self.settings.get('genshi.default_domain')
        
        # the i18n is available
        if lookup.translate is not None:
            # XXX: This is a very dirty hack, too
            # but this is how Pyramid does - getting request from local thread
            # IChameleonLookup doesn't provide pluralize there, so we need to
            # get by it ourself
            pluralize = None
            if hasattr(lookup, 'pluralize'):
                # pluralize should be added to the lookup, but it is not there
                # see will it be there in the future
                # this is mainly for test right now
                pluralize = lookup.pluralize
            else:
                request = get_current_request()
                if request is not None:
                    pluralize = get_localizer(request).pluralize
            
            self.adaptor = TranslationStringAdaptor(
                lookup.translate, 
                pluralize,
                default_domain=self.default_domain
            )
            self._translator = Translator(self.adaptor)
        # no i18n available, just use translator with NullTranslations
        else:
            self._translator = Translator()
            
        # TODO: handle auto reload here
        self._loader = TemplateLoader(callback=self._tmpl_loaded)
        self._tmpl = self.loader.load(os.path.abspath(self.path))
                
    def translate(self, *args, **kwargs):
        kwargs.setdefault('domain', self.default_domain)
        ts = TranslationString(*args, **kwargs)
        if self.lookup.translate is not None:
            return self.lookup.translate(ts)
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
    
    #@reify # avoid looking up reload_templates before manager pushed
    @property
    def template(self):
        """Loaded Genshi Template
        
        """
        return self._tmpl
    
    def render(self, **values):
        """Render template with values
        
        """
        values.setdefault('_', self.translate)
        stream = self.template.generate(**values)
        method = self.settings.get('genshi.method', 'html')
        body = stream.render(method=method)
        return body
        
    # implement ITemplateRenderer interface
    
    def implementation(self):
        return self.render
    
    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        result = self.render(**system)
        return result

def includeme(config):
    config.add_renderer('.genshi', renderer_factory)