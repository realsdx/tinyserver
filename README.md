# TinyServer
### This is a tiny HTTP server written in Python

It provides minimal HTTP server to serve simple HTML pages

## Screenshots
TinyServer in action
![alt text](.github/img/tiny_term.png)

![alt text](.github/img/tinyindex.png)

Default 404 Page
![alt text](.github/img/tiny_404.png)

## Usage
It serves HTML pages.
At least one `.hmtl` file should be in the current directory.

If no specified filename is given in URL then it will serve `index.html`.

Start the server in specified port.
```python
python main.py 8888
```
Start the server in default port 5000
```python
python main.py
```

### I made this to learn about HTTP Servers.
#### Not intended for actual use.
