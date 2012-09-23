.. _api:

API
===

.. module:: gears.environment

Environment
-----------

.. autoclass:: Environment
   :members:

File Finders Registry
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Finders
   :members:

MIME Types Registry
^^^^^^^^^^^^^^^^^^^

.. autoclass:: MIMETypes
   :members:

Compilers Registry
^^^^^^^^^^^^^^^^^^

.. autoclass:: Compilers
   :members:

Preprocessors Registry
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Preprocessors
   :members:

Postprocessors Registry
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Postprocessors
   :members:

Compressors Registry
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: Compressors
   :members:

Suffixes Registry
^^^^^^^^^^^^^^^^^

.. autoclass:: Suffixes
   :members:

.. module:: gears.asset_attributes

Asset Attributes
----------------

.. autoclass:: AssetAttributes
   :members:
   :inherited-members:

.. module:: gears.asset_handler

Asset Handlers
--------------

.. autoclass:: BaseAssetHandler
   :members:
   :inherited-members:

   .. automethod:: __call__(asset)

.. autoclass:: ExecMixin
   :members:

.. module:: gears.processors

Processors
^^^^^^^^^^

.. autoclass:: BaseProcessor
   :members:

.. module:: gears.compilers

Compilers
^^^^^^^^^

.. autoclass:: BaseCompiler
   :members:
