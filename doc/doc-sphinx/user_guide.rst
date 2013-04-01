==============================================
 How to use Thunderstorm Library interactively
==============================================

An example
==========

.. code-block:: python

   from thunderstorm.interact import new_storm

   mystorm = new_storm("tmp_storm.oef")
   mystorm.import_SERMA("../TestData01012012/SERMA/101_s1V_A.csv", "serma data")
   mystorm.overlay_raw_tlp((0,))


