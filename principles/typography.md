# Типографика

**Один шрифт — Inter.** Везде: в Google Slides, на сайтах, в email-шаблонах, в документации, в постерах, в интерфейсах.

Inter — нейтральный grotesque с сильной кириллицей и лучшей читаемостью на экране среди свободных аналогов. Лицензия OFL, доступен одной строкой в Google Slides и Google Docs. Это значит: ни один документ, который мы передаём наружу, не теряет шрифт при открытии у партнёра. Slides не подменяет его на Arial при экспорте.

**Чего не делаем.** Не используем Pragmatica Next в материалах, которые передаются наружу — у партнёра шрифта нет, ляжет на Times. Внутренние Figma-файлы — оставляем как есть. Не миксуем Inter с другим основным шрифтом «для разнообразия» — этого хватает.

## Weights

400 для body, 500 для подзаголовков, 600 для заголовков, 300 для крупных дисплейных надписей с разреженным эффектом, 700–800 для редких силовых акцентов.

## Подключение

**Google Slides / Google Docs.** Insert → Font → More fonts → ищем «Inter» → Add. После этого ставим как Theme font на весь шаблон.

**Web.** Через Google Fonts:

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

```css
font-family: 'Inter', sans-serif;
```

**Self-hosting.** Файлы — `github.com/google/fonts/tree/main/ofl/inter`. Variable TTF: `Inter[opsz,wght].ttf`. Лицензия OFL — можно класть в репозиторий.
