
upgrade:
	docker exec -it almacen flask db upgrade
downgrade:
	docker exec -it almacen flask db downgrade
migrate:
	docker exec -it almacen flask db migrate
revision:
	docker exec -it almacen flask db revision --autogenerate -m $(name)
current:
	docker exec -it almacen flask db current
bash:
	docker exec -it almacen /bin/bash