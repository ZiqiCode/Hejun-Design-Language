# 字体加载与免安装交付

本工具使用 HarmonyOS Sans Fonts。Copyright 2021 Huawei Device Co., Ltd.

## 来源和许可

字体来自华为官方地址：
https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip

从包内 `HarmonyOS Sans/HarmonyOS_Sans_SC/` 提取 Light、Regular、Medium、Bold 四个 TTF。原始字节不变，散列见 `assets/fonts/source.json`。原始 `LICENSE.txt` 保持不变；`LICENSE-readable.txt` 保留完整协议正文，仅清理末尾 NUL 填充和换行。HTML starter 也保留完整许可正文。

许可允许随软件使用、嵌入、打包和再分发未经修改的字体，要求显著说明使用该字体、保留版权及完整协议，并禁止字体单独分发或销售。本仓库作为排版工具配套使用字体，不是独立字体下载站。不要从本仓库抽出字体作为独立产品分发。

不修改字形、元数据，不做字体格式转换或字形子集化。保留原版 TTF。全字体嵌入会增大成品体积；需要缩小文件时先与用户说明体积/字体选择的取舍，不静默改造字体。

已读取这四个 TTF 的 OS/2 表：fsType=8（Editable Embedding）。嵌入权限位和许可正文是不同层面的检查，两者都要保留。此信息不保证每个文档引擎和阅读器都支持该字体。

## 先加载文件，再考虑替代

1. 获取当前任务需要的仓库 TTF、许可和 source.json，校验 SHA-256。
2. 优先使用能指定字体文件路径的渲染/制作工具。可用任务级字体目录、进程内注册或工具字体搜索目录，但要实际验证制作进程看到了字体。
3. 系统字体列表没有 HarmonyOS Sans SC，不代表字体文件不能用。不要立即改用微软雅黑。
4. 当前工具确实无法加载或嵌入时说明限制；未经验证不承诺免安装编辑。用户明确允许替代时，记录真实字体和换行变化。
5. 不自动进行系统级安装或持久用户字体安装。任务级加载与系统安装区分说明。

## HTML

starter 用 `@font-face` 加载原版 Regular 400、Medium 500、Bold 700，不使用 `local()`，使检查针对配套文件。Light 300 仅在版式确实需要时增加，正文不用 Light。

`init_deliverable.py` 复制字体、许可和来源清单到输出源目录。`build_standalone_html.py` 将 CSS 引用的完整 TTF 编为 data URI，保留正文和许可，读取者不需要安装字体。只要没有远程展示资源，离线也能加载。

等待 `document.fonts.ready`，确认 FontFace 的 status 为 loaded，并检查含中文的真实页面。仅看到 computed font-family 不能证明字体加载成功。测试期间禁止 HTTP/HTTPS 请求，再检查字体、图片和页面宽度。

三个字重原始约 24.6 MB，Base64 后约 33 MB；四个字重会更大。不要无条件在每份 HTML 加载四个字重。

## PDF

用支持字体文件路径和完整字体嵌入的工具。以原版 TTF 加载，保证文字可搜索，不把文字轮廓化或截图化来冒充嵌入。

注意：浏览器、ReportLab、某些 Office/PDF 导出器可能默认子集化。不能假定它们符合本工作流的完整嵌入策略。导出后检查实际 PDF 字体表、嵌入流和是否带子集前缀，必要时换用能完整嵌入的导出路径。PDF 里的字体家族名称本身不证明嵌入成功。

## Word 和 PPT

TTF 放在文件夹里不会让 Word/PowerPoint 自动识别。制作进程必须能加载字体，再使用支持完整字体嵌入的保存选项。

Windows 的 FR_PRIVATE 字体加载仅对调用进程有效。在 Python 进程加载字体，不代表另一个 Word COM 进程能看到它。不要用这种方式声称 Office 字体可用。其他平台和文档引擎也要验证各自的字体发现方式。

交付 DOCX/PPTX 时启用完整嵌入，不启用“仅嵌入所用字符”。检查文件包中的真实字体部件与关系：DOCX 通常为 `word/fonts/`、fontTable 及相关关系；PPTX 通常为字体部件和 embeddedFontLst。存在字体部件仍需核对对应字体及使用范围，并用目标阅读器检查。Office 为存储字体进行的规范化封装/可逆混淆不等于允许修改原 TTF。

需要接收端继续编辑时，明确目标软件与版本。某些在线阅读器或第三方 Office 不支持同样的嵌入行为；“仓库包含字体”不等于“所有软件无需安装即可编辑”。如果制作工具不能完成这条链，保留可编辑文件并说明字体限制，可以另交经过验证的嵌入字体 PDF 或离线 HTML。

原有 `hejun-starter.docx` 与 `hejun-reference.pdf` 保留初版微软雅黑内容，不宣称已经嵌入鸿蒙字体。它们提供版式起点，后续任务须执行字体重应用和验证。

## 授权与工具参考

- 华为官方字体包：上方下载地址（使用与包内许可一起核对）。
- OpenHarmony 官方资源仓库的同类许可：https://github.com/openharmony/resources/blob/master/LICENSE_Fonts
- Microsoft 字体嵌入说明：https://support.microsoft.com/en-us/office/fonts/benefits-of-embedding-custom-fonts
