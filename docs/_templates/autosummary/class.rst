{{ fullname | escape | underline}}

.. Don't use :members: in autoclass because it shows information of
   classes based on classes and show a lot of information.

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
    :private-members:
    :undoc-members:
    :show-inheritance:

   {% block attributes %}
   {% if attributes %}
      .. rubric:: Attributes

      .. autosummary::
         :toctree:

         {% for item in attributes %}
         {{ name }}.{{ item }}
         {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block methods %}
   {% if methods %}
      .. rubric:: Methods

      .. autosummary::
         :toctree:

         {% for item in methods %}
         {{ name }}.{{ item }}
         {%- endfor %}
   {% endif %}
   {% endblock %}
