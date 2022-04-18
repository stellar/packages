# install

```shell
dnf install -y stellar-core-postgres
systemctl enable --now postgresql@core.service

sudo -s -u stellar sh -c 'cd /var/lib/stellar/core;
psql "postgresql:///postgres?host=/var/run/stellar" -c "CREATE DATABASE core";
stellar-core --conf /etc/stellar/stellar-core-postgres-public.cfg new-db;
stellar-core --conf /etc/stellar/stellar-core-postgres-public.cfg new-hist local'
systemctl enable --now stellar-core@public.service
```
