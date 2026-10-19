# Вариант 36 — раздельные конвейеры development и main

Готовый учебный проект по дисциплине «DevOps инженерия».
Два самостоятельных файла GitHub Actions находятся в `.github/workflows/`.

## Репозиторий GitHub

Исходный код опубликован в https://github.com/dosz1974/CRODEOPS.
Ветки `main` и `development` содержат свои конфигурации конвейеров.
Актуальные результаты удаленных запусков доступны на странице
https://github.com/dosz1974/CRODEOPS/actions.

### Подтвержденные запуски 19 октября 2026 года

- development: https://github.com/dosz1974/CRODEOPS/actions/runs/39232342517
- main: https://github.com/dosz1974/CRODEOPS/actions/runs/39232347814

Оба запуска через Run workflow завершились успешно. В каждом выполнены
quality, build и deploy: Ruff, восемь тестов, сохранение и скачивание артефакта,
учебное развертывание и проверки HTTP 200 / 200 / 404.
Проверенный коммит: `1df4c6007dc13e393f58654c8aeb4f101897d37c`.

## Поведение

| Событие | development.yml | main.yml | Развертывание |
|---|---|---|---|
| push в development | quality → build → deploy | не запускается | development |
| push в main | не запускается | quality → build → deploy | production |
| ручной запуск development.yml из development | quality → build → deploy | не запускается | development |
| ручной запуск main.yml из main | не запускается | quality → build → deploy | production |
| PR с целью development | quality → build | не запускается | пропускается |
| PR с целью main | не запускается | quality → build | пропускается |
| push в feature/demo без PR | не запускается | не запускается | отсутствует |

Фильтр `pull_request.branches` проверяет целевую ветку PR.
При ручном запуске выбирайте соответствующую ветку. Проверка `quality`
пропускается при выборе другой ветки, поэтому build и deploy также не выполняются.
При PR development → main может также выполняться development-конвейер для
отдельного события push в development; PR-конвейер main развертывание не выполняет.

## Что реализовано

- HTTP-приложение на Python 3.12 без внешних библиотек времени выполнения.
- Ruff для проверки качества; восемь автоматических тестов unittest.
- Сборка `app.pyz` и `manifest.json` с веткой, Git SHA и контрольной суммой SHA-256.
- Передача собранного артефакта из build в deploy, без повторной сборки.
- Изолированные каталоги и GitHub environments development / production.
- Реальный запуск собранного приложения и HTTP-проверки `/health`, `/`, `/missing`.
- Запрет несовместимой ветки и среды; отклонение измененного артефакта.
- Зависимости quality → build → deploy останавливают дальнейшие этапы при ошибке.

Развертывание учебное: приложение запускается на runner, проходит HTTP-проверки
и останавливается. Runner и его каталог временные. Это не постоянный внешний
production-сервер. Для такого сервера этап deploy нужно заменить доставкой
артефакта на выбранную инфраструктуру и проверкой ее адреса.

## Локальный запуск

Необходимы Git, Python 3.12 и доступ к PyPI для установки средств проверки.
В архиве рядом с папкой project находится `repository.bundle` с обеими ветками.
Выполните из каталога, где лежит bundle:

```powershell
git clone repository.bundle branch-pipelines-demo
cd branch-pipelines-demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-ci.txt
git switch -c development --track origin/development
python scripts/local_ci.py --branch development
git switch main
python scripts/local_ci.py --branch main
```

В Linux/macOS активация: `source .venv/bin/activate`.
Если политика PowerShell запрещает активацию, запускайте `.venv\Scripts\python.exe`
вместо `python`; изменять системную политику не требуется.

`local_ci.py` выполняет те же команды проекта, что и файлы workflow.
Это локальная проверка, она не имитирует GitHub Actions, загрузку артефактов,
защиту environments или планировщик GitHub.

После запуска результаты лежат в `dist/development`, `dist/main`,
`.deploy/development` и `.deploy/production`. Для ручного просмотра приложения:

```powershell
$env:APP_ENV = 'development'
python .deploy/development/app.pyz --port 8000
```

Откройте http://127.0.0.1:8000/health. Завершение сервера: Ctrl+C.

## Запуск на GitHub

1. Создайте пустой репозиторий GitHub без README и лицензии.
2. После клонирования bundle удалите его локальный remote: `git remote remove origin`.
3. Добавьте URL своего репозитория: `git remote add origin ВАШ_URL`.
4. Отправьте main и development: `git push -u origin main development`.
5. При необходимости разрешите Actions в Settings → Actions → General.
6. В Settings → Environments создайте development и production. Для production
   разрешите deployment только из main, для development — только из development.
   Доступность правил зависит от плана GitHub и видимости репозитория.
7. Дождитесь двух запусков во вкладке Actions. Скачайте артефакты
   app-development-<Git SHA> и app-main-<Git SHA>, сохраните реальные скриншоты.
8. Для main настройте требование PR и успешной проверки `quality` через правила
   ветки. Если вводите required reviewers для production, deploy будет ждать
   одобрения; базовое решение выполняет его автоматически.

`ВАШ_URL` — ваш фактический URL, например адрес, выданный при создании репозитория.
Учетные данные и секреты для учебного runner-развертывания не нужны.

## Состав проекта

```text
.github/workflows/development.yml
.github/workflows/main.yml
app.py
requirements-ci.txt
pyproject.toml
scripts/build.py
scripts/deploy.py
scripts/local_ci.py
scripts/verify_workflows.py
tests/test_app.py
tests/test_deploy.py
```

Каталог evidence в ранее подготовленном архиве содержит реальные журналы
двух локальных запусков, манифесты и готовые артефакты. Эти журналы относятся
к локальной проверке. Результаты GitHub Actions нужно смотреть отдельно
во вкладке Actions опубликованного репозитория.

## Официальные источники

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://github.com/actions/checkout
- https://github.com/actions/setup-python
- https://github.com/actions/upload-artifact
- https://github.com/actions/download-artifact
- https://docs.python.org/3.12/library/zipapp.html
