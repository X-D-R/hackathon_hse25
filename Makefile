# Имя образа и контейнера
IMAGE_NAME=chatbot-dashboard
CONTAINER_NAME=chatbot-dashboard

run:
	docker run --rm -p 8501:8501 \
		-v $(PWD):/app \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

rebuild:
	docker build -t $(IMAGE_NAME) .
	make run

build:
	docker build -t $(IMAGE_NAME) .

clean:
	docker system prune -f
