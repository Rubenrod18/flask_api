{{ fullname | escape | underline }}

..
  Custom formatting of module doc layout
  https://stackoverflow.com/questions/48074094/use-sphinx-autosummary-recursively-to-generate-api-documentation
  TODO: how can we add the documented module attributes (constants, ...)?

.. rubric:: Description

.. automodule:: {{ fullname }}
    :members:
    :private-members:
    :inherited-members:
    :undoc-members:


    {% block modules %}
    {% if modules %}
    .. rubric:: Modules

    .. autosummary::
       :toctree:
       :recursive:

       {% for item in modules %}
       {{ item }}
       {% endfor %}

    {% endif %}
    {% endblock %}


    {% block classes %}
    {% if classes %}
    .. rubric:: Classes

    .. autosummary::
        :toctree:

        {% for item in classes %}
        {{ item }}
        {% endfor %}

    {% endif %}
    {% endblock %}


    {% block functions %}
    {% if functions %}
    .. rubric:: Functions

    .. autosummary::
        :toctree:

        {% for item in functions %}
        {{ item }}
        {% endfor %}

    {% endif %}
    {% endblock %}


    {% block attributes %}
    {% if attributes %}
    .. rubric:: Attributes

    .. autosummary::
       :toctree:

       {% for item in attributes %}
       {{ item }}
       {% endfor %}
    {% endif %}
    {% endblock %}


    {% block exceptions %}
    {% if exceptions %}
    .. rubric:: Exceptions

    .. autosummary::
        :toctree:

        {% for item in exceptions %}
        {{ item }}
        {% endfor %}

    {% endif %}
    {% endblock %}
