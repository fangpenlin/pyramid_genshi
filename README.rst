pyramid_genshi
==============

Bindings for `Genshi <http://genshi.edgewall.org/>`_ templating support under
`Pyramid <http://docs.pylonsproject.org/>`_.

To use pyramid_genshi, simply include pyramid_genshi in your Pyramid main 
function::

    config.include('pyramid_genshi')
    
And you can use it as you use other template::

    @view_config(route_name='home',
                 renderer='my_project:templates/home.genshi')
    def home(request):
        return 'Hello world'
        
To adjust output format, you can change `genshi.method` in settings. ::

    genshi.method = xhtml
    
To adjust the default i18n domain, you can change `genshi.default_domain` in 
settings. ::

    genshi.default_domain = my_domain
