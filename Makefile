# Имя образа и контейнера
IMAGE_NAME=chatbot-dashboard
CONTAINER_NAME=chatbot-dashboard

ifeq ($(OS),Windows_NT)
	HOST_DIR := $(shell cd)
else
	HOST_DIR := $(shell pwd)
endif

ifeq ($(OS),Windows_NT)
	HOST_DIR := $(shell cd)
else
	HOST_DIR := $(shell pwd)
endif

run:
	docker run --rm -p 8501:8501 \
		-v "$(HOST_DIR):/app" \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

build:
	docker build -t $(IMAGE_NAME) .

rebuild: build run

rebuild: build run

clean:
	docker rm -f $(CONTAINER_NAME) || true
	docker rmi -f $(IMAGE_NAME) || true
