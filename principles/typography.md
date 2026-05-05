# Типографика

**Основной шрифт — Manrope.** Везде, где это возможно — в Google Slides, на сайтах, в email-шаблонах, в документации, в постерах.

Manrope — geometric sans с тёплым «техно» характером, который ложится на визуальный код студии. Лицензия OFL, доступен одной строкой в Google Slides и Google Docs. Это значит: ни один документ, который мы передаём наружу, не теряет шрифт при открытии у партнёра. Slides не подменяет его на Arial при экспорте.

**Запасной — Inter.** Только для плотных интерфейсов, мелких подписей и табличных данных, где Manrope может казаться слишком «бренд-голосовым». Не использовать в заголовках и постерах.

**Чего не делаем.** Не используем Pragmatica Next в материалах, которые передаются наружу — у партнёра шрифта нет, ляжет на Times. Внутренние Figma-файлы — оставляем как есть.

## Weights

Базовые: 400 для body, 500 для подзаголовков, 600 для заголовков, 300 для крупных дисплейных надписей с разреженным эффектом, 700–800 для редких силовых акцентов.

## Подключение

**Google Slides / Google Docs.** Insert → Font → More fonts → ищем «Manrope» → Add. После этого ставим как Theme font на весь шаблон.

**Web.** Через Google Fonts:

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

```css
font-family: 'Manrope', sans-serif;
```

**Self-hosting.** Файлы — `github.com/google/fonts/tree/main/ofl/manrope`. Variable TTF: `Manrope[wght].ttf`. Лицензия OFL — можно класть в репозиторий.
