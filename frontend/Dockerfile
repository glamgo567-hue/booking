FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
ARG VITE_BOOKING_AUTO_CANCEL_SECONDS
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_BOOKING_AUTO_CANCEL_SECONDS=$VITE_BOOKING_AUTO_CANCEL_SECONDS
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
