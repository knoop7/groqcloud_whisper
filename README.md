# Whisper STT Cloud API 集成到 Home Assistant 🏠🎙️


### 要求 📖

- **GroqCloud 账户** 👤  --> 你可以在[这里](https://console.groq.com/login)创建一个
- **API 密钥** 🔑 --> 你可以在[这里](https://console.groq.com/keys)生成一个

### 模型

GroqCloud 的所有 Whisper 模型每天免费使用最多 28800 秒音频！

- `whisper-large-v3`
- `distil-whisper-large-v3-en` - 优化版本的 *whisper-large-v3*

## 如何安装 ⚙️

在配置集成之前，必须先安装 `custom_integration`。你可以通过 HACS 或手动方式进行安装。

### HACS ✨

1. **复制** 这个 URL 并粘贴到你的 HACS 自定义仓库中：
    ```url
    https://github.com/knoop7/ha-openai-whisper-stt-api
    ```

2. **安装** 💻 `OpenAI Whisper Cloud` 集成
3. **重启** 🔁 Home Assistant

### 手动安装 ⌨️

1. **下载** 这个仓库
2. **复制** `custom_components` 文件夹中的所有内容到你的 Home Assistant 的 `custom_components` 文件夹中。
3. **重启** Home Assistant

## 配置 🔧

你可以配置以下参数：

- **`api_key`**: (必填) API 密钥
- **`proxy`**: (必填) 代理地址，需要搭配容器镜像
- **`temperature`**: (可选) 采样温度，范围在 0 到 1 之间。默认值 `0.4`
- **`prompt`**: (可选) 用于**提高语音识别**的准确性，特别是词汇或名称。默认值 `""`
  <br>提供一个由逗号 `, ` 分隔的词汇或名称列表
  <br>示例: `"open, close, Chat GPT-3, DALL·E"`。

现在你可以通过 Home Assistant 仪表盘进行设置（不支持 YAML 配置）。

## 镜像容器使用方法 🚀

### 拉取镜像

```bash
docker pull ghcr.io/knoop7/ha-openai-whisper-stt-api/groq-proxy2:20240830
```

### 运行镜像容器

```bash
docker run -d -p 8020:8020 \
  -e HOST="0.0.0.0" \
  -e PORT="8020" \
  -e PROXY_URL="" \ 
  -e AUDIO_URL="https://api.groq.com/openai/v1/audio/transcriptions" \
  -e TIMEOUT="60" \
  ghcr.io/knoop7/ha-openai-whisper-stt-api/groq-proxy2:20240830
```

#### 参数解释

- **`docker run -d`**: 以后台模式运行容器. 🖥️
- **`-p 8020:8020`**: 将主机的 8020 端口映射到容器的 8020 端口. 🔄
- **`-e HOST="0.0.0.0"`**: 设置容器内的环境变量 `HOST` 为 `0.0.0.0`，使容器监听所有网络接口. 🌐
- **`-e PORT="8020"`**: 设置容器内的环境变量 `PORT` 为 `8020`。🔢
- **`-e PROXY_URL=""`**: 设置容器内的环境变量 `PROXY_URL` 为 `""`，用于设置代理地址，这里为空. 🕵️‍♂️
- **`-e AUDIO_URL="https://api.groq.com/openai/v1/audio/transcriptions"`**: 设置容器内的环境变量 `AUDIO_URL` 为 `https://api.groq.com/openai/v1/audio/transcriptions`，指定音频转文字的 API 地址. 🎤
- **`-e TIMEOUT="60"`**: 设置容器内的环境变量 `TIMEOUT` 为 `60`，表示超时时间为 60 秒. ⏳
