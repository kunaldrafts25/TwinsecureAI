# Development Dockerfile for TwinSecure Frontend
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package files first to leverage Docker cache
COPY package*.json ./

# Install dependencies with legacy peer deps to handle version conflicts
RUN npm install --legacy-peer-deps

# Copy the rest of the application code
COPY . .

# Create a custom CSS file to fix styling issues
RUN echo "/* Override CSS to fix styling issues */\n\n/* Fix for red background */\nbody, html {\n  background-color: #f8fafc !important; /* slate-50 - light default */\n  margin: 0;\n  padding: 0;\n}\n\n/* Fix for loading screen */\n.loading-screen {\n  background-color: #1e293b !important; /* slate-800 */\n  position: fixed;\n  top: 0;\n  left: 0;\n  right: 0;\n  bottom: 0;\n  z-index: 9999;\n}\n\n/* Dark mode overrides */\n.dark body, .dark html {\n  background-color: #0f172a !important; /* slate-900 - dark default */\n}" > /app/src/override.css

# Update the main.tsx file to import the override CSS
RUN sed -i "s/import '.\/index.css';/import '.\/index.css';\nimport '.\/override.css'; \/\/ Import override CSS to fix styling issues/" /app/src/main.tsx

# Update the LoadingScreen component to use the loading-screen class
RUN sed -i 's/className="fixed inset-0 flex min-h-screen items-center justify-center bg-/className="loading-screen fixed inset-0 flex min-h-screen items-center justify-center bg-/' /app/src/components/common/LoadingScreen.tsx

# Update the vite.config.ts file to allow external access
RUN sed -i 's/export default defineConfig({/export default defineConfig({\n  server: {\n    host: "0.0.0.0",\n    port: 5173,\n    strictPort: true,\n    watch: {\n      usePolling: true,\n    },\n  },/' vite.config.ts

# Add environment variables for development
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost:8000/api/v1

# Expose port for Vite dev server
EXPOSE 5173

# Command to run the development server with host flag to ensure it's accessible
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
