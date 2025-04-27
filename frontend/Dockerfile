# project/Dockerfile

# --- Stage 1: Build ---
# Use an official Node.js LTS version as a parent image (Alpine for smaller size)
# Check Nodejs.org for the current LTS version (e.g., 20)
FROM node:20-alpine AS builder

# Set the working directory in the container
WORKDIR /app

COPY . .
COPY package.json package-lock.json ./
COPY package*.json ./
# If using yarn:
# COPY yarn.lock ./

# Install dependencies using npm ci for cleaner installs matching lock file
RUN npm ci --legacy-peer-deps

RUN npm install
RUN rm -rf node_modules package-lock.json && npm install
RUN npm run build

# Copy the rest of the application code
# (Respects .dockerignore)
COPY . .

# Build the React app for production
# This runs the "build" script defined in your package.json (usually vite build)
RUN npm run build
# If using yarn:
# RUN yarn build

# --- Stage 2: Serve ---
# Use a lightweight Nginx image
FROM nginx:stable-alpine

# Remove default Nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output from the 'builder' stage to Nginx's web server directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (the port Nginx listens on inside the container)
EXPOSE 8000

# Command to run Nginx in the foreground when the container starts
CMD [ "nginx", "-g", "daemon off", "npm", "run", "dev"]


