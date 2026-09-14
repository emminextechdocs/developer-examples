# syntax=docker/dockerfile:1
FROM alpine:3.22.1 AS build
ARG CACHE_EPOCH=1
ARG LAB_RUN=manual
RUN --mount=type=secret,id=token,required=true \
    test -n "$LAB_RUN" && test -s /run/secrets/token && printf '%s\n' "$CACHE_EPOCH" > /artifact
FROM scratch
COPY --from=build /artifact /artifact
