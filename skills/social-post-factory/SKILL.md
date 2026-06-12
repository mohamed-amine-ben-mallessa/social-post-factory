---
name: social-post-factory
description: >
  Generate branded social media posts (Instagram square, story, banner/OG image) in one
  command with Photopea — free, no Photoshop. Use when the user wants to create a social
  post, IG post, story, banner, OG image, ad creative, or branded graphic from text. One
  brand theme drives all formats. Keywords: social post, instagram, story, banner, OG
  image, ad creative, branded graphic, content, marketing visual, photopea.
license: MIT
---

# social-post-factory — branded posts in one command

Compose on-brand social graphics with the **photopea MCP** (free browser Photoshop). The
first tool call opens a browser window (expected). Three formats, one theme, a clean ramp.

## Formats
- **square** 1080×1080 — IG/FB/LinkedIn feed
- **story** 1080×1920 — IG/FB/TikTok stories
- **banner** 1200×630 — Open Graph / Twitter card / blog header

## The recipe (square example)
```
create_document(1080,1080, fillColor="#16182e")
add_layer("bg"); add_gradient(target="bg", type="linear", colors=["#16182e","#283276"], angle=120)
add_shape(rectangle, bounds={x:90,y:150,width:120,height:12}, fillColor="#f5d76e")   # accent bar
add_text(content="EYEBROW", x:90, y:205, size:30, color="#f5d76e", bold:true, letterSpacing:4)
add_text(content="Headline",      x:88, y:320, size:84, color="#ffffff", bold:true)
add_text(content="accent line",   x:88, y:430, size:84, color="#f5d76e", bold:true)
add_text(content="Subtitle here", x:92, y:580, size:36, color="#c9cde0")
add_shape(rectangle, bounds={x:90,y:740,width:380,height:92}, fillColor="#f5d76e")   # CTA
add_text(content="Call to action", x:120, y:770, size:38, color="#16182e", bold:true)
add_text(content="@handle", x:90, y:1005, size:32, color="#8b90b0", bold:true)
export_image(outputPath="post.png", format="png")
```
For story (1080×1920) push the headline block to ~y:320 and the CTA to ~y:1500. For banner
(1200×630) use a 92px hero and start at y:150.

## Design system (keep it consistent)
- **One accent color** (here gold #f5d76e). Warm dark gradient bg, never pure #000/#fff.
- **Type ramp:** eyebrow (small, tracked, accent) → hero (big, bold, white + one accent
  line) → subtitle (muted). One easy idea per post.
- Keep text inside safe margins (~90px). If a hero line overflows, size it down.
- Match canvas to the platform; export PNG.

## Tool args (verified)
`add_text` uses **`content`**; `export_image` uses **`outputPath`**+`format`; `add_shape`
bounds use **`{x,y,width,height}`**; gradient targets an existing layer (add_layer first).

A ready multi-format runner: `scripts/post_factory.py` (edit the THEME block to rebrand).
