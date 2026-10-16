# 和君设计语言 · Hejun Design Language

适用于 Codex 的和君品牌设计 Skill。基于用户提供的和君红 V2026 官方 PPT 模板、集团简介，以及事业部和研究中心历史材料提炼。

支持 PPT、Word、PDF、HTML 的制作和排版改版。默认采用 **和君红 V2026**，历史青蓝风格按需求延续。包含官方空白 PPT、原始 Logo、主题色 token、推导 Word/HTML starter、格式指南及辅助脚本。

> 本项目是从材料提炼的工作规范，并非和君品牌部门发布的完整 VI 手册。Word、HTML 和推荐字号等扩展规则均注明为推导值。字体未随仓库分发。

## 在 Codex 中安装

向 Codex 发送：

```text
请用 $skill-installer 安装这个 Skill：
https://github.com/ZiqiCode/Hejun-Design-Language/tree/main/.agents/skills/hejun-design-language
```

如果使用安装器命令：

```sh
python <skill-installer目录>/scripts/install-skill-from-github.py --repo ZiqiCode/Hejun-Design-Language --path .agents/skills/hejun-design-language
```

安装后在下一轮对话使用；若客户端尚未刷新，可重新启动 Codex。也可在 Codex 打开克隆后的仓库，使用仓库内 `.agents/skills/`。

## 使用示例

```text
用 $hejun-design-language 把这份项目资料制作成一份 12 页中文客户提案 PPT，使用和君红，保留可编辑图表。
```

```text
用 $hejun-design-language 把这份 Word 研究报告重新排版，并导出 PDF，保留原文事实和来源。
```

```text
用 $hejun-design-language 根据这份需求制作响应式 HTML，交付离线单文件和可编辑源文件夹。
```

```text
用 $hejun-design-language 延续这份旧稿的青蓝风格，改善排版，验证后替换到原位置。
```

“替换原位置”只在具体任务要求时执行。Skill 不会自动上传附件、联系客户或发布网页。

## 内容与证据

- [Skill 入口](.agents/skills/hejun-design-language/SKILL.md)
- [设计规范](.agents/skills/hejun-design-language/references/design-system.md)
- [来源与证据](.agents/skills/hejun-design-language/references/source-evidence.md)
- [原始主题色和推荐版式](.agents/skills/hejun-design-language/assets/tokens.json)
- [官方五页 PPT 模板](.agents/skills/hejun-design-language/assets/templates/hejun-official-red-v2026.pptx)
- [Word starter](.agents/skills/hejun-design-language/assets/templates/hejun-starter.docx)
- [HTML starter](.agents/skills/hejun-design-language/assets/templates/hejun-starter.html)
- [验证记录](VALIDATION.md)

已对 31 份 PPTX/PDF（共 1,147 个页/幻灯片，含同名与版本重复）做结构清点，并抽样观察历史版式；官方五页模板做全页渲染检查。仓库不收录历史业务正文、客户案例或联系名单。完整证据边界见来源文档。

![官方和君红空白封面](.agents/skills/hejun-design-language/assets/previews/official-slide-1.png)

## 权利说明

和君品牌名称、Logo、背景和原始模板的权利归各自权利人。本项目不授予第三方使用、转售或再许可这些品牌资产的权利。字体按实际文件许可使用；不捆绑来源未核实的字体。

结构参考 [DeepStone Design Language](https://github.com/lajayliu2-ops/deepstone-design-language)，和君规范、素材映射与辅助代码重新编写。此仓库未设置覆盖品牌素材的通用开源许可。
