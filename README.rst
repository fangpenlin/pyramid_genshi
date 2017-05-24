pyramid_genshi
==============

Build:

.. image:: https://travis-ci.org/fangpenlin/pyramid_genshi.png?branch=master   
  :target: https://travis-ci.org/fangpenlin/pyramid_genshi

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
        
Settings
--------
        
To adjust output format, you can change `genshi.default_format` ::

    genshi.default_format = xhtml
    
To adjust output encoding, you can change `genshi.default_encoding` ::

    genshi.default_encoding = cp950
    
To adjust output doctype, you can change `genshi.default_doctype` ::

    genshi.default_doctype = html5
   
To adjust the default i18n domain, you can change `genshi.default_domain` ::

    genshi.default_domain = my_domain
    
To adjust template auto reloading, you can change `genshi.auto_reload` ::

    genshi.auto_reload = False
    
For available options, you can reference to 
`<http://genshi.edgewall.org/wiki/Documentation/0.6.x/plugin.html>`_
