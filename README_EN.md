[简体中文](./README.md) | **English**

# LitematicaViewer v0.7.2

### Minecraft tool - A tool to easily check Litematica files

[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/v/release/Albertchen857/LitematicaViewer)]()
[![三连](https://img.shields.io/badge/-一键三连-00A1D6?logo=bilibili&logoColor=white)](https://www.bilibili.com/video/BV1H9ZVYtEta/?spm_id_from=333.1387.homepage.video_card.click&vd_source=20c164cb28b2da114329d8728dad750f)
[![转发](https://img.shields.io/badge/-转发-00A1D6?logo=bilibili&logoColor=white)](https://space.bilibili.com/3494373232741268)
[![YoutubeIntro](https://img.shields.io/badge/-Youtube-00A1D6?logo=youtube&logoColor=red)](https://www.youtube.com/watch?v=0nofWrfKJeg)

GITHUB Link: https://github.com/albertchen857/LitematicaViewer
Please give a star! I want Stars~ Target 100 stars

A light Viewer for Litematica files

- `Input file` Input your file first and choose a mode to check your file.
- `Output` Output Litematica analysis data into a file or chart. (Text File & Excel File)
- `Classification Output` Output Litematica analysis data with classification into a file or chart. (Text File & Excel File)
- `Simple Analysis` Used for easy checking of block numbers and names (no properties).
- `Container Analysis` Analyze containers with items inside, showing items and basic info.
- `Spawn Regular Shape` A Light Tool to generate a regular shape.
- `Fill Specific Block` A Light Tool to replace multiple types of blocks with your own set limitations.
- `3D Rendering` 3D Rendering for Litematic files.
- `Transfer Litematic File Version` Transfer 1.21 Litematic files into older versions (1.16 ~ 1.12).
- `UI ColorMap` Change the theme color. (Classic Blue, Light Green, Darkly, Dark Blue, Pink)

# Branch Diagram

```
LitematicaViewer
|- Analysis
| |- Simple Analysis
| |- Container Analysis
| | |- Normal Analysis
| | |- Classification Analysis (In development)
| |- Full Analysis (Closed)
|- Output
| |- Normal Output (txt/csv)
| |- Classification Output (txt/csv)
|- Statistics
| |- Basic Statistics (Redstone/Median/Other)
| |- Composition Statistics (Block Pie Chart)
| |- 3D Rendering (Rotating/Static)
|- Functionality
| |- Generate Polygon Schematic
| | |- Cube Generation
| | |- Special Shape Generation (In development)
| |- Replace Specific Block
| |- Transfer Schematic Version (1.17/1.15/1.12)
|- UI
  |- Font/Color/Layout Customization UI update (V0.7)
```
