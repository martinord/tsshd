# Twisted SSH Server
## Intro
An implementation of a SSH server using the [Twisted Framework](https://twistedmatrix.com/trac/) for network application development.

Twisted is an event-driven framework for Python. It uses a `reactor` event loop as the main part, waiting for events to occur.


## Usage

**Init the server**
```bash
python tsshd.py
```
<br>

**Connecting to the server**
```bash
ssh admin@localhost -p 2222
```

## Packages used
* twisted
* pyopenssl
* crypto
* zope


## Licence

Source code can be found on [github](https://github.com/martinord/tsshd), licenced under [GPL-3.0](https://opensource.org/licenses/GPL-3.0).

Developed by [Martiño Rivera](https://github.com/martinord)
