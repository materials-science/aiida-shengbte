.. _code:

============
3. Create codes
============

Now we need to add the code (in this case `ShengBTE`_ and `Thirdorder`_) to `AiiDA`_.  The
``verdi`` subcommand ``code`` makes it possible to set up a code that later
can be used to execute a given calculation. The code has to be installed on
the `computer`, i.e. in this case ``mycluster``. Before configuring the code
in `AiiDA`_, please make sure it runs and functions as normal on ``mycluster``.

Remember `AiiDA`_ use ``bash`` to implement your codes. So make sure the dependencies and environment have been set correctly (Commonly adding paths of libs in ``<The user's directory you set to login remote computer>/.bashrc``).

prerequisite
++++++++++++

VASP code
---------
`AiiDA VASP code setup`_

Phonopy code
------------
`aiida-phonopy`_

Thirdorder
++++++++++

We assume you have gotton `Thirdorder`_ installed and set the environments of `Spglib`_ and `Thirdorder`_ correctly. If you are not sure, use ``ssh user@mycluster <thirdorder command>`` to have a test. As follow we will take ``thirdorder_vasp.py`` command as a example, assuming its absolute executable path is ``/workdir/thirdorder/thirdorder_vasp.py`` on the computer you created before in :ref:`profile`.

Thirdorder sow
--------------

Let us now add the `thirdorder_vasp sow` code, which will call ``thirdorder_vasp.py sow`` on remote computer::

    $ verdi code setup
    Info: enter "?" for help
    Label: thirdorder_vasp_sow
    Description []:
    Default calculation input plugin: shengbte.thirdorder_sow
    Installed on target computer? [True]:
    Computer: mycluster
    Remote absolute path: /workdir/thirdorder/thirdorder_vasp.py
    Success: Code<1> user@mycluster created

Thirdorder reap
--------------

Let us now add the `thirdorder_vasp reap` code, which will call ``thirdorder_vasp.py reap`` on remote computer::

    $ verdi code setup
    Info: enter "?" for help
    Label: thirdorder_vasp_reap
    Description []:
    Default calculation input plugin: shengbte.thirdorder_reap
    Installed on target computer? [True]:
    Computer: mycluster
    Remote absolute path: /workdir/thirdorder/thirdorder_vasp.py
    PREPEND TEXT: find job.* -name vasprun.xml|sort -n|
    Success: Code<2> user@mycluster created

Note that ``find job.* -name vasprun.xml|sort -n|`` is neccessary as prepend_text to implement ``thirdorder_vasp.py reap``.

ShengBTE
++++++++

As same with setup of `Thirdorder`_ code. Assuming ``ShengBTE``'s absolute executable path is ``/workdir/ShengBTE/ShengBTE`` on the computer you created before in :ref:`profile`.

Let us now add the `ShengBTE`_ code, which will call ``ShengBTE`` on remote computer::

    $ verdi code setup
    Info: enter "?" for help
    Label: shengbte
    Description []:
    Default calculation input plugin: shengbte.shengbte
    Installed on target computer? [True]:
    Computer: mycluster
    Remote absolute path: /workdir/ShengBTE/ShengBTE
    Success: Code<2> user@mycluster created

You then can add other codes by yourself following above steps.

In next section we will run a simple test to ensure you have known these concepts: `profile`, `computer` and `code`.

.. _AiiDA: https://www.aiida.net
.. _ShengBTE: http://www.shengbte.org/
.. _Thirdorder: https://bitbucket.org/sousaw/thirdorder/
.. _Spglib: https://spglib.github.io/spglib/
.. _Aiida VASP code setup: https://aiida-vasp.readthedocs.io/en/latest/getting_started/code.html
.. _aiida-phonopy: https://aiida-phonopy.readthedocs.io/en/latest/install.html