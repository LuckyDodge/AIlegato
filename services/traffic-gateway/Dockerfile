FROM golang:1.22-alpine AS build

WORKDIR /src
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN go build -o /out/traffic-gateway ./cmd/gateway

FROM alpine:3.20

RUN adduser -D appuser
USER appuser
COPY --from=build /out/traffic-gateway /usr/local/bin/traffic-gateway

EXPOSE 8080
ENTRYPOINT ["traffic-gateway"]
