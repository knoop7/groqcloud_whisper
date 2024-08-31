# const.py

# 组件域名
DOMAIN = "groqcloud_whisper"

# 配置常量
CONF_PROMPT = "prompt"  # 提示文本
CONF_TEMPERATURE = "temperature"  # 温度参数
CONF_LINK = "代理URL"  # 自定义 API 代理 URL

# 支持的模型列表
SUPPORTED_MODELS = [
    "whisper-large-v3"  # 目前支持的 Whisper 模型
]

# 支持的语言列表
SUPPORTED_LANGUAGES = [
    "zh",  # 中文
    "en"   # 英文
]

# 默认值设置
DEFAULT_NAME = "GroqCloud Whisper"  # 默认名称
DEFAULT_URL = ""  # 默认的 API 代理 URL（空字符串表示未设置）
DEFAULT_WHISPER_MODEL = SUPPORTED_MODELS[0]  # 默认 Whisper 模型
DEFAULT_PROMPT = ""  # 默认提示文本（空字符串表示无提示）
DEFAULT_TEMPERATURE = 0.4  # 默认温度参数
