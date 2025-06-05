# Paper-Agent

一款可以帮助经常阅读论文的同学提升效率的小工具，有两个部分：

- HuggingFace Weekly Paper 制作工具
- Arxiv Helper

## 前置条件

翻译基于 `deepseek` 的服务， 论文十问依赖于 `kimi`， 因此需要这两个的 api key。可以配置到环境变量中，代码中使用的环境变量 key 分别是

- DEEPSEEK_KEY
- KIMI_KEY

如果不想同时用两家，翻译可以考虑也换成 kimi，需要手动修改代码，将 deepseek 里面的设置换成 kimi 的。

## 1. HuggingFace Weekly Paper 制作工具

我每周博客和公众号上都会发一篇 weekly paper，文章来源于 HuggingFace 的 Daily Paper。 为了减少每次都要一个个点进去通过 N 次复制粘贴来得到翻译后的结果的痛苦，写了个脚本，可以直接读取本周的点赞超过 n 次的论文，并生成 Weekly Paper。

代码就是 hf.py 文件，运行 `weekly_paper` 方法即可，慢慢等待即可，如果出现了一些翻译上的问题或者接口异常，可以重新从目录下的 output.md 文件里面拿到英文原版继续人工处理。

此脚本依赖的模型是 `deepseek`。 翻译 prompt 来自于微博上宝玉老师的分享。
