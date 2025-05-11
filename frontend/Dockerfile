# 使用 Node 22 构建
FROM node:22-slim

# 安装 pnpm
RUN npm install -g pnpm@10.5.2

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 lock 文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install

# 复制源代码
COPY . .

# 构建前端
RUN pnpm build

# 使用 nginx 提供静态文件服务
FROM nginx:alpine

# 复制构建的文件到 nginx 目录
COPY --from=0 /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 80 端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]