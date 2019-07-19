drc: ../gemma-documentregistratiecomponent/env/bin/python ../gemma-documentregistratiecomponent/src/manage.py runserver 8000
zrc: ../gemma-zaakregistratiecomponent/env/bin/python ../gemma-zaakregistratiecomponent/src/manage.py runserver 8003
nrc: ../gemma-notificatiecomponent/env/bin/python ../gemma-notificatiecomponent/src/manage.py runserver 8005
alfresco: docker-compose -f alfresco/docker-compose.yml up

bing: ../BInG/env/bin/python ../BInG/src/manage.py runserver 8002
utrechtdemo: ../utrecht-demo/env/bin/python ../utrecht-demo/src/manage.py runserver 8004

celery_nrc: ../gemma-notificatiecomponent/env/bin/celery worker -A notifications --workdir ../gemma-notificatiecomponent/src -l debug
celery_bing: ../BInG/env/bin/celery worker -A bing --workdir ../BInG/src -l debug

outway: docker run --volume ~/nlx-setup/root.crt:/certs/root.crt:ro --volume ~/nlx-setup/org.crt:/certs/org.crt:ro --volume ~/nlx-setup/org.key:/certs/org.key:ro --env DIRECTORY_INSPECTION_ADDRESS=directory-inspection-api.demo.nlx.io:443 --env TLS_NLX_ROOT_CERT=/certs/root.crt --env TLS_ORG_CERT=/certs/org.crt --env TLS_ORG_KEY=/certs/org.key --env DISABLE_LOGDB=1 --publish 12018:8080 nlxio/outway:latest
