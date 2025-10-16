# Stage 1: Base image
FROM node:alpine AS base
WORKDIR /frontend

# Install deps
COPY package.json package-lock.json ./
RUN npm install

# Copy project sources
COPY . .

# Stage 3: Development server
FROM base AS dev
CMD ["npm", "run", "dev"]

# Stage 4: Build the application
FROM base AS build
RUN npm run build

# Stage 5: Production server using Nginx
FROM nginx:alpine AS prod
# Copy the built application from the 'build' stage
COPY --from=build /frontend/dist /usr/share/nginx/html
# Copy the custom Nginx configuration
COPY --from=build /frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]