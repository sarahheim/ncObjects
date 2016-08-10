Text2NC's documentation
=======================

Guide
^^^^^

    import sccoos
    c = sccoos.CAF()
    print c.ncpath
    print c.logsdir
    c.text2nc_all()

Notes
^^^^^

  - change ncpath(s) in __init__ to /data (currently using local home)
  - put *createVariable* in text

.. graphviz::

   digraph {
      "From" -> "To";
   }

Contents
^^^^^^^^

.. toctree::
    :maxdepth: 3

.. autosummary::
    :toctree: _autosummary

    sccoos.SASS
    sccoos.CAF

.. autoclass:: nc.NC
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: sccoos.SCCOOS
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: sccoos.SASS
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: sccoos.CAF
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
