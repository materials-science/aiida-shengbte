.. _conda_env:

===============
1. Installation
===============

Setup the Conda environment
+++++++++++++++++++++++++++

Install MiniConda
-----------------

1. Download `Miniconda`_ installation pakage. `Optinal Tsinghua mirror`_.

2. Install MiniConda::
    
    # the `version` is the version code of your MiniConda
    bash ./Miniconda-[version].sh

3. Reboot shell

4. Create and activate a virtual environment called ``aiida_shengbte`` and prepare it::

    # create a virtual environment
    conda create -n aiida_shengbte python=3.8
    # activate environment
    conda activate aiida_shengbte
    # exit current environment
    conda deactivate

The command ``conda activate aiida_shengbte`` enables the `Conda`_ environment ``aiida_shengbte``.
All the settings, installs or running are always done in this `Conda`_
environment. It is mandatory to activate this every time logging to
this computer. Please also remember to activate this everytime you
need to make changes to the respective environments. You can of course
created multiple `Conda`_ environments depending on your use case or versions
you would like to have installed.

.. _`Optinal Tsinghua mirror`:


Optinal Tsinghua mirror
```````````````````````

1. Download from https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/ and install

2. Add Tsinghua's channel::

    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    conda config --set show_channel_urls yes

Install AiiDA and AiiDA-ShengBTE
++++++++++++++++++++++++++++++++

We assume `MiniConda`_ is installed and operational and will now activate a virtual
environment called ``aiida_shengbte`` and install `AiiDA`_. Check `AiiDA Installation Docs`_ for more details.

1. Prerequisites Installation::

    # you may try `apt update` in advance
    # if logging `update error message`, try a accessible open source mirror
    sudo apt-get install postgresql postgresql-server-dev-all postgresql-client
    sudo apt-get install rabbitmq-server
    sudo rabbitmqctl status

2. Setup the ``aiida-core``
    conda activate aiida_shengbte
    pip install aiida-core[atomic_tools]
    # For maximum customizability, one can use verdi setup
    verdi quicksetup

3. Success info like this::

    Success: created new profile `a`.
    Info: migrating the database.
    Operations to perform:
    Apply all migrations: auth, contenttypes, db
    Running migrations:
    Applying contenttypes.0001_initial... OK
    Applying contenttypes.0002_remove_content_type_name... OK
    ...
    Applying db.0044_dbgroup_type_string... OK
    Success: database migration completed.

4. More optinal operations if need
    - ``rabbitmq-server -detached``
    - ``verdi daemon start``
    - ``verdi check``
    - Use ``sudo apt install graphviz`` for Ubuntu to install `graphviz`_
    - `Postgres`_

5. Get `AiiDA-ShengBTE`_ and install
    From Github::

        git clone https://github.com/Meterials-Science-of-IAS/aiida-shengbte
        cd aiida-shengbte && pip install -e .
    
    .. # TODO: pip install aiida-shengbte

6. ``reentry scan`` to update `entry_points`

7. `AiiDA-VASP`_, `AiiDA-QUANTUMESPRESSO`_ and `AiiDA-PHONOPY`_ will also be installed since `AiiDA-ShengBTE`_ depends on them

.. _AiiDA-ShengBTE: https://github.com/aiida-vasp/aiida-vasp
.. _Conda: https://docs.conda.io/en/latest/
.. _MiniConda: https://docs.conda.io/en/latest/miniconda.html
.. _AiiDA: https://www.aiida.net
.. _AiiDA Installation Docs: https://aiida.readthedocs.io/projects/aiida-core/en/latest/intro/installation.html
.. _graphviz: https://graphviz.org/download/
.. _Postgres: https://www.postgresql.org/
.. _AiiDA-VASP: 
.. _AiiDA-QUANTUMESPRESSO: 
.. _AiiDA-PHONOPY: 