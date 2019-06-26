# SDF - packages
  
1.  [Adding the SDF stable repository to your system](adding-the-sdf-stable-repository-to-your-system.md)
2.  [Quickstart](quickstart.md)
3.  [Installing individual packages](installing-individual-packages.md)
4.  [Upgrading](upgrading.md)
5.  [Running Horizon in production](running-horizon-in-production.md)
6.  [Building Packages](building-packages.md)
7.  [Running a Full Validator](running-a-full-validator.md)
8.  [Publishing a History archive](publishing-a-history-archive.md)
9.  [Backfilling a History archive](backfilling-a-history-archive.md)
10. [Monitoring](monitoring.md)
11. [Testnet Reset](testnet-reset.md)

## Publishing a history archive

Running a full validator requires publishing the validator's history archive, this can be achieved using blob stores such as Amazon's s3, digital ocean's spaces or simply by serving a local archive directly via an HTTP server such as Nginx or Apache. Which ever method you choose to use you may find the below tips useful.

In order to publish a history archive it is essential to have a stellar-core instance running as either an [Archiver](https://www.stellar.org/developers/stellar-core/software/admin.html#archiver-nodes) or a [Full Validator](https://www.stellar.org/developers/stellar-core/software/admin.html#full-validators)

### Caching and History Archives

It is possible to significantly reduce the data transfer costs associated with running a public History archive by using common caching techniques or a CDN.

Which ever solution you choose, 3 simple rules apply to caching the History archives:

  * Do not cache the archive state file `.well-known/history-stellar.json` (**"Cache-Control: no-cache"**)
  * Do not cache HTTP 4xx responses (**"Cache-Control: no-cache"**)
  * Cache everything else for as long as possible (**> 1 day**)

### Local history archive published using nginx

 * add a history configuration stanza to your `/etc/stellar/stellar-core.cfg`:

```
[HISTORY.local]
get="cp /mnt/xvdf/stellar-core-archive/node_001/{0} {1}"
put="cp {0} /mnt/xvdf/stellar-core-archive/node_001/{1}"
mkdir="mkdir -p /mnt/xvdf/stellar-core-archive/node_001/{0}"
```

 * run new-hist to create the local archive

`# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist local`

This command creates the History archive structure:

```
# tree -a /mnt/xvdf/stellar-core-archive/
/mnt/xvdf/stellar-core-archive
└── node_001
    ├── history
    │   └── 00
    │       └── 00
    │           └── 00
    │               └── history-00000000.json
    └── .well-known
        └── stellar-history.json

6 directories, 2 file
```

 * configure a virtual host to serve the local archive (Nginx)

```
server {
  listen 80;
  root /mnt/xvdf/stellar-core-archive/node_001/;

  server_name history.example.com;

  # default is to deny all
  location / { deny all; }

  # do not cache 404 errors
  error_page 404 /404.html;
  location = /404.html {
    add_header Cache-Control "no-cache" always;
  }

  # do not cache history state file
  location ~ ^/.well-known/stellar-history.json$ {
    add_header Cache-Control "no-cache" always;
    try_files $uri;
  }

  # cache entire history archive for 1 day
  location / {
    add_header Cache-Control "max-age=86400";
    try_files $uri;
  }
}
```

### Amazon S3 backed history archive

 * add a history configuration stanza to your `/etc/stellar/stellar-core.cfg`:

```
[HISTORY.s3]
get='curl -sf http://history.example.com/{0} -o {1}' # Cached HTTP endpoint
put='aws s3 cp --region us-east-1 {0} s3://bucket.name/{1}' # Direct S3 access
```

 * run new-hist to create the s3 archive

`# sudo -u stellar stellar-core --conf /etc/stellar/stellar-core.cfg new-hist s3`

 * serve the archive using an Amazon S3 static site
 * optionally place a reverse proxy and CDN in front of the S3 static site

```
server {
  listen 80;
  root /srv/nginx/history.example.com;
  index index.html index.htm;

  server_name history.example.com;

  # use google nameservers for lookups
  resolver 8.8.8.8 8.8.4.4;

  # bucket.name s3 static site endpoint
  set $s3_bucket "bucket.name.s3-website-us-east-1.amazonaws.com";

  # default is to deny all
  location / { deny all; }

  # do not cache 404 errors
  error_page 404 /404.html;
  location = /404.html {
    add_header Cache-Control "no-cache" always;
  }

  # do not cache history state file
  location ~ ^/.well-known/stellar-history.json$ {
    add_header Cache-Control "no-cache" always;
    proxy_intercept_errors on;
    proxy_pass  http://$s3_bucket;
    proxy_read_timeout 120s;
    proxy_redirect off;
    proxy_buffering off;
    proxy_set_header        Host            $s3_bucket;
    proxy_set_header        X-Real-IP       $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto $scheme;
  }

  # cache history archive for 1 day
  location / {
    add_header Cache-Control "max-age=86400";
    proxy_intercept_errors on;
    proxy_pass  http://$s3_bucket;
    proxy_read_timeout 120s;
    proxy_redirect off;
    proxy_buffering off;
    proxy_set_header        Host            $s3_bucket;
    proxy_set_header        X-Real-IP       $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto $scheme;
  }
}
```
