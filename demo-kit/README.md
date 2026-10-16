# Open WebUI 可落地 Demo

本包将 Open WebUI 与 Ollama 放在同一 Docker Compose 网络中，首次启动后下载 `qwen3:0.6b` 小模型，让你在不填写商业 API 密钥的情况下完成一轮聊天。它使用官方镜像，不重复打包上游仓库代码或模型文件。上游：[open-webui/open-webui](https://github.com/open-webui/open-webui)；你的 Fork：[2514827566zzx-dev/open-webui](https://github.com/2514827566zzx-dev/open-webui)。

## 启动

需要 Docker Engine/Desktop、Docker Compose v2+、Python 3 和可下载镜像/模型的网络。建议至少 4 GB 可用内存和数 GB 磁盘。`qwen3:0.6b` 模型下载约 523 MB；镜像体积另计。

1. 解压后执行 `python3 start.py`。脚本生成本地 `.env` 密钥、校验配置、拉取镜像、启动容器，并从 Ollama 官方模型库拉取 `qwen3:0.6b`。
2. 执行 `python3 verify.py`；预期得到 `HTTP 200`。若首次下载还没完成，稍等并查看 `docker compose logs -f open-webui`。
3. 打开 `http://127.0.0.1:3102`，创建第一个管理员账号，在模型选择器选 `qwen3:0.6b`，复制 `examples/first-chat.txt` 的提问并发送。应看到本地模型的文字回答。

镜像：Open WebUI `v0.12.3`、Ollama `0.40.5`。聊天记录和模型文件分别保存在 Docker 命名卷中。停止：`docker compose down`；该命令不删除卷。

## 部署边界

默认只监听 `127.0.0.1:3102`。远程服务器上可用 `ssh -L 3102:127.0.0.1:3102 用户@服务器` 访问。若要公开给别人使用，需要先设置 HTTPS、账号与权限、模型资源限制，再考虑放开监听地址。此包不含 GPU 配置；在 CPU 上的小模型回答可能较慢，质量也不能代表更大的模型。

参考：[Open WebUI 官方快速安装](https://docs.openwebui.com/getting-started/quick-start/) 和 [Ollama 模型标签](https://ollama.com/library/qwen3/tags)。
