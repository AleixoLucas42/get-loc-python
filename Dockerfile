FROM python:3.10.17-slim-bullseye AS build

WORKDIR /app

RUN apt-get update && apt-get install -y binutils gcc

COPY . .

RUN pip3 install -r requirements.txt
RUN pyinstaller --onefile main.py

FROM python:3.10.17-slim-bullseye AS final

WORKDIR /app

COPY --from=build /app/dist/main /app/main

ENTRYPOINT ["./main"]

