## Compose
It works correctly, except for using the env variable from secrets.env.
2 options:
1. Change the name to .env and put it in the docker/compose folder
2. export the env variabe

```bash
export DB_PASSWORD=<Your password>
cd docker/compose
docker compose up
```

## One image

I don't really know why, but it doesn't let me connect through python, even though it works with the start.sh.