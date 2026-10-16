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
- 初版 Word 示例使用 Microsoft YaHei。后续已补充官方 HarmonyOS Sans SC 字体，当前 Word starter 和其 PDF 参考仍保留初版；新增字体的验证见下方记录。不将旧版渲染记录当作鸿蒙字体的 Office 验证。
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


## 2026-10-16 字体补充验证

- 从华为官方包提取 Light、Regular、Medium、Bold 四个 TTF，逐个与 ZIP 内原字节比较，SHA-256 一致；原始许可不变。source.json 记录下载地址和原包散列。
- 四个字体的 OS/2.fsType 均为 8（Editable Embedding）。没有转换字体格式、修改原 TTF 或子集化。
- Microsoft Edge headless 在未系统安装鸿蒙字体的情况下加载网页本地 TTF；Regular 400、Medium 500、Bold 700 三个 FontFace 均为 loaded。
- 经 Chrome DevTools Protocol 检查 h1 实际使用 HarmonyOS Sans SC、isCustomFont=true、glyphCount>0。不是仅检查 CSS 声明。
- 阻断 HTTP/HTTPS 网络后，源文件和离线单文件截图完全一致；390 px 窄屏无文档横向溢出，表格可滚动；查看了新版桌面与窄屏 PNG。
- PyMuPDF 直接从原版 Regular TTF 生成测试 PDF，无需系统安装。提取 PDF 内字体流，与原版 TTF 字节完全相同，中文可搜索；测试页已渲染查看。该测试不表示现有 Word 参考 PDF 已改为鸿蒙字体。
- 辅助脚本回归现为 8 项通过，新增原版字体/许可散列和初始化时字体复制检查。
- 本次没有验证 Word/PPT 的无系统安装字体加载或字体嵌入，不承诺所有 Office 阅读器免安装编辑。旧 Word starter 和 PDF 参考保留初版微软雅黑。
- 详细浏览器及 PDF 证据见 `.agents/skills/hejun-design-language/references/font-validation.json`。
