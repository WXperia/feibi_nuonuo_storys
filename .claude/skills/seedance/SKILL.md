# Seedance 2.0 分镜脚本 Skill

## 触发条件

用户说「写分镜」「生成 Seedance 提示词」「写成能丢给 AI 视频的格式」「按 Seedance 标准写」时激活本 skill。

---

## 本 Skill 的输出目标

把剧本场次翻译成**可直接丢给 Seedance 2.0 生成的分镜表**，每个镜头包含：
- 时长（≤ 11 秒，推荐 3–7 秒）
- 首帧参考图编号（@image 几）
- 英文 I2V 提示词（10–30 词，只写运动）
- 配音 / 音效说明

## 核心原则：所有有画面的镜头全部 I2V

> T2V（纯文本生成）无法保证角色一致性，每次生成人物面孔必然跑偏。
> 正确做法：先用 Midjourney / Flux 生成首帧参考图，再上传 Seedance 做 I2V。
> I2V 提示词只描述「运动」，Seedance 负责让首帧动起来，不负责决定画面长什么样。
>
> 唯一例外：纯字卡、黑屏、屏幕文字打出等镜头，用剪辑软件做，不用 Seedance。

---

## 第一步：确认前置信息

开始写分镜前，先确认（可一次性问）：

1. **角色参考图状态**：是否已有 @image1～@image4 的参考图？没有的话需要先写生成参考图的提示词。
2. **单集目标时长**：2 分钟 / 2 分 30 秒 / 5 分钟？
3. **画面风格**：动漫 / 半写实 / 全写实 / 其他？确认后写进每镜的 Style 字段。

---

## 第二步：提示词公式

### I2V（图生视频）公式 — 所有有画面的镜头使用

```
[Motion description] + [Camera movement] + [What stays static]
```

字数要求：**10–30 词**。图里已有的内容不要写，只描述运动。

### 参考：T2V 公式（仅用于无人物的纯场景开场镜头）

```
[Subject] + [Action] + [Setting] + [Camera] + [Style] + [Lighting]
```

字数要求：**20–60 词**。但本项目优先用 I2V，T2V 作为备用。

### 六个字段的标准写法

| 字段 | 正确示例 | 错误示例 |
|------|---------|---------|
| Subject | `a young woman with blue-grey long hair, silver jacket` | `a person` / `a girl` |
| Action | `slowly picks up a glowing chip and holds it close` | `does something with the chip` |
| Setting | `rain-soaked cyberpunk junkyard, neon reflections on wet ground` | `outside` |
| Camera | `slow dolly forward` / `static locked shot` / `orbit left` | `moving camera` / `cool angle` |
| Style | `cyberpunk anime style, 85mm portrait lens, shallow depth of field` | `cinematic` / `cool style` |
| Lighting | `single pink-blue neon rim light from left, deep shadow on right` | `nice lighting` / `cinematic lighting` |

---

## 第三步：核心规则（每镜都要遵守）

### 规则 1：每镜只写一个镜头运动

```
✅ slow dolly forward
✅ pan left across scene
✅ static locked shot, no movement
❌ pan left while dollying in and tilting up
```

多个运动叠加 = 画面抖动 + 生成失败。

### 规则 2：永远不写 "fast"

速度用物理效果描述：

```
❌ fast car chase
✅ tires screeching on wet asphalt, suspension compressing through sharp turns
❌ running fast
✅ she sprints, footsteps splashing puddles, jacket trailing behind
```

### 规则 3：光线是最高 ROI 元素

每个镜头都要写具体光线，这一行提升质量最明显：

```
❌ nice lighting
❌ cinematic lighting
✅ harsh unshielded neon from above, deep chiaroscuro shadows below
✅ golden hour backlight, long shadows, dust particles lit in beam
✅ single cold blue screen glow as only light source on her face
```

### 规则 4：I2V 只写运动，不重描场景

```
❌（I2V 错误）A young woman in silver jacket stands in a junkyard. She slowly picks up a chip.
✅（I2V 正确）She slowly reaches down and picks up a small object. Camera holds static.
```

### 规则 5：单镜只给一个主体一个动作

```
❌ the man walks left while the woman dances and the drone flies overhead
✅ 拆成三个镜头分别写
```

### 规则 6：角色一致性靠 @ 引用

每次生成菲比或糯糯的镜头，都在上传界面附上对应参考图，提示词里写：

```
Use @image1 for character identity.（生成糯糯时）
Use @image2 for character identity.（生成菲比时）
```

---

## 第四步：镜头运动关键词速查表

| 运动类型 | 英文关键词 |
|---------|----------|
| 向主体推近 | `slow dolly forward` / `gentle push in` |
| 向后拉远 | `dolly back` / `slow pull out` |
| 水平扫移 | `slow pan left` / `pan right across scene` |
| 垂直扫移 | `slow tilt up` / `tilt down to reveal` |
| 环绕 | `orbit left around subject` / `slow 360-degree arc` |
| 跟随 | `tracking shot following from the side` |
| 固定机位 | `static locked shot, no camera movement` |
| 手持晃动 | `handheld camera with slight natural shake` |
| 俯拍 | `overhead drone shot` / `bird's eye view` |
| 主观视角 | `POV first-person view` |

---

## 第五步：分镜表输出格式（每集标准模板）

````markdown
**[镜 XX]** Xs | @imageN（说明） | 中文一句话场景说明

```
PROMPT:
（英文 I2V 提示词，10–30 词，只写运动）
```
`AUDIO:` 配音台词 / 音效说明
````

### AUDIO 字段规范

AUDIO 只写两类内容，不写 BGM：

| 类型 | 示例 |
|------|------|
| 对白 | 糯糯：「出去。」/ 菲比啾比（小声）：「哎呀。」|
| 环境音效 | 雨声、管道滴水声、无人机嗡鸣声、金属碰撞声、电流声 |

> BGM 是后期混音环节统一处理的，不在分镜脚本里逐镜指定。
> 如果某个场次有整体的情绪节奏提示，写在场次标题行的括号里，不写进每个镜头的 AUDIO。

示例：

````markdown
**[镜 09]** 4s | @image7（糯糯手腕特写） | 她捡起芯片，终端弹出红色警告

```
PROMPT:
Hand picks up the chip. Wrist terminal flashes red. She taps to dismiss.
Chip glows brighter in palm. Slight camera push into hand.
```
`AUDIO:` 糯糯（平淡）：「不兼容。」警告音被打断又重启。
````

---

## 第六步：哪些镜头不需要 Seedance

以下类型直接用剪辑软件做，省生成额度：

| 镜头类型 | 制作方式 |
|---------|---------|
| 字卡（「30 分钟前」「第 X 集」） | Pr / CapCut 文字动效 |
| 屏幕逐行打字特效 | 静态图 + 打字动效插件 |
| 纯黑屏 + 声音 | 剪辑软件 |
| 集末片尾字卡 | 剪辑软件 |

## 第七步：参考图库规范（每集都要先建好）

每集开始前，按以下分类生成参考图：

| 编号 | 内容 | 用途 |
|------|------|------|
| @image1 | 主角角色参考图（正面全身） | 所有主角出现的镜头 |
| @image2 | 配角/对立角色参考图（正面全身） | 所有该角色出现的镜头 |
| @image3～@imageN | 场景参考图（无人物） | 对应场景的镜头首帧 |
| 合成图 | @image1 + @image3 合成（人物在场景里） | 双元素镜头首帧 |

> 合成图用 Photoshop / Canva / 任意图层工具把角色图扣背景后叠到场景图上。
> 每次 Seedance I2V 时上传对应合成图，提示词只写运动。

---

## 附：本项目角色参考图生成提示词

> 用 Midjourney 或 Flux 生成，再存为 @image1～@image4 供 Seedance I2V 使用。

### @image1 糯糯

```
Portrait of a 20-year-old East Asian young woman.
Blue-grey long hair covering ears (small dim glowing neural interface visible behind left ear).
Silver-grey short jacket, dark work trousers, expression calm and slightly detached.
Soft blue neon backlight, cyberpunk lower-city atmosphere.
Anime-realistic hybrid style. 85mm portrait lens.
```

### @image2 菲比啾比

```
Portrait of a digital holographic girl, semi-transparent glowing appearance.
Gold hair, oversized vivid purple eyes, white cap, silver-white jacket with white fox emblem on back.
Pink-blue data particles and glitch effects surrounding her, cheerful exaggerated expression.
Black background to isolate transparency. Anime style. Full body visible.
```

### @image3 数据垃圾场

```
Dystopian cyberpunk data junkyard. Massive mechanical sorting arms over piles of discarded
neural implants. Iron canopy roof with rain dripping through gaps. Far background: glowing
pink-blue idol advertisement screen on skyscraper. Puddles reflecting neon. Dark, gritty.
No people. Wide establishing shot, 24mm wide angle.
```

### @image4 白色办公室

```
Ultra-minimal white office room, no windows. Large monitor casting blue light.
Silent red warning alarm light on wall. White desk. Cold, sterile, corporate.
Wide angle, completely static.
```

---

## 常见失败原因速查

| 症状 | 原因 | 修复 |
|------|------|------|
| Generation failed | 提示词超 100 词 / 内容违规 | 删减到 60 词以内，删掉名人/品牌词 |
| 画面抖动/崩坏 | 叠加了多个镜头运动 | 只保留一个运动指令 |
| 角色换脸 | 没有 @ 引用参考图 | 上传参考图并在提示词注明 @image1 |
| 运动模糊/拖影 | 写了 "fast" | 改用物理描述速度 |
| Stuck 不出结果 | 多主体各自运动 / 矛盾指令 | 拆镜 / 删矛盾描述 |
| I2V 出来的和图不像 | I2V 提示词重描了场景 | 只写运动，删掉场景描述 |
