/* The audit pass of `book audit` (bookkit/audit.py): run in the browser once the book is paginated and its footers are
 * drawn, it measures the finished pages and returns what is crooked on them - no screenshots, only the DOM.
 *
 * Evaluated as one function of `opts` (the thresholds, from bookkit/design.py); returns a list of findings
 * `{check, severity, page, chapter, where, detail, numbers, rect}`: `where` is a short snippet of the text concerned,
 * `rect` the box to mark on the page's contact sheet, in CSS pixels from the page's top left corner.
 */
(opts) => {
  const findings = [];
  const probe = document.createElement('div');
  probe.style.cssText = 'position:absolute;width:100mm;height:0';
  document.body.append(probe);
  const PX = probe.getBoundingClientRect().width / 100;        // CSS pixels in a millimetre
  probe.remove();
  const MM = (px) => Math.round(px / PX * 10) / 10;
  const report = window.__bookReport || {};
  const feet = new Map((report.feet || []).map((f) => [f.page, f]));
  const pages = [...document.querySelectorAll('#book > .page')];
  const snippet = (text, n = 60) => String(text || '').replace(/\s+/g, ' ').trim().slice(0, n);

  let current = null;                                           // the page being audited
  function add(check, severity, where, detail, numbers = {}, box = null, page = current) {
    let rect = null;
    if (page && box) {
      const sheet = page.getBoundingClientRect();
      const r = box.getBoundingClientRect ? box.getBoundingClientRect() : box;
      rect = { x: r.left - sheet.left, y: r.top - sheet.top, w: r.width, h: r.height };
    }
    findings.push({ check, severity, page: page ? +page.dataset.page : 0, chapter: page ? page.dataset.chapter || '' : '',
                    where: snippet(where), detail, numbers, rect });
  }
  const union = (a, b) => {
    const left = Math.min(a.left, b.left), top = Math.min(a.top, b.top);
    const right = Math.max(a.right, b.right), bottom = Math.max(a.bottom, b.bottom);
    return { left, top, right, bottom, width: right - left, height: bottom - top };
  };
  const overlaps = (a, b, air = 1) => a.left < b.right - air && b.left < a.right - air &&
                                      a.top < b.bottom - air && b.top < a.bottom - air;
  const styles = new WeakMap();
  const style = (el) => { if (!styles.has(el)) styles.set(el, getComputedStyle(el)); return styles.get(el); };

  // ------------------------------------------------------------------ the lines of a block of text
  /* A block (a paragraph, a list item, a table cell) as words and the gaps between them, each word with the line it
   * starts on; a word the line breaks inside is cut into pieces, one per line. Every measurement is a Range over one
   * character or one run of spaces, so it is the browser's own layout, glyph by glyph. */
  const BLOCKS = 'p, li, td, th';
  const SPACE = /[ \t\n\r ]/;
  const range = document.createRange();
  function charBox(node, i) {
    range.setStart(node, i);
    range.setEnd(node, i + 1);
    for (const r of range.getClientRects()) if (r.width > 0 || r.height > 0) return r;
    return null;
  }
  function textNodes(block) {
    const out = [];
    const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const parent = node.parentElement;
      if (!parent || parent.closest('svg') || parent.closest(BLOCKS) !== block) continue;
      out.push(node);
    }
    return out;
  }
  function model(block) {
    const fontSize = parseFloat(style(block).fontSize) || 16;
    const lineHeight = parseFloat(style(block).lineHeight) || fontSize * 1.5;
    const tokens = [];                                          // words and runs of space, in reading order
    let word = null, space = null;
    for (const node of textNodes(block)) {
      const text = node.data;
      for (let i = 0; i < text.length; i++) {
        if (SPACE.test(text[i])) {
          word = null;
          if (!space) { space = { kind: 'space', parts: [] }; tokens.push(space); }
          const last = space.parts[space.parts.length - 1];
          if (last && last.node === node && last.end === i) last.end = i + 1;
          else space.parts.push({ node, start: i, end: i + 1 });
        } else {
          space = null;
          if (!word) { word = { kind: 'word', chars: [] }; tokens.push(word); }
          word.chars.push({ node, i, ch: text[i] });
        }
      }
    }
    // Lines: a character a line lower than the line being read opens the next one.
    const lines = [];
    const lineAt = (top) => {
      let k = lines.length - 1;
      while (k >= 0 && top < lines[k].top - lineHeight / 2) k--;
      if (k >= 0 && top <= lines[k].top + lineHeight / 2) return k;
      lines.push({ top, pieces: [], gaps: [] });
      return lines.length - 1;
    };
    let previous = null;                                        // the piece read last, and the space after it
    let pendingSpace = null;
    for (const token of tokens) {
      if (token.kind === 'space') { pendingSpace = token; continue; }
      const { chars } = token;
      const first = charBox(chars[0].node, chars[0].i);
      const last = charBox(chars[chars.length - 1].node, chars[chars.length - 1].i);
      if (!first || !last) { pendingSpace = null; continue; }
      // Cut the word where its line changes (binary search: the characters of one word go down, never up).
      const cuts = [0];
      let from = 0, fromTop = first.top;
      while (Math.abs(last.top - fromTop) > lineHeight / 2) {
        let lo = from + 1, hi = chars.length - 1;
        while (lo < hi) {
          const mid = (lo + hi) >> 1;
          const r = charBox(chars[mid].node, chars[mid].i);
          if (r && r.top > fromTop + lineHeight / 2) hi = mid; else lo = mid + 1;
        }
        const r = charBox(chars[lo].node, chars[lo].i);
        if (!r || lo <= from) break;
        cuts.push(lo);
        from = lo;
        fromTop = r.top;
      }
      cuts.push(chars.length);
      for (let c = 0; c + 1 < cuts.length; c++) {
        const part = chars.slice(cuts[c], cuts[c + 1]);
        const box = c === 0 ? first : charBox(part[0].node, part[0].i);
        if (!box) continue;
        const line = lineAt(box.top);
        const piece = { chars: part, text: part.map((x) => x.ch).join(''), line, box, word: token, broken: c > 0 };
        if (c === 0 && previous && previous.line === line && pendingSpace) {
          // The gap between two words of one line: the width of the space between them, as set.
          let width = 0, em = fontSize;
          for (const { node, start, end } of pendingSpace.parts) {
            range.setStart(node, start);
            range.setEnd(node, end);
            for (const r of range.getClientRects()) width += r.width;
            em = parseFloat(style(node.parentElement).fontSize) || fontSize;
          }
          if (width > 0) lines[line].gaps.push({ em: width / em, after: previous });
        }
        lines[line].pieces.push(piece);
        previous = piece;
      }
      pendingSpace = null;
    }
    // A line ending in a <br>, and the last line unless it is justified too, are set ragged.
    const ragged = new Set([lines.length - 1]);
    if (style(block).textAlignLast === 'justify') ragged.delete(lines.length - 1);
    for (const br of block.querySelectorAll('br')) {
      if (br.closest(BLOCKS) !== block) continue;
      range.selectNode(br);
      const r = range.getBoundingClientRect();
      const k = lines.findIndex((l) => Math.abs(l.top - r.top) <= lineHeight / 2);
      if (k >= 0) ragged.add(k);
    }
    return { lines, ragged, lineHeight, fontSize };
  }
  const lineText = (line) => line.pieces.map((p) => p.text).join(' ');
  const lineBox = (line) => line.pieces.map((p) => p.box).reduce(union);

  // ------------------------------------------------------------------ text: gaps, line starts and ends, code, numbers
  function auditText(page) {
    for (const block of page.querySelectorAll(`.p-body ${BLOCKS.split(', ').join(', .p-body ')}`)) {
      if (block.closest('svg, pre, .screen')) continue;
      const { lines, ragged } = model(block);
      if (!lines.length) continue;
      const justified = style(block).textAlign === 'justify';
      const running = justified && block.matches('.main > p, .main li');
      lines.forEach((line, k) => {
        if (!line.pieces.length) return;
        const first = line.pieces[0];
        const last = line.pieces[line.pieces.length - 1];
        // 2. Wide word gaps in a justified line.
        if (justified && !ragged.has(k) && line.gaps.length) {
          const mean = line.gaps.reduce((s, g) => s + g.em, 0) / line.gaps.length;
          const most = Math.max(...line.gaps.map((g) => g.em));
          if (mean > opts.gapMean || most > opts.gapMax) {
            add('word-gap', 'warning', lineText(line),
                `a justified line with wide gaps between its words: mean ${mean.toFixed(2)} em, widest ${most.toFixed(2)} em`,
                { mean_em: +mean.toFixed(2), max_em: +most.toFixed(2) }, lineBox(line));
          }
        }
        // 6. A line that starts with a punctuation mark, or with a dash that belongs to the line above.
        if (k > 0) {
          const ch = first.text[0];
          if (/[,.;:)!?»…]/.test(ch) && first.broken) {          // a word of its own may begin with a dot (.env)
            add('line-start', 'error', lineText(line), `a line starts with "${ch}", which belongs at the end of the line above`,
                {}, lineBox(line));
          } else if (/[—–]/.test(ch) && !first.broken) {
            add('line-start', 'warning', lineText(line), 'a line starts with a dash that should stay on the line above ' +
                '(a no-break space before it)', {}, lineBox(line));
          }
        }
        const end = last.chars[last.chars.length - 1];
        if (/[-‐‑]{2}$/.test(last.text) && !end.node.parentElement.closest('code')) {   // `--` in code is typed so
          add('double-hyphen', 'error', lineText(line), `a line ends with a doubled hyphen: "${last.text.slice(-12)}"`,
              {}, lineBox(line));
        }
      });
      // 5 and 9. A break inside a word: inside a bit of code it must fall at a space, slash, hyphen or dot; never
      // between two digits of a number.
      for (const line of lines) {
        for (const piece of line.pieces) {
          if (!piece.broken) continue;
          const chars = piece.word.chars;
          const at = chars.indexOf(piece.chars[0]);
          const before = chars[at - 1], after = chars[at];
          const codeA = before.node.parentElement.closest('code'), codeB = after.node.parentElement.closest('code');
          if (codeA && codeA === codeB && !/[\s/\-.]/.test(before.ch)) {
            add('code-break', 'error', codeA.textContent,
                `inline code broken across lines inside a token: "${chars.slice(Math.max(0, at - 12), at).map((x) => x.ch).join('')}` +
                `|${chars.slice(at, at + 12).map((x) => x.ch).join('')}"`, {}, codeA);
          } else if (/\d/.test(before.ch) && /[\d.,%]/.test(after.ch) || /[\d]/.test(after.ch) && /[.,]/.test(before.ch)) {
            add('number-break', 'error', piece.word.chars.map((x) => x.ch).join(''),
                'a number broken across lines', {}, block);
          }
        }
      }
      // 8. The last line of a paragraph: one short word alone.
      const row = block.closest('.row');
      if (running && lines.length > 1 && !block.classList.contains('cut') &&
          !(row && row.classList.contains('split-head') && block.matches('.main > p:last-child'))) {
        const line = lines[lines.length - 1];
        const letters = line.pieces.length === 1 ? line.pieces[0].text.replace(/[^\p{L}\p{N}]/gu, '') : '';
        if (letters && letters.length < opts.shortWord) {
          add('hanging-word', 'warning', lineText(lines[lines.length - 2]) + ' / ' + lineText(line),
              `the last line of a paragraph is one short word: "${line.pieces[0].text}"`, {}, lineBox(line));
        }
      }
    }
  }

  // ------------------------------------------------------------------ the page as a whole
  const BOXES = '.quote-card, .bubble, .terminal, .code, .crt, .sheet, .tree, table, .callout, .steps, .prompt';
  function textRects(root, skip) {
    const out = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.data.trim() || node.parentElement.closest('svg') || (skip && node.parentElement.closest(skip))) continue;
      range.selectNodeContents(node);
      for (const r of range.getClientRects()) if (r.width > 0) out.push({ el: node.parentElement, rect: r });
    }
    return out;
  }

  function auditPage(page) {
    const number = +page.dataset.page;
    const full = page.classList.contains('full');
    const body = page.querySelector(':scope > .p-body');
    const foot = page.querySelector(':scope > .p-foot');
    const record = feet.get(number);
    if (full || !body) return;
    const sheet = page.getBoundingClientRect();
    const area = body.getBoundingClientRect();
    const footTop = foot ? foot.getBoundingClientRect().top : sheet.bottom;
    const rows = [...body.children];
    let lowest = area.top;
    for (const row of rows) {
      lowest = Math.max(lowest, row.getBoundingClientRect().bottom);
      for (const note of row.querySelectorAll(':scope > .side > *')) lowest = Math.max(lowest, note.getBoundingClientRect().bottom);
    }
    const lastOfChapter = record && record.end === 'last';
    // 1. A hole above the footer.
    const hole = (footTop - lowest) / PX - opts.bodyGap;
    if (!lastOfChapter && hole > opts.hole) {
      const why = record ? (record.end === 'stuck' ? `the next block (${record.blocker || 'block'}) could not move up`
        : record.end === 'break' ? 'the chapter breaks the page here' : 'the next text could have filled it') : '';
      add('hole', 'warning', snippet(rows.length ? rows[rows.length - 1].textContent.slice(-80) : '', 40),
          `${hole.toFixed(0)} mm empty above the footer (${record ? record.size : '?'})${why ? '; ' + why : ''}`,
          { hole_mm: Math.round(hole), footer: record ? record.size : '', end: record ? record.end : '',
            blocker: record ? record.blocker : '' },
          { left: area.left, top: lowest, right: area.right, bottom: footTop, width: area.width, height: footTop - lowest });
    }
    // 15. A page with next to nothing on it.
    if ((lowest - area.top) / PX < opts.blank) {
      add('blank-page', 'warning', body.textContent.slice(0, 60),
          `the page holds only ${MM(lowest - area.top)} mm of content`, { content_mm: MM(lowest - area.top) }, body);
    }
    // 7. A heading at the foot of the text, or a section that starts with less than two lines of itself.
    const LINE = parseFloat(style(document.body).lineHeight) || 26;
    const bottom = footTop - opts.bodyGap * PX;
    const headings = rows.filter((r) => r.classList.contains('row-heading'));
    for (const head of headings) {
      const h = head.getBoundingClientRect();
      if (bottom - h.bottom < opts.headingFoot * PX) {
        add('heading-at-foot', 'error', head.textContent, `a heading ${MM(bottom - h.bottom)} mm above the foot of the text`,
            { room_mm: MM(bottom - h.bottom) }, head);
      }
    }
    const lastHead = headings[headings.length - 1];
    if (lastHead && rows.indexOf(lastHead) > 0) {
      let k = rows.indexOf(lastHead);
      while (k > 0 && rows[k - 1].classList.contains('row-heading')) k--;
      const after = rows.slice(rows.indexOf(lastHead) + 1);
      const under = after.length ? Math.max(...after.map((r) => r.getBoundingClientRect().bottom)) -
        lastHead.getBoundingClientRect().bottom : 0;
      if (k > 0 && under < opts.sectionLines * LINE - 1) {
        add('section-start', 'error', lastHead.textContent,
            `a section starts at the foot of the page with ${MM(under)} mm of itself (fewer than ${opts.sectionLines} lines)`,
            { under_mm: MM(under) }, lastHead);
      }
    }
    // 4. Text outside the text area: wider than the text block, or down into the footer.
    const texts = textRects(body, null);
    for (const { el, rect } of texts) {
      if (rect.left < area.left - opts.slack * PX || rect.right > area.right + opts.slack * PX) {
        add('off-text-area', 'error', el.textContent, `text runs ${MM(Math.max(area.left - rect.left, rect.right - area.right))} mm ` +
            'out of the text block', {}, rect);
        break;
      }
    }
    // 13. A note touching another note, or a block or a line of text beside it.
    const notes = [...body.querySelectorAll('.row > .side > *')].filter((n) => n.getBoundingClientRect().height > 0);
    for (let i = 0; i < notes.length; i++) {
      const a = notes[i].getBoundingClientRect();
      for (const other of notes.slice(i + 1)) {
        const b = other.getBoundingClientRect();
        const across = a.left < b.right && b.left < a.right;
        const air = Math.max(b.top - a.bottom, a.top - b.bottom);
        if (across && air < opts.noteAir * PX) {
          add('note-overlap', 'error', other.textContent, `two notes in one margin ${air < 0 ? 'overlap' : 'touch'}: ` +
              `${MM(air)} mm apart`, { air_mm: MM(air) }, union(a, b));
        }
      }
      if (notes[i].classList.contains('accent')) continue;      // text wraps round an accent's outline, not its box
      const own = notes[i].closest('.row');
      const hit = texts.find((t) => !notes[i].contains(t.el) && !t.el.closest('.side') && overlaps(a, t.rect, 1)) ||
        [...body.querySelectorAll(BOXES)].map((x) => ({ el: x, rect: x.getBoundingClientRect() }))
          .find((t) => !notes[i].contains(t.el) && !t.el.contains(notes[i]) && !t.el.closest('.side') &&
                       overlaps(a, t.rect, 1) && t.el.closest('.row') !== own);
      if (hit) {
        add('note-overlap', 'error', notes[i].textContent, `a note overlaps "${snippet(hit.el.textContent, 40)}"`, {}, union(a, hit.rect));
      }
    }
    // 9. Tables: wider than their column, a cell whose content does not fit.
    for (const table of body.querySelectorAll('table')) {
      const holder = table.parentElement.getBoundingClientRect();
      const t = table.getBoundingClientRect();
      if (t.width > holder.width + 1 || t.right > area.right + 1) {
        add('table', 'error', table.textContent, `a table ${MM(t.width - holder.width)} mm wider than its column`, {}, table);
      }
      for (const cell of table.querySelectorAll('td, th')) {
        if (cell.scrollWidth > cell.clientWidth + 1) {
          add('table', 'error', cell.textContent, `a table cell's content does not fit it (${MM(cell.scrollWidth - cell.clientWidth)} mm)`,
              {}, cell);
        }
      }
    }
    // 10. A monitor: its screen 4:3, the whole monitor no wider than the text.
    for (const prompt of body.querySelectorAll('.prompt')) {
      const screen = prompt.querySelector('.screen');
      if (!screen) continue;
      const s = screen.getBoundingClientRect();
      const ratio = s.width / s.height;
      if (Math.abs(ratio / (4 / 3) - 1) > opts.monitorRatio) {
        add('monitor', 'error', screen.textContent, `a monitor's screen is ${ratio.toFixed(3)}:1, not 4:3`, { ratio: +ratio.toFixed(3) }, screen);
      }
      const p = prompt.getBoundingClientRect();
      if (p.width > area.width + 1) {
        add('monitor', 'error', screen.textContent, `a monitor ${MM(p.width - area.width)} mm wider than the text`, {}, prompt);
      }
    }
    // 11. The running head, clipped or cut with an ellipsis.
    for (const head of page.querySelectorAll('.rh-text')) {
      if (head.scrollWidth > head.clientWidth + 1) {
        add('running-head', 'error', head.textContent, 'the running head is too long and is cut with an ellipsis', {}, head);
      }
    }
  }

  // ------------------------------------------------------------------ text left over from the markup
  const NOT_TEXT = 'svg, code, pre, kbd, .screen, .terminal, .code, .tree, .sheet, script, style';
  const MARKUP = [['**', /\*\*/], ['==', /==/], [':::', /:::/], ['[[', /\[\[/], ['TODO', /\bTODO\b/], ['FIXME', /\bFIXME\b/],
                  ['<!--', /<!--/], ['-->', /-->/]];
  const TEXT_BLOCKS = 'p, li, td, th, h1, h2, h3, h4, figcaption, blockquote';
  const BOXY = 'div, aside, section, figure, header, footer';     // what holds text that is not in a paragraph
  function auditResidue(page) {
    // The text of each block, code left out, read as one string: a split paragraph's added hyphen is a node of its own.
    const texts = new Map();
    const walker = document.createTreeWalker(page, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.data.trim()) continue;
      const block = node.parentElement.closest(TEXT_BLOCKS) || node.parentElement.closest(BOXY) || node.parentElement;
      const so = texts.get(block) || '';
      if (node.parentElement.closest(NOT_TEXT)) {       // code stands in as one sign: the spaces round it stay single
        if (!so.endsWith('\u00a7')) texts.set(block, so + '\u00a7');
      } else texts.set(block, so + node.data);
    }
    for (const [box, text] of texts) {
      const around = snippet(box.textContent, 60);
      for (const [mark, pattern] of MARKUP) {
        if (pattern.test(text)) add('residue', 'error', around, `markup left in the text: "${mark}"`, {}, box);
      }
      const russian = /[\u0430-\u044f\u0451]/i.test(text);
      if (/\S {2,}\S/.test(text)) add('residue', 'warning', around, 'two spaces in a row', {}, box);
      if (russian && text.includes('"')) add('residue', 'warning', around, 'a straight quote " in Russian text; use «»', {}, box);
      if (russian && /(^|\s)-(\s|$)/.test(text)) add('residue', 'warning', around, 'a hyphen used as a dash: " - "', {}, box);
      if (/(^|[^-])--([^-]|$)/.test(text)) add('residue', 'warning', around, 'a double hyphen "--" in running text', {}, box);
    }
  }

  // ------------------------------------------------------------------ the whole document
  function auditDocument() {
    current = null;
    // 12. Pictures that did not load.
    for (const img of document.images) {
      if (!img.naturalWidth) {
        current = img.closest('.page');
        add('image', 'error', img.getAttribute('src'), `a picture did not load: ${img.getAttribute('src')}`, {}, img);
      }
    }
    // 12. Ids: one element each, and every reference finds its target.
    const owners = new Map();
    for (const el of document.querySelectorAll('[id]')) {
      const top = el.closest('svg') ? (el.closest('svg:not(svg svg)') || el.ownerSVGElement) : el;
      if (!owners.has(el.id)) owners.set(el.id, top);
      else if (owners.get(el.id) !== top) {
        current = el.closest('.page');
        add('svg-id', 'error', el.id, `the id "${el.id}" is used twice`, {}, null);
      }
    }
    const refs = '[clip-path], [mask], [filter], [fill^="url("], [stroke^="url("], use';
    const missing = new Set();
    for (const el of document.querySelectorAll(refs)) {
      const links = [el.getAttribute('href'), el.getAttribute('xlink:href')];
      for (const value of [el.getAttribute('clip-path'), el.getAttribute('mask'), el.getAttribute('filter'),
                           el.getAttribute('fill'), el.getAttribute('stroke'), ...links]) {
        const m = value && (links.includes(value) ? /^#(.+)$/ : /^url\(#([^)]+)\)$/).exec(value.trim());
        const id = m && m[1];
        if (id && !document.getElementById(id) && !missing.has(id)) {
          missing.add(id);
          current = el.closest('.page');
          add('svg-id', 'error', id, `a drawing refers to the id "${id}", which is nowhere`, {}, null);
        }
      }
    }
    // 22. Links: external ones well-formed, internal ones found; the contents' page numbers right.
    for (const a of document.querySelectorAll('#book a[href]')) {
      const href = a.getAttribute('href');
      current = a.closest('.page');
      if (href.startsWith('#')) {
        if (!document.getElementById(decodeURIComponent(href.slice(1)))) {
          add('links', 'error', a.textContent, `an internal link to "${href}" leads nowhere`, {}, a);
        }
      } else if (/^mailto:/.test(href)) {
        if (!/^mailto:[^@\s]+@[^@\s]+\.[^@\s]+$/.test(href)) add('links', 'error', href, `a malformed address: ${href}`, {}, a);
      } else {
        let ok = /^https?:\/\/[^\s]+$/.test(href);
        try { ok = ok && new URL(href).hostname.includes('.'); } catch (error) { ok = false; }
        if (!ok) add('links', 'error', href, `a link that is not a well-formed http(s) address: ${href}`, {}, a);
      }
    }
    for (const cell of document.querySelectorAll('[data-ref]')) {
      const target = document.getElementById(cell.dataset.ref);
      const holder = target && target.closest('.page');
      current = cell.closest('.page');
      if (holder && cell.textContent.trim() !== holder.dataset.page) {
        add('links', 'error', cell.closest('a') ? cell.closest('a').textContent : cell.dataset.ref,
            `the contents give page ${cell.textContent.trim()}, the heading is on page ${holder.dataset.page}`, {}, cell);
      }
    }
    // 16. Which side the book ends on.
    const last = pages[pages.length - 1];
    if (last) {
      current = last;
      add('last-page', 'info', '', `the book ends on page ${last.dataset.page}, a ${last.classList.contains('recto') ? 'right' : 'left'} ` +
          'page', { pages: pages.length }, null);
    }
    current = null;
  }

  const timing = {};
  const time = (name, fn) => { const t = performance.now(); fn(); timing[name] = (timing[name] || 0) + performance.now() - t; };
  for (const page of pages) {
    current = page;
    time('page', () => auditPage(page));
    time('text', () => { if (!page.classList.contains('full')) auditText(page); });
    time('residue', () => auditResidue(page));
    // 19. The weight of a page's markup: a heavy one runs the browser out of memory.
    time('weight', () => {
      const kb = page.outerHTML.length / 1024;
      if (kb > opts.pageWeight) {
        add('page-weight', 'warning', '', `the page weighs ${Math.round(kb)} KB of markup (drawings, mostly)`,
            { kb: Math.round(kb) }, null);
      }
    });
  }
  time('document', auditDocument);
  return { findings, timing };
}
