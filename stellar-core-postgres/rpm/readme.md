# What is this

stellar-core-postgres is a meta-package with dependencies and configs
to run postgresql service and stellar-core in one command.

# How it works

```shell
dnf install -y stellar-core-postgres # will install stellar-core and postgresql-server
systemctl enable --now stellar-core@public.service
```
// TODO: translation needed
При запуске `postgresql@core.service` мы наследуем `postgresql@.service` из пакета `postgresql-server`.
Изменения заключаются только в том, что процесс будет работать от системного пользователя `stellar`, в его пространстве.
Оригинальный юнит постгреса перед запуском сервиса выполняет скрипт /usr/libexec/postgresql-check-db-dir
для проверки наличия БД, ее версии, и соответсвия с версии БД с версией исполняемого файла.
Перед запуском проверки мы выполняем инициализацию кластера постгри (/usr/libexec/stellar/init-db-core), если его нет.

Запуск `stellar-core@public.service` требует работающего сервиса постгри (он описан выше `postgresql@core.service`).
Перед запуском скрипт `/usr/libexec/stellar/init-stellar-core` проверяет наличие папки `buckets`.
В случае ее отсутсвия, через юникс сокет постгри выполняется создание БД, схемы, и настройка папок истории транзакций.

// TODO: need stellar-core@testnet.service
