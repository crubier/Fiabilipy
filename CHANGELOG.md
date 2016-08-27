2016-08-27 Vincent Lecrubier <vincent dot lecrubier at gmail dot com>

	* 3.0 :
	Port to python3
	networkx representation is based on names of components instead of component instances themselves
  addition of the `_map` attribute on `systems` in order to map component names to component themselves


2013-10-08 Akim Sadoui <akim dot sadoui at etu dot utc dot fr>

	* 2.4 :
	A better cache system.
	A documentation in English, using Sphinx (http://sphinx.pocoo.org/).
	Add some metrics computation. One can compute maintainability, and therefore
	availability, for complex systems and voters.
	First release as Archlinux package.
	The code has been cleaned. (thank you pylint ;))
	Symbolic computation can now be performed, using sympy.

2013-10-08 Simon Chabot <simon dot chabot at chabotsi dot fr>

	* 2.3.1 :
	Update the module name from fiabili to fiabilipy.

2013-10-08 Simon Chabot <simon dot chabot at chabotsi dot fr>

	* 2.3 :
	Create a pypi package (https://pypi.python.org/pypi/fiabilipy/).
	Update the documentation.
	A Markov graph can be drawn.

2013-10-08 Simon Chabot <simon dot chabot at chabotsi dot fr>

	* 2.2 :
	Add a markov module.

2013-10-08 Simon Chabot <simon dot chabot at chabotsi dot fr>

	* 0.2 :
	Some metrics are cached to make the computation faster (MTTF, MTTR, etc).
	A documentation is started (in French… sorry).

2013-10-08 Simon Chabot <simon dot chabot at chabotsi dot fr>

	* 0.1 :
	*Show time*.
	System, Component and voter can be built.
	Reliability can be computed.
	MTTF can be computed.
	Compute the minimal cuts of order 1 and 2.
