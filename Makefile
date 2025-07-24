.PHONY: run, dev, build, rebuild, rebuild_dev, clean

IMAGE_NAME=chatbot-dashboard
CONTAINER_NAME=chatbot-dashboard

ifeq ($(OS),Windows_NT)
	HOST_DIR := $(shell cd)
else
	HOST_DIR := $(shell pwd)
endif

# Запуск в режиме продакшн
run:
	docker compose up

# Запуск в режиме разработки
dev:
	docker compose -f docker-compose.dev.yml up

# Сборка продакшн-образа
build:
	docker compose build

# Пересборка и запуск
rebuild:
	docker compose build && docker compose up

# Пересборка и запуск в режиме разработки
rebuild_dev:
	docker compose build && docker compose -f docker-compose.dev.yml up

# Очистка образов и контейнеров
clean:
	docker rm -f $(CONTAINER_NAME) || true
	docker rmi -f $(IMAGE_NAME) || true
