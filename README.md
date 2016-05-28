## Python 3.5

[Python 3.5 in Fedora 23](https://synfo.github.io/2015/11/13/Python-3.5-in-Fedora)

    $ dnf copr enable -y mstuchli/Python3.5
    $ dnf install -y python35-python3
    $ python3.5

### virtualenv

    virtualenv-3.4 --python python3.5 venv
	. venv/bin/activate
