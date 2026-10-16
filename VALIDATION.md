# 验证记录

日期：2026-10-16。此记录区分结构、渲染和实际行为验证。

| 项目 | 结果 | 验证范围 |
| --- | --- | --- |
| Skill frontmatter / 命名 | 通过 | skill-creator 的 quick_validate.py；以 Python UTF-8 模式运行 |
| 内部 Markdown 链接 | 通过 | 仓库内相对链接逐项检查目标存在 |
| 官方 PPT 一致性 | 通过 | 与用户提供的原模板 SHA-256 相同，无原位修改 |
| 官方 PPT 视觉 | 通过 | Microsoft PowerPoint 将 5 页导出为 1600×900 PNG，查看封面及五页总览 |
| Word starter | 通过 | 可编辑正文、样式、原生表格、重复表头、动态 PAGE 字段；Microsoft Word 导出两页 PDF，逐页检查最终修订版 PNG |
| HTML 初始化 | 通过 | 生成独立目录；转义用户标题；拒绝覆盖已有目录 |
| HTML 桌面与窄屏 | 通过 | Microsoft Edge headless，经 Playwright 检查 1440 px 和 390 px 视口；图片完整，文档无横向溢出，窄屏表格可横向滚动 |
| HTML 离线打包 | 通过 | 阻断 HTTP/HTTPS；0 次远程展示请求；源文件与单文件桌面截图 PNG 字节一致 |
| HTML 打印 | 通过 | 浏览器导出 A4 PDF，两页渲染检查，表头/内容/来源无裁切 |
| 辅助脚本回归 | 通过 | 6 项 unittest：资源嵌入、相对路径、越界/远程拒绝、未支持形式拒绝、输入转义、不覆盖、token 导出一致性 |
| 品牌资产清单 | 通过 | asset-provenance.json 记录并校验每个资产 SHA-256；单文件小于 50 MiB |

## 环境与限制

- bundled render_docx.py 因环境没有 LibreOffice soffice.exe 无法运行；诊断后改用本机 Microsoft Word 导出 PDF，再渲染为 PNG。没有将未执行的 LibreOffice 检查写成通过。
- 示例 Word 使用本次已安装的 Microsoft YaHei 字体；HarmonyOS Sans SC 未提供字体文件，未测试该字体在其他机器上的排版。字体文件均未随仓库分发。
- PPT 复用原官方模板，不声称把整页图片组成的 V2026 集团简介恢复成可编辑正文。
- 历史文件做结构清点与抽样视觉观察，不是全部 1,147 页的逐页视觉审核。
- 单文件打包器仅支持文档化的静态资源形式，拒绝未支持结构；不解析任意 JavaScript 内的资源请求。
- 没有使用独立新会话测试 Skill 的自动触发；脚本、模板和规则的验证不能替代今后每份成品的内容和视觉检查。

## 重跑辅助脚本检查

```sh
python -m unittest discover -s tests -v
python .agents/skills/hejun-design-language/scripts/export_tokens.py
python .agents/skills/hejun-design-language/scripts/init_deliverable.py /new/output --title "项目名称"
python .agents/skills/hejun-design-language/scripts/build_standalone_html.py /new/output/index.html
```

初始化和打包命令拒绝覆盖已有输出。需要重跑时选择新的临时输出位置。
