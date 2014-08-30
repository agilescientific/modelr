========================
Welcome to modelr server
========================

.. image:: https://img.shields.io/badge/license-Apache-blue.svg
    :target: https://github.com/agile-geoscience/modelr/blob/develop/LICENSE.md
    :alt: Apache 2 license

.. image:: http://img.shields.io/pypi/dw/modelr.svg
    :target: http://pypi.python.org/pypi/modelr/
    :alt: PyPI downloads
    
.. image:: https://img.shields.io/pypi/v/modelr.svg
    :target: http://pypi.python.org/pypi/modelr/
    :alt: PyPI version
    
.. image:: http://img.shields.io/github/issues/badges/modelr.svg
    :target: https://github.com/agile-geoscience/modelr
    :alt: GitHub issues

This is the documentation for the back-end modelr server software. You might be looking for `modelr.io <https://www.modelr.io/>`_

Modelr server is a Google-Charts-like API for geophysics! Submit tasks via a URL.

Example: 

* `<https://www.modelr.org/plot.jpeg?script=wedge_spatial.py&theta=0&f=25&colourmap=Greys&base1=variable-density&overlay1=none&base2=earth-model&overlay2=wiggle&opacity=0.5&Rock0=3000.0%2C1600.0%2C2500.0%2C%0A%09%20%2050.0%2C%2050.0%2C%2050.0&Rock1=2770.0%2C1780.0%2C2185.0%2C%0A%09%20%2050.0%2C%2050.0%2C%2050.0&Rock2=3000.0%2C1600.0%2C2500.0%2C%0A%09%20%2050.0%2C%2050.0%2C%2050.0&tslice=0.15&scale=1.0%2C99&type=scenario>`_

Full interface
+++++++++++++
* There's a full interface for modelr at `modelr.io <https://www.modelr.io/>`_

Prerequisites
++++++++++++++++

You will need scientific python (numpy, scipy, matplotlib), which come with
Enthought Canopy:  `<http://www.enthought.com>`_

They can alternatively be installed via pip, aptitude, ports, or sourced from git.

Additionally, ImageMagick will need to be installed in order to handle conversion of svg to png. Binaries can be downloaded from the ImageMagick website: 
`<http://www.imagemagick.org/script/binary-releases.php#unix>`_

ImageMagick can also be installed via ports or aptitude.

Other python packages that will be automatically installed during setup:

* agilegeo
* pypng
* requests
* jinja2
* svgwrite

Links
+++++++++++

* `Agile Geoscience <http://www.agilegeoscience.com>`_
* `Homepage <http://agile-geoscience.github.com/modelr/>`_
* `Issue Tracker <https://github.com/agile-geoscience/modelr/issues/>`_
* `PyPi <http://pypi.python.org/pypi/modelr/>`_
* `Github <https://github.com/agile-geoscience/modelr>`_

Authors
++++++++++++++++

* `Matt Hall <https://github.com/kwinkunks>`_ @ `Agile Geoscience <http://www.agilegeoscience.com>`_
* `Sean Ross-Ross <https://github.com/srossross>`_ @ now at `Continuum`
* `Evan Bianco <https://github.com/EvanBianco>`_ @ `Agile Geoscience <http://www.agilegeoscience.com>`_
* `Ben Bougher <https://github.com/ben-bougher>`_
