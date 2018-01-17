Text2NC's documentation
=======================

.. include:: ../../README.rst

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

  .. rubric:: Class Inheritance

  .. inheritance-diagram:: sccoos

  .. rubric:: Graphviz Workflow

  .. graphviz:: flow_createNCs.dot

  .. graphviz:: flow_ncMeta.dot

  .. rubric:: Ex PlantUML

.. uml::

    @startuml

    (*) --> "First mod"
    "First mod" --> (*)

    @enduml

Contents
^^^^^^^^

.. toctree::
    :maxdepth: 4

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

.. autoclass:: sass_oop.SASS
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: caf.CAF
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: dm_mooring.Moor
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
