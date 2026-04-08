# VantaVault Product UI Styleguide

Этот документ фиксирует общую дизайн-систему проекта и служит опорой для `web/` интерфейса, GitHub-витрины и будущих экранов.

## Design Principles

- интерфейс должен выглядеть как продуктовый desktop tool, а не как декоративный concept;
- основа визуала: чистая сетка, читаемые контрасты, предсказуемые размеры и единые состояния;
- акцент используется дозированно и только для primary actions, focus и активного состояния;
- длинный текст всегда разбивается на короткие строки и не выходит за контейнеры.

## Color Tokens

| Token | Value | Purpose |
| --- | --- | --- |
| `--bg` | `#0A0D12` | основной фон |
| `--bg-canvas` | `#07090D` | нижний слой и большие фоны |
| `--surface-1` | `rgba(16, 19, 25, 0.92)` | панели и оболочки |
| `--surface-2` | `rgba(22, 27, 35, 0.96)` | усиленные карточки и модалки |
| `--surface-3` | `rgba(255, 255, 255, 0.04)` | hover/secondary layers |
| `--border` | `rgba(255, 255, 255, 0.10)` | стандартная граница |
| `--border-strong` | `rgba(255, 255, 255, 0.18)` | активная граница |
| `--text` | `#F5F7FA` | основной текст |
| `--text-secondary` | `#AEB7C2` | вторичный текст |
| `--text-tertiary` | `#7F8996` | подписи и caption |
| `--brand` | `#5B8CFF` | primary action |
| `--brand-strong` | `#4C79E6` | pressed / active primary |
| `--focus` | `rgba(91, 140, 255, 0.22)` | focus ring |
| `--success` | `#72D39A` | success / healthy state |
| `--danger` | `#FF8C8C` | error / warning state |

## Typography Scale

| Token | Use |
| --- | --- |
| `--type-display` | крупный product headline |
| `--type-h1` | главный заголовок секции |
| `--type-h2` | заголовок панели |
| `--type-subtitle` | descriptive label |
| `--type-body` | основной текст |
| `--type-body-sm` | компактный текст |
| `--type-caption` | captions, eyebrow, helper |
| `--type-button` | кнопки и action labels |

## Spacing

Базовая шкала:

- `4px`
- `8px`
- `16px`
- `24px`
- `32px`
- `48px`

Использование:

- внутренняя плотность controls: `8px` или `16px`;
- стандартный gap между блоками: `16px`;
- расстояние между крупными секциями: `24px` или `32px`;
- крупные модальные и shell-container отступы: `24px`.

## Radius

| Token | Value |
| --- | --- |
| `--radius-0` | `0px` |
| `--radius-1` | `4px` |
| `--radius-2` | `8px` |
| `--radius-3` | `16px` |
| `--radius-pill` | `999px` |

Правило:

- inputs и buttons: `8px`;
- cards и panels: `16px`;
- chips и status pills: `999px`.

## Elevation

| Token | Purpose |
| --- | --- |
| `--elevation-0` | flat |
| `--elevation-1` | subtle separation |
| `--elevation-2` | standard product card |
| `--elevation-3` | modal / floating emphasis |

## Component Rules

### Buttons

- primary button использует `--brand`;
- secondary / ghost button строится на `surface + border`;
- на hover меняется border и слегка поднимается elevation;
- на focus используется ring, а не только смена border.

### Inputs

- высота и padding должны совпадать с кнопками;
- ошибку, hover и focus нужно показывать явно;
- placeholder и helper copy остаются вторичными по контрасту.

### Chips

- chips короткие и компактные;
- выбранное состояние выделяется бордером и мягким accent fill;
- chip не должен быть выше обычной кнопки.

### Cards

- card всегда имеет читаемую внутреннюю сетку;
- title, body и actions не должны визуально прилипать друг к другу;
- текст внутри card должен жить в безопасной ширине.

## GitHub Visual Rules

- SVG-витрина использует ту же типографическую и spacing систему;
- верхние control chips и CTA должны стоять по центровочной сетке;
- в hero нельзя ставить плавающие блоки поверх главного заголовка;
- длинные строки должны быть разбиты заранее, без надежды на авто-рендер GitHub.
