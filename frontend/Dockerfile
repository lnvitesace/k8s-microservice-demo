FROM nginx:alpine
COPY nginx.conf /etc/nginx/
RUN echo "<h1>Hello World</h1>" > /usr/share/nginx/html/index.html
CMD ["nginx", "-g", "daemon off;"]
