docker run -p 5080:5080 -e ZO_ROOT_USER_EMAIL=a@gmail.com -e ZO_ROOT_USER_PASSWORD=1234 openobserve/openobserve:latest
docker run -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest
docker run -e POSTGRES_PASSWORD=1234 -p 54320:5432 postgres