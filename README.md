### Hexlet tests and linter status:
[![Actions Status](https://github.com/i-evgenii/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/i-evgenii/devops-engineer-from-scratch-project-313/actions)

[![Tests and format](https://github.com/i-evgenii/devops-engineer-from-scratch-project-313/actions/workflows/push.yml/badge.svg)](https://github.com/i-evgenii/devops-engineer-from-scratch-project-313/actions/workflows/push.yml)

```
make install
make test
make run
```

docker build -t crud-app .
docker run -p 5173:5173 -p 8080:8080 --env-file .env crud-app