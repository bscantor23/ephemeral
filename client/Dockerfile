# Stage 1: Build Flutter Web
FROM ghcr.io/cirruslabs/flutter:3.24.0 AS builder

WORKDIR /app

# Disable analytics and enable web support
RUN flutter config --no-analytics && \
    flutter config --enable-web

# Copy dependency definition and download packages
COPY pubspec.yaml ./
RUN flutter pub get

# Copy source and build static web release
COPY . .
RUN flutter pub get && \
    flutter build web --release

# Stage 2: Serve static bundle with Nginx
FROM nginx:1.27-alpine

COPY --from=builder /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
