// MathJax 3 (локальная копия tex-svg.js, без CDN).
// tags: "ams" включает нумерацию \begin{equation} и ссылки \eqref.
// Разделители \( \) и \[ \] формирует pymdownx.arithmatex (generic: true).
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "ams"
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  },
  svg: { fontCache: "global" }
};
