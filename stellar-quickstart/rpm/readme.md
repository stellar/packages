# readme

a few containers to test rpm packages.

```shell
podman build -f Dockerfile.public  -t test
podman run --rm -it  -t test /bin/bash
```
