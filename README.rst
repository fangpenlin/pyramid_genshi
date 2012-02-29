pyramid_genshi
==============

Bindings for Genshi templating support under `Pyramid
<http://docs.pylonsproject.org/>`_.

To use pyramid_genshi, simply include pyramid_genshi in your Pyramid main 
function::

    config.include('pyramid_genshi')
    
And you can use it as you use other template:

    @view_config(route_name='home',
                 renderer='my_project:templates/home.genshi')
    def home(request):
        return 'Hello world'
        
To adjust output format, you can add `genshi.method` in your settings. For 
example, in development.ini or production.ini, you can write::

    genshi.method = xhtml
    
To adjust the default i18n domain, you can write

    genshi.default_domain = my_domain