# Как развернуть проект в Docker:
Запустите терминал. Убедитесь, что вы находитесь в той же
директории, где сохранён Dockerfile, и запустите сборку образа:
```
docker build -t <image name> . 
```
Просмотреть образы в терминале:
```
docker image ls 
```
Запуск контейнера (если запуск из windows, дописать в начало строки 'winpty'):
```
docker run --env-file ./.env --name <container name> -it  -p 10080:80 <image name>
```
Просмотр всех контейнеров:
``` 
docker container ls -a
```
Запустить контейнер:
```
docker container stop <CONTAINER ID> 
```
Остановить контейнер:
```
docker container start <CONTAINER ID> 
```
Список всех команд для работы с контейнером можно вызвать через:
```
docker container 
```