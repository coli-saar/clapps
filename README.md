
# CL Apps - online job application server

Clapps provides a server that runs a web server on which people can submit job applications. The applications are stored in a database and can be displayed and processed through the web interface.

## Preparation

Clapps requires Python 3. Install its dependencies using `pip install -r requirements.txt`.

Create a MySQL database which will hold the applications. The database schema is described in the [Wiki](https://github.com/coli-saar/clapps/wiki/Database-Scheme).


## Starting a clapps server

To start a new instance of the clapps server, create a new directory with a subdirectory for storing the CVs. Make a copy of [example-clapps.conf](example-clapps.conf) and rename it to `clapps.conf`. The directory structure should be as follows:

```
your_directory
+-- clapps.conf
+-- CVs/
```

Edit your `clapps.conf` to suit your needs. Some fields may require explanation:

* `server.secret` should hold some secret string that will be used to protect against [CSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery) attacks.
* `database.url` needs to be configured to point to your database.
* `email.server` should be an SMTP server through which clapps will send you notifications about new applications. If your SMTP server requires authentication, you can set `email.user` and `email.password` too.
* Under `users`, feel free to add as many users as you like.

Once you start the server using `python main.py` for the clapps main.py, the clapps server will be listening on the port specified in `server.port`. You can have multiple instances of clapps running on the same machine, as long as they use different ports. These instances can share the same database.


## Simplifying the clapps URL

You can and should make your clapps instance(s) available under a default HTTP port by running a web server (e.g. Apache) on your server and having it rewrite URLs. For instance, the following code block for `/etc/apache2/sites-enabled/000-default` redirects the path `http://.../ak19b` to `http://...:5001/`.

```
<Location /ak19b>
  ProxyPass http://localhost:5001 retry=0
  ProxyPassReverse http://localhost:5001
  SetOutputFilter proxy-html
  ProxyHTMLURLMap http://localhost:5001
</Location>
RewriteRule ^/ak19b$ /ak19b/ [R]
```

The entry `server.path` in your `clapps.conf` should point to the URL under which your clapps instance can be reached. Notice that the entry in `examples-clapps.conf` is consistent with the URL `/ak19b/` which is specified in the Apache configuration block above.

