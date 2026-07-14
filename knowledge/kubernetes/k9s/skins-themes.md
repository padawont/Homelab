---
title: "k9s Skins and Custom Views"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k9s
  - kubernetes
  - tooling
  - customization
  - skins
sources:
  - url: "https://k9scli.io/topics/skins"
    title: "k9s — Skins"
  - url: "https://k9scli.io/topics/columns"
    title: "k9s — Custom Views"
  - url: "https://k9scli.io/topics/config"
    title: "k9s — Configuration"
  - url: "https://github.com/derailed/k9s/tree/master/skins"
    title: "k9s Sample Skins — GitHub"
last_audit_date: 2026-07-10
---

# k9s Skins and Custom Views

## Skins Overview

Skins are YAML files that customize the k9s UI colors. Skin files live in `$XDG_CONFIG_HOME/k9s/skins/<name>.yaml`.

### Applying a Skin

Three levels of skin configuration, applied in order (last wins):

| Level | Configuration |
|---|---|
| Global | `skin: <name>` in `$XDG_CONFIG_HOME/k9s/config.yaml` |
| Per-context | `skin: <name>` in `$XDG_DATA_HOME/k9s/clusters/<cluster>/<context>/config.yaml` |
| Environment | `export K9S_SKIN="<name>"` |

Source: [k9s Skins — Overview](https://k9scli.io/topics/skins)

## Skin YAML Structure

```yaml
# $XDG_CONFIG_HOME/k9s/skins/in_the_navy.yaml
k9s:
  body:
    fgColor: dodgerblue
    bgColor: '#ffffff'
    logoColor: '#0000ff'

  info:
    fgColor: lightskyblue
    sectionColor: steelblue

  frame:
    border:
      fgColor: dodgerblue
      focusColor: aliceblue
    menu:
      fgColor: darkblue
      keyColor: cornflowerblue
      numKeyColor: cadetblue
    crumbs:
      fgColor: white
      bgColor: steelblue
      activeColor: skyblue
    status:
      newColor: '#00ff00'
      modifyColor: powderblue
      addColor: lightskyblue
      errorColor: indianred
      highlightcolor: royalblue
      killColor: slategray
      completedColor: gray
    title:
      fgColor: aqua
      bgColor: white
      highlightColor: skyblue
      counterColor: slateblue
      filterColor: slategray

  views:
    table:
      fgColor: blue
      bgColor: darkblue
      cursorColor: aqua
      header:
        fgColor: white
        bgColor: darkblue
        sorterColor: orange
    yaml:
      keyColor: steelblue
      colonColor: blue
      valueColor: royalblue
    logs:
      fgColor: white
      bgColor: black
```

Source: [k9s Skins — Skin Configuration](https://k9scli.io/topics/skins)

## Named Color Reference

Colors can be specified by name (case-insensitive) or hex value (e.g. `'#ffffff'`). Use `default` to inherit the terminal's background color.

| Color | Hex | Color | Hex |
|---|---|---|---|
| black | `#000000` | maroon | `#800000` |
| green | `#008000` | olive | `#808000` |
| navy | `#000080` | purple | `#800080` |
| teal | `#008080` | silver | `#c0c0c0` |
| gray | `#808080` | red | `#ff0000` |
| lime | `#00ff00` | yellow | `#ffff00` |
| blue | `#0000ff` | fuchsia | `#ff00ff` |
| aqua | `#00ffff` | white | `#ffffff` |
| aliceblue | `#f0f8ff` | antiquewhite | `#faebd7` |
| aquamarine | `#7fffd4` | azure | `#f0ffff` |
| beige | `#f5f5dc` | bisque | `#ffe4c4` |
| blanchedalmond | `#ffebcd` | blueviolet | `#8a2be2` |
| brown | `#a52a2a` | burlywood | `#deb887` |
| cadetblue | `#5f9ea0` | chartreuse | `#7fff00` |
| chocolate | `#d2691e` | coral | `#ff7f50` |
| cornflowerblue | `#6495ed` | cornsilk | `#fff8dc` |
| crimson | `#dc143c` | darkblue | `#00008b` |
| darkcyan | `#008b8b` | darkgoldenrod | `#b8860b` |
| darkgray | `#a9a9a9` | darkgreen | `#006400` |
| darkkhaki | `#bdb76b` | darkmagenta | `#8b008b` |
| darkolivegreen | `#556b2f` | darkorange | `#ff8c00` |
| darkorchid | `#9932cc` | darkred | `#8b0000` |
| darksalmon | `#e9967a` | darkseagreen | `#8fbc8f` |
| darkslateblue | `#483d8b` | darkslategray | `#2f4f4f` |
| darkturquoise | `#00ced1` | darkviolet | `#9400d3` |
| deeppink | `#ff1493` | deepskyblue | `#00bfff` |
| dimgray | `#696969` | dodgerblue | `#1e90ff` |
| firebrick | `#b22222` | floralwhite | `#fffaf0` |
| forestgreen | `#228b22` | gainsboro | `#dcdcdc` |
| ghostwhite | `#f8f8ff` | gold | `#ffd700` |
| goldenrod | `#daa520` | greenyellow | `#adff2f` |
| honeydew | `#f0fff0` | hotpink | `#ff69b4` |
| indianred | `#cd5c5c` | indigo | `#4b0082` |
| ivory | `#fffff0` | khaki | `#f0e68c` |
| lavender | `#e6e6fa` | lavenderblush | `#fff0f5` |
| lawngreen | `#7cfc00` | lemonchiffon | `#fffacd` |
| lightblue | `#add8e6` | lightcoral | `#f08080` |
| lightcyan | `#e0ffff` | lightgoldenrodyellow | `#fafad2` |
| lightgray | `#d3d3d3` | lightgreen | `#90ee90` |
| lightpink | `#ffb6c1` | lightsalmon | `#ffa07a` |
| lightseagreen | `#20b2aa` | lightskyblue | `#87cefa` |
| lightslategray | `#778899` | lightsteelblue | `#b0c4de` |
| lightyellow | `#ffffe0` | limegreen | `#32cd32` |
| linen | `#faf0e6` | mediumaquamarine | `#66cdaa` |
| mediumblue | `#0000cd` | mediumorchid | `#ba55d3` |
| mediumpurple | `#9370db` | mediumseagreen | `#3cb371` |
| mediumslateblue | `#7b68ee` | mediumspringgreen | `#00fa9a` |
| mediumturquoise | `#48d1cc` | mediumvioletred | `#c71585` |
| midnightblue | `#191970` | mintcream | `#f5fffa` |
| mistyrose | `#ffe4e1` | moccasin | `#ffe4b5` |
| navajowhite | `#ffdead` | oldlace | `#fdf5e6` |
| olivedrab | `#6b8e23` | orange | `#ffa500` |
| orangered | `#ff4500` | orchid | `#da70d6` |
| palegoldenrod | `#eee8aa` | palegreen | `#98fb98` |
| paleturquoise | `#afeeee` | palevioletred | `#db7093` |
| papayawhip | `#ffefd5` | peachpuff | `#ffdab9` |
| peru | `#cd853f` | pink | `#ffc0cb` |
| plum | `#dda0dd` | powderblue | `#b0e0e6` |
| rebeccapurple | `#663399` | rosybrown | `#bc8f8f` |
| royalblue | `#4169e1` | saddlebrown | `#8b4513` |
| salmon | `#fa8072` | sandybrown | `#f4a460` |
| seagreen | `#2e8b57` | seashell | `#fff5ee` |
| sienna | `#a0522d` | skyblue | `#87ceeb` |
| slateblue | `#6a5acd` | slategray | `#708090` |
| snow | `#fffafa` | springgreen | `#00ff7f` |
| steelblue | `#4682b4` | tan | `#d2b48c` |
| thistle | `#d8bfd8` | tomato | `#ff6347` |
| turquoise | `#40e0d0` | violet | `#ee82ee` |
| wheat | `#f5deb3` | whitesmoke | `#f5f5f5` |
| yellowgreen | `#9acd32` | | |

Source: [k9s Skins — Named Color Reference](https://k9scli.io/topics/skins)

## Custom Views (Column Configuration)

Customize which columns appear in resource table views via `$XDG_CONFIG_HOME/k9s/views.yaml`. Uses GVR (Group/Version/Resource) keys.

```yaml
# $XDG_CONFIG_HOME/k9s/views.yaml
views:
  v1/pods:
    sortColumn: AGE:asc
    columns:
      - AGE
      - NAMESPACE|WR          # Wide mode only, right-aligned
      - NAME
      - IP
      - NODE
      - STATUS
      - READY
      - MEM/RL|S              # Show even when not in wide mode

  v1/services:
    columns:
      - AGE
      - NAMESPACE
      - NAME
      - TYPE
      - CLUSTER-IP
```

### Column Attributes

| Attribute | Meaning |
|---|---|
| `T` | Time column indicator |
| `N` | Number column indicator |
| `W` | Only visible in wide mode |
| `S` | Visible (overrides default wide-only) |
| `H` | Hidden |
| `L` | Left-aligned (default) |
| `R` | Right-aligned |

### JSON Parse Expressions

Extract values from the resource manifest into custom columns:

```yaml
views:
  v1/pods:
    columns:
      - ZORG:.metadata.labels.fred\.io\.kubernetes\.blee
      - BLEE:.metadata.annotations.blee|R   # Right-aligned annotation value
```

Column syntax: `COLUMN_NAME<:json_parse_expression><|column_attributes>`

### Per-Namespace Views (v0.40.6+)

```yaml
views:
  v1/pods@fred:              # Pod view in namespace "fred"
    sortColumn: NAME:asc
    columns:
      - NAME|WR
      - AGE
  v1/pods@kube*:             # Regex-based namespace matching
    columns:
      - NAME
      - AGE
      - LABELS
```

### Per-Context Views

Custom views for a specific cluster/context at `$XDG_DATA_HOME/k9s/clusters/<cluster>/<context>/views.yaml`.

Source: [k9s Custom Views page](https://k9scli.io/topics/columns)
