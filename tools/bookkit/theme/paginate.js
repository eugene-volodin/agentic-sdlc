/* Paginator: distributes the flat stream of rows in #source over pages.
 *
 * What it guarantees
 *   - a row that does not fit moves to the next page; only listings and lists taller than a page are split
 *     between their units (the children of a [data-split] element);
 *   - a heading never stays last on a page: it travels with the block it introduces;
 *   - every row has its own width: a row with nothing beside it spans the full width, a row
 *     with a margin note shares the line with it, and the notes on a page alternate between the
 *     outer and the inner edge (each page composed freely, no empty space left);
 *   - the text wraps round what stands in the margin and runs on at full width below it;
 *   - no text runs into a picture: the build checks every line against every drawing;
 *   - a page is for content: a paragraph that does not fit is split between its lines, so the next page's
 *     text fills this one; the footer scene is small (s or m) and grows to l only when the next block cannot
 *     move up, and up to the last line when that block is a prompt (size 'fill', chosen only once the page's
 *     content is final); only the last page of a chapter gets a big panorama; nothing is put on a page just to
 *     fill it.
 *
 * Every measurement comes from the design tokens (custom properties written by bookkit/design.py).
 * The page talks to Python through four globals: __bookConfig (in), __bookScenes and __bookReport
 * (out), __setScenes (called back with the footer drawings); __bookReady flips when done.
 */
(async function () {
  // ---------------------------------------------------------------- setup
  // Layout depends on real glyph metrics and image sizes, so wait for both. Every declared face is loaded before
  // anything is measured: a face first met during layout would arrive after the measurement and move the text.
  const config = window.__bookConfig;
  const warnings = [];
  /* Every warning is also kept structured, for `book audit` (audit.py): what was checked, on which page, a short
   * snippet that says where, and the box on the page to mark on its contact sheet. */
  const findings = [];
  // The soft hyphens of running text (hyphenate.py) are break points, not text: whatever is reported or compared
  // goes without them.
  const SHY = /\u00ad/g;
  const plain = (text) => String(text || '').replace(SHY, '');
  function warn(check, record, where, text, box = null) {
    text = plain(text);
    warnings.push(text);
    const el = record && record.el;
    let rect = null;
    if (el && box) {
      const sheet = el.getBoundingClientRect();
      const r = box.getBoundingClientRect ? box.getBoundingClientRect() : box;
      rect = { x: r.left - sheet.left, y: r.top - sheet.top, w: r.width, h: r.height };
    }
    findings.push({ check, severity: 'error', page: record ? record.number : 0,
                    chapter: record ? String(record.chapter || '') : '',
                    where: plain(where).replace(/\s+/g, ' ').trim().slice(0, 60), detail: text, rect });
  }
  await Promise.all([...document.fonts].map((face) => face.load().catch(() => null)));
  await document.fonts.ready;
  for (const face of document.fonts) {
    if (face.status === 'error') warn('font', null, face.family, `font: ${face.family} ${face.weight} ${face.style} did not load`);
  }
  for (const family of config.fonts) {
    if (![...document.fonts].some((face) => face.family.replace(/"/g, '') === family && face.status === 'loaded')) {
      warn('font', null, family, `font: no face of "${family}" loaded; the text falls back to another font`);
    }
  }
  await Promise.all([...document.images].map((img) => img.decode().catch(() => null)));

  const probe = document.createElement('div');
  probe.style.cssText = 'position:absolute;width:100mm;height:0';
  document.body.append(probe);
  const PX_PER_MM = probe.getBoundingClientRect().width / 100;
  probe.remove();
  const root = getComputedStyle(document.documentElement);
  const mm = (name) => parseFloat(root.getPropertyValue(name));        // a token, in millimetres
  const px = (name) => mm(name) * PX_PER_MM;                           // the same token, in pixels

  const FOOT = { s: mm('--foot-s'), m: mm('--foot-m'), l: mm('--foot-l') };
  const FOOT_MAX = mm('--foot-max');
  const FOOT_LARGE_MAX = parseFloat(root.getPropertyValue('--foot-large-max'));
  const FOOT_PANORAMA = mm('--foot-panorama');
  const HOLE_MAX = mm('--hole-max');
  const SECTION_MIN = px('--section-min');
  const HANG_MAX = px('--hang-max');
  const MAX_BODY = (mm('--page-h') - mm('--body-top') - FOOT.s - mm('--body-gap')) * PX_PER_MM;
  const SPREAD_MAX = px('--spread-max');
  const SPREAD_FROM = px('--spread-from');
  const EDGE_MIN = px('--edge-min');                     // text keeps at least this far from the edge of the sheet

  const book = document.getElementById('book');
  const source = document.getElementById('source');
  const stock = document.getElementById('stock');
  const accents = [...stock.querySelectorAll('[data-accent]')];
  const ACCENT_EVERY = px('--accent-every');             // this much full-width text in a row earns an accent
  const ACCENT_FROM = px('--accent-from');               // a paragraph at least this tall can take one
  const pages = [];
  let page = null;      // record of the page being filled
  let body = null;      // its text block element
  let chapter = null;   // running header data for the current section
  let accentIndex = 0;
  const stream = [];    // everything to lay out, in order; `cursor` is the next item
  let cursor = 0;

  // ---------------------------------------------------------------- small helpers
  const rowsOf = (holder) => [...holder.children].filter((el) => el.classList.contains('row'));
  const sideOf = (row) => row.querySelector(':scope > .side');
  const isHeading = (el) => !!el && el.classList.contains('row-heading');
  const isFirstOnPage = (row) => {
    for (let p = row.previousElementSibling; p; p = p.previousElementSibling) if (!isHeading(p)) return false;
    return true;
  };

  /* Copy an ornament from the stock. Its drawings reference their own clip paths and gradients by id,
   * so every copy gets fresh ids: duplicates in one document would resolve to whichever comes first. */
  let copies = 0;
  function stockCopy(item) {
    const suffix = `-c${++copies}`;
    return item.innerHTML.replace(/\bid="([^"]+)"/g, `id="$1${suffix}"`).replace(/url\(#([^)]+)\)/g, `url(#$1${suffix})`);
  }

  // ---------------------------------------------------------------- pages
  function makePage(full) {
    const number = pages.length + 1;
    const el = document.createElement('div');
    el.className = 'page ' + (number % 2 ? 'recto' : 'verso') + (full ? ' full' : '');
    el.dataset.page = number;
    if (chapter) el.dataset.color = chapter.color;
    el.dataset.chapter = chapter ? chapter.number || chapter.title : '';   // for `book audit`
    book.append(el);
    const record = { number, el, foot: null, accents: 0, chapter: chapter ? chapter.number || chapter.title : '',
                     world: chapter ? chapter.world : '' };
    pages.push(record);
    return record;
  }

  // The centred and the full layouts have one column and no margin.
  const singleColumn = (el) => el.classList.contains('side-center') || el.classList.contains('side-full');

  function resolveSide(setting, number) {
    if (setting === 'center' || setting === 'full') return setting;
    if (setting === 'outer') return number % 2 ? 'right' : 'left';
    if (setting === 'inner') return number % 2 ? 'left' : 'right';
    return setting === 'left' ? 'left' : 'right';
  }

  function applySide() {
    page.el.classList.remove('side-left', 'side-right', 'side-center', 'side-full');
    page.el.classList.add('side-' + resolveSide(chapter.side, page.number));
  }

  function startPage() {
    page = makePage(false);
    applySide();
    const head = document.createElement('header');
    head.className = 'p-head';
    const running = document.createElement('span');     // the chapter only: the book's title on every page is noise
    running.className = 'rh';
    if (chapter.number) {
      const badge = document.createElement('b');
      badge.textContent = chapter.number;
      running.append(badge);
    }
    const text = document.createElement('span');
    text.className = 'rh-text';                          // truncated with an ellipsis if too long
    text.textContent = chapter.title;
    running.append(text);
    head.append(running);
    const perch = stock.querySelector(`[data-perch="${page.number % 4}"]`);
    if (perch) {
      const holder = document.createElement('span');
      holder.className = 'perch';
      holder.innerHTML = stockCopy(perch);
      head.append(holder);
      holder.style.bottom = perch.dataset.drop + 'mm';      // feet on the dashed line (pages.py)
    }
    body = document.createElement('div');
    body.className = 'p-body';
    page.el.append(head, body);
  }

  /* What ends the page being finished, i.e. what comes next in the stream: 'last' when nothing can follow on this
   * page (the end of a chapter or of a front page, a full page next, a page break in the front matter), 'break'
   * for a page break or a change of layout the chapter asks for, 'stuck' when the next block cannot move up (a
   * block that is never split), 'text' otherwise - the text that comes next could have filled the page. */
  let blocker = '';     // what the next block is when it cannot move up, for the report
  function pageEnd() {
    blocker = '';
    for (let i = cursor; i < stream.length; i++) {
      const { kind, el } = stream[i];
      if (kind === 'end' || kind === 'cover' || kind === 'fullpage' || kind === 'chapter') return 'last';
      if (kind === 'pagebreak' || kind === 'set-side') {
        blocker = kind;
        return chapter && chapter.number ? 'break' : 'last';
      }
      // Headings, a prompt's hint and a short lead-in that left with its list travel with the block after them.
      if (isHeading(el) || el.classList.contains('keep-next') || el.classList.contains('leads-on')) continue;
      if (isText(el) || el.classList.contains('split-tail') || el.classList.contains('prompt-cont')) {
        return 'text';                                   // or the rest of a split block
      }
      const block = el.querySelector(':scope > .main > *');
      blocker = block ? (block.className || block.tagName).toString().split(' ')[0].toLowerCase() : 'block';
      return 'stuck';
    }
    return 'last';
  }

  const ROOM = FOOT.m - FOOT.s + 2;                       // the free space a footer of size m takes

  function finishPage() {
    if (!page) return;
    widenHangingNotes();
    // 1. The footer scene: a page is for content (an illustration never takes a half or
    // a third of a page). Normally s or m; l only when the next block cannot move up; the last page of a chapter,
    // which nothing can fill, gets one big panorama instead of a hole.
    const free = (MAX_BODY - settle()) / PX_PER_MM;
    const end = pageEnd();
    // A large footer only before a block that cannot move up, and at most FOOT_LARGE_MAX times a chapter: past that,
    // the page keeps a hole for the text to be moved, which the audit reports.
    const spent = end === 'stuck' && chapter && chapter.large >= FOOT_LARGE_MAX;
    const sizes = end === 'text' || spent ? ['m'] : ['m', 'l'];
    let size = 's';
    for (const key of sizes) if (FOOT[key] - FOOT.s <= free - 2) size = key;
    let height = FOOT[size];
    const fill = end === 'stuck' && blocker === 'prompt';
    if (size === 'l' && end === 'stuck' && !fill && chapter) chapter.large++;
    if (end === 'last' && FOOT.s + free - 2 >= FOOT_PANORAMA) {
      size = 'panorama';
      height = Math.min(FOOT_MAX, FOOT.s + free - 2);
    } else if (fill) {
      // A prompt is never split while it fits a page, so its monitor moved on whole and left this page short. The
      // text is not trimmed to fit: the footer grows up to the last line instead and draws more of its scene above
      // (size 'fill'). Decided here only, after the page's content is final, so no layout choice can aim at it; it
      // is the one exception to the size l and to FOOT_LARGE_MAX, and does not count towards that limit.
      size = 'fill';
      height = Math.max(height, Math.min(FOOT_MAX, FOOT.s + free - 2));
    }
    const limit = MAX_BODY - (height - FOOT.s) * PX_PER_MM;          // where that scene begins
    // 2. Whatever is still left: lay the content out more loosely.
    spread(limit - settle());

    const foot = document.createElement('footer');
    foot.className = 'p-foot';
    foot.style.height = height + 'mm';
    const recto = page.number % 2 === 1;
    const tag = document.createElement('div');
    tag.className = 'p-num';
    const outline = recto ? 'M86,3 H22 L3,22 L22,41 H86' : 'M-2,3 H62 L81,22 L62,41 H-2';
    tag.innerHTML = `<svg viewBox="0 0 84 44"><path d="${outline}"/>` +
      `<text x="${recto ? 52 : 32}" y="28" text-anchor="middle">${page.number}</text></svg>`;   // colors: .p-num in CSS
    page.el.append(foot, tag);
    page.foot = { height, size, end, blocker, free: Math.round(free), el: foot, clear: recto ? 'right' : 'left' };
    page = null;
    body = null;
  }

  // ---------------------------------------------------------------- fitting
  /* Lays out the rows of the page being filled, top to bottom, and returns the height they take.
   * What a row has for the margin floats at one page edge and the text wraps round it: beside a short
   * note the paragraph is narrow, below it the paragraph runs on at full width. The notes of a page
   * alternate between the outer and the inner edge; while one still hangs down beside the next rows,
   * the next note takes the same edge, so the text is never squeezed between two. Rows with nothing in
   * the margin span the full width; a block that must be wide clears the notes (page.css). */
  const other = (where) => (where === 'left' ? 'right' : 'left');
  function settle() {
    const rows = rowsOf(body);
    for (const row of rows) {
      row.classList.remove('bare', 'note-left', 'note-right');
      const side = sideOf(row);
      if (side) side.style.paddingBottom = '';
    }
    if (singleColumn(page.el)) return body.offsetHeight;                       // notes are in the flow there
    const home = page.el.classList.contains('side-left') ? 'left' : 'right';  // where the first note goes
    let hangs = 0;                                       // the lowest note so far ends at this y
    let hangSide = home;                                 // on this edge
    let hangEl = null;                                   // and belongs to this margin
    let notes = 0;
    for (const row of rows) {
      const side = sideOf(row);
      if (row.classList.contains('wide') || !side || !side.children.length) {
        row.classList.add('bare');
        // A paragraph of its own that starts beside a note still hanging from above keeps its last line beside
        // that note too: the tail rule is about the text, not about whose note it is.
        if (hangEl && !row.classList.contains('wide') && row.offsetTop < hangs) {
          keepTail(row, hangEl);
          hangs = Math.max(hangs, hangEl.offsetTop + hangEl.offsetHeight);
        }
        continue;
      }
      const where = row.offsetTop < hangs ? hangSide : (notes % 2 ? other(home) : home);
      notes++;
      row.classList.add('note-' + where);
      keepTail(row, side);
      const bottom = side.offsetTop + side.offsetHeight;
      if (bottom > hangs) { hangs = bottom; hangSide = where; hangEl = side; }
    }
    return body.offsetHeight;
  }

  /* A paragraph whose last line or two would run out from under its note to full width - a few words alone on
   * a wide line - keeps them beside the note instead. The note's
   * bottom margin counts: the text only runs on to full width below it. */
  function keepTail(row, side) {
    const text = row.querySelector(':scope > .main > p:last-child');
    if (!text) return;
    const gap = parseFloat(getComputedStyle(side).marginBottom) || 0;
    // One line at most: two or more lines are a proper run of text and flow on at full width.
    // Narrowing that line can push a word onto a new last line, so measure again until it settles.
    for (let round = 0; round < 3; round++) {
      const wide = wideLines(text, side);
      if (wide.count !== 1 || !wide.last) return;
      const box = side.getBoundingClientRect();
      const now = parseFloat(side.style.paddingBottom) || 0;
      side.style.paddingBottom = Math.ceil(now + wide.bottom - box.bottom - gap + 2) + 'px';
    }
  }

  /* The lines of a paragraph that reach into a note's column, i.e. run on at full width under it. */
  function wideLines(text, side) {
    const column = side.getBoundingClientRect();
    const range = document.createRange();
    range.selectNodeContents(text);
    const lines = new Map();
    for (const r of range.getClientRects()) {
      const key = Math.round(r.top);
      const into = r.left < column.right - 2 && column.left + 2 < r.right;
      const was = lines.get(key) || { into: false, bottom: 0 };
      lines.set(key, { into: was.into || into, bottom: Math.max(was.bottom, r.bottom) });
    }
    const ordered = [...lines.entries()].sort((x, y) => x[0] - y[0]).map(([, v]) => v);
    const count = ordered.filter((l) => l.into).length;
    const last = ordered.length > 1 && ordered[ordered.length - 1].into && !ordered[0].into;
    return { count, last, bottom: ordered.length ? ordered[ordered.length - 1].bottom : 0 };
  }

  const fits = () => settle() <= MAX_BODY + 0.5;

  /* Split a row between its units. Returns the remainder row, or null if nothing was split. */
  function split(row) {
    const box = row.querySelector('[data-split]');
    if (!box) return null;
    const units = [...box.children];
    const count = units.length;
    if (count < 2) return null;
    // A block that fits on a page of its own is never torn between pages: it moves on whole.
    // Only a block taller than a page is split - and a list or a list of steps, which may break between
    // its items wherever it falls, at least two on each side, so it does not leave a hole.
    // A sheet, code, terminal or table that fits a page splits too when moving on whole would leave more than a
    // third of this page empty (HOLE_MAX): lines at least four a side, table rows two.
    const list = isList(row, box);
    const frame = framed(row, box);
    const tall = row.getBoundingClientRect().height > MAX_BODY;
    // The hole is what the page loses to the move: the empty space and the footer that would stand in it.
    const hole = !list && !tall && !!frame && !isFirstOnPage(row) && freeWithout(row) + FOOT.s > HOLE_MAX;
    if (!list && !hole && !isFirstOnPage(row) && !tall) return null;
    // A list whose items are each three lines or more is read item by item: one may stay and one go on.
    const long = list && units.every((u) => u.getBoundingClientRect().height >= 3 * LINE - 1);
    const min = box.tagName === 'PRE' ? 4 : box.tagName === 'TBODY' || (list && !long) ? 2 : 1;   // lines in fours, rows in twos
    // The first part of a sheet, code, terminal or table ends with a small mark: it goes on overleaf. It is there while
    // measuring, so the part that stays fits with it.
    const mark = frame ? document.createElement('div') : null;
    if (mark) {
      mark.className = 'cont-mark';
      mark.textContent = config.continued || '';
      (frame === 'table' ? box.parentElement : box).after(mark);   // a table's goes under it
    }
    const show = (k) => units.forEach((u, i) => { u.style.display = i < k ? '' : 'none'; });
    let lo = 0;
    let hi = count - 1;                                  // largest k such that the first k units fit
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      show(mid);
      if (fits()) lo = mid; else hi = mid - 1;
    }
    let keep = lo;
    if (count - keep < min && keep > min) keep = count - min;   // do not strand an orphan on the next page
    if ((list || hole) && keep >= min) {                 // as many go on; a section shows enough of itself
      keep = Math.min(keep, count - min);
      show(keep);
      if (!sectionFits() || !fits()) keep = 0;
    }
    if (keep < min) {
      if (!isFirstOnPage(row)) { show(count); if (mark) mark.remove(); settle(); return null; }
      keep = Math.max(1, keep);                          // nothing else on the page: force progress
    }
    show(count);
    const rest = row.cloneNode(true);
    rest.querySelectorAll('.cont-mark').forEach((el) => el.remove());
    const restBox = rest.querySelector('[data-split]');
    [...restBox.children].slice(0, keep).forEach((u) => u.remove());
    units.slice(keep).forEach((u) => u.remove());
    if (box.tagName === 'OL') {
      const start = parseInt(box.getAttribute('start') || '1', 10) + keep;
      restBox.setAttribute('start', start);
      restBox.style.setProperty('--start', start);
    }
    rest.querySelectorAll(':scope > .main > h4').forEach((el) => el.remove());   // a block's title stays with its start
    row.classList.add('split-head');
    rest.classList.remove('split-head');
    rest.classList.add('split-tail');
    rest.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));   // ids stay with the head
    const side = sideOf(rest);
    if (side) side.innerHTML = '';                       // and so do the margin notes
    return rest;
  }

  /* A section that begins on this page shows at least SECTION_MIN of itself under its heading: never a heading and a
   * line or two at the foot of a page. A heading at the top of the page has the whole page. */
  function sectionFits() {
    const rows = rowsOf(body);
    let last = rows.length - 1;
    while (last >= 0 && !isHeading(rows[last])) last--;
    if (last <= 0) return true;
    let head = last;                                     // a run of headings counts as one
    while (head > 0 && isHeading(rows[head - 1])) head--;
    if (head === 0) return true;
    return body.offsetHeight - (rows[last].offsetTop + rows[last].offsetHeight) >= SECTION_MIN;
  }

  /* A paragraph of running text: a row whose block is a single <p>, nothing wide, no heading. */
  const isText = (row) => !!row && !row.classList.contains('wide') && !isHeading(row) &&
    row.querySelector(':scope > .main > p:only-child') !== null;

  /* The lines of a paragraph. Glyphs of one line may stand a little higher or lower (inline code, a smaller face),
   * so tops closer than half a line belong to one line. Returns a function from a rect's top to its line's index. */
  const LINE = parseFloat(getComputedStyle(document.body).lineHeight) || px('--gap') * 4;
  function lineIndex(tops, line = LINE) {
    const starts = [];
    for (const top of [...tops].sort((a, b) => a - b)) {
      if (!starts.length || top - starts[starts.length - 1] > line / 2) starts.push(top);
    }
    const of = (top) => { let i = 0; while (i + 1 < starts.length && top - starts[i + 1] > -line / 2) i++; return i; };
    return { count: starts.length, of };
  }
  function lineCount(p) {
    const range = document.createRange();
    range.selectNodeContents(p);
    return lineIndex([...range.getClientRects()].filter((r) => r.width > 0).map((r) => r.top)).count;
  }

  /* The last line of a paragraph, set ragged, is nearly as long as the line above it: justified, it would not open
   * wide gaps. */
  function fullLastLine(p) {
    const cut = p.classList.contains('cut');
    p.classList.remove('cut');
    const range = document.createRange();
    range.selectNodeContents(p);
    const rects = [...range.getClientRects()].filter((r) => r.width > 0);
    if (cut) p.classList.add('cut');
    const lines = lineIndex(rects.map((r) => r.top));
    const width = (n) => {
      const line = rects.filter((r) => lines.of(r.top) === n);
      return Math.max(...line.map((r) => r.right)) - Math.min(...line.map((r) => r.left));
    };
    return lines.count < 2 || width(lines.count - 1) >= width(lines.count - 2) * 0.85;
  }

  /* Where a paragraph may be cut: after a space, so a word is never cut in two. Each cut is a character offset in the
   * paragraph's text and the line its next word starts on. */
  function textCuts(p) {
    const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    const found = [];
    let at = 0;
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const text = node.textContent;
      for (let i = 1; i < text.length; i++) {
        if (!/\s/.test(text[i - 1]) || /\s/.test(text[i])) continue;
        range.setStart(node, i);
        range.setEnd(node, i + 1);
        const rect = range.getClientRects()[0];
        if (rect) found.push({ at: at + i, top: rect.top });
      }
      at += text.length;
    }
    const all = document.createRange();
    all.selectNodeContents(p);
    const lines = lineIndex([...all.getClientRects()].filter((r) => r.width > 0).map((r) => r.top));
    return { lines: lines.count, of: lines.of, cuts: found.map((c) => ({ at: c.at, line: lines.of(c.top) })) };
  }

  /* Where the character offset `at` of an element's text lies: a text node and an offset in it. */
  function pointAt(el, at) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (at <= node.textContent.length) return [node, at];
      at -= node.textContent.length;
    }
    return null;
  }

  /* Split a paragraph between its lines (the text is pulled up from the next pages): the page
   * is filled with the next page's text, not with a picture standing in for a paragraph that moved on whole. At
   * least two lines stay and at least two go on, at full width on the next page. The margin notes stay with the
   * first part; if they do not fit there, the remarks go on with the second and a question stays on this page -
   * beside the first part or across the page above it - so it is still read before its answer. The section rule
   * holds. Returns the remainder row, or null if the paragraph moves on whole. */
  const MIN_LINES = 2;
  function splitText(row) {
    if (!isText(row)) return null;
    const p = row.querySelector(':scope > .main > p');
    const side = sideOf(row);
    const original = p.cloneNode(true);
    const restore = () => { p.replaceChildren(...original.cloneNode(true).childNodes); p.classList.remove('cut'); };
    const notes = side ? [...side.children] : [];
    const goers = notes.filter((n) => !n.textContent.trim().endsWith('?'));   // a question never leaves its place
    // No note may hang far below the first part, the last row of the page: it would go across the page when the
    // page is finished (`widenHangingNotes`), between the two parts of the paragraph, and the text would set anew.
    const hangs = () => !singleColumn(page.el) && body.offsetHeight - (row.offsetTop + row.offsetHeight) >= HANG_MAX;

    /* Cut the paragraph so that k lines stay, where the browser broke line k: inside a word it hyphenated there -
     * the first part then ends with that hyphen, as it was set - or before the first word of the next line, or else
     * before the hyphenated word. The first part's last line must stay full: it is justified, and a short one would
     * open wide gaps. Returns the cut-off tail, or null (nothing changed). */
    function cut(k, measured) {
      const { cuts, of } = measured;
      const next = cuts.find((c) => c.line === k);
      const last = cuts.filter((c) => c.line === k - 1).pop();
      if (!next || !last) return null;
      const range = document.createRange();
      const tries = [];
      for (let i = last.at + 1; i < next.at; i++) {     // a character of the last word already on the next line
        const point = pointAt(p, i);
        if (!point || /\s/.test(point[0].textContent[point[1]] || ' ')) break;
        range.setStart(...point);
        range.setEnd(point[0], point[1] + 1);
        // The letter's own box is its last: the letter after a soft hyphen that broke the line also gets the box of
        // that hyphen, at the end of the line above.
        const rect = [...range.getClientRects()].filter((r) => r.width > 0).pop();
        if (rect && of(rect.top) >= k) { tries.push({ at: i, hyphen: true }); break; }
      }
      // Without the hyphen: before the next line's first word, or before the hyphenated word.
      tries.push({ at: next.at, hyphen: false }, { at: last.at, hyphen: false });
      for (const { at, hyphen } of tries) {
        const point = pointAt(p, at);
        if (!point) continue;
        // Never inside a bit of code: `claude auto-mode config` torn between two pages reads as two commands.
        const code = point[0].parentElement && point[0].parentElement.closest('code');
        if (code && !(point[1] === 0 && code.firstChild === point[0])) continue;
        range.setStart(...point);
        range.setEnd(p, p.childNodes.length);
        const tail = range.extractContents();
        // A word broken at its own hyphen (state-manager) keeps that one; only a syllable break gets one added, in
        // place of the soft hyphen it broke at.
        if (hyphen && !/[-‐‑]$/.test(p.textContent)) {
          const end = pointAt(p, p.textContent.length);
          if (end && end[1] > 0 && end[0].data[end[1] - 1] === '\u00ad') end[0].deleteData(end[1] - 1, 1);
          p.append('-');
        }
        p.classList.add('cut');                          // its last line is justified: the sentence runs on
        if (lineCount(p) === k && fullLastLine(p) && fits() && sectionFits() && !hangs() && tailLines(tail) >= MIN_LINES) {
          return tail;
        }
        restore();
      }
      return null;
    }
    // The second part runs at full width on its page: it must keep at least two lines there too.
    function tailLines(tail) {
      const probe = document.createElement('div');
      probe.className = 'row wide';
      const main = document.createElement('div');
      main.className = 'main';
      const q = p.cloneNode(false);
      q.classList.remove('cut');
      q.append(tail.cloneNode(true));
      main.append(q);
      probe.append(main);
      body.append(probe);
      const count = lineCount(q);
      probe.remove();
      return count;
    }
    /* Where the notes go while the paragraph is split: 'all' stay beside the first part; 'questions' - only the
     * questions stay, the remarks go on with the second part; 'above' - the questions go across the page above the
     * paragraph, as `widenHangingNotes` would put them, and the remarks go on. `arrange` sets that up, `undo` puts
     * every note back in its margin. */
    const questions = notes.filter((n) => !goers.includes(n));
    let above = [];
    function arrange(mode) {
      if (mode !== 'all') goers.forEach((n) => n.remove());
      if (mode === 'above') above = questions.map((n) => { const wide = wideNote([n], side); aboveOf(row).before(wide); return wide; });
      settle();
    }
    function undo() {
      above.forEach((wide) => wide.remove());
      above = [];
      if (side) side.replaceChildren(...notes);
      settle();
    }
    /* The most lines that can stay with the notes arranged so; the paragraph is left as it was. */
    function most(mode) {
      arrange(mode);
      const measured = textCuts(p);
      let best = 0;
      for (let k = measured.lines - MIN_LINES; k >= MIN_LINES && !best; k--) {
        if (cut(k, measured)) best = k;
        restore();
      }
      undo();
      return best;
    }

    // Prefer to keep the notes beside their text; they move only if that keeps more text here.
    const modes = ['all', ...(goers.length ? ['questions'] : []), ...(questions.length ? ['above'] : [])];
    let mode = null;
    let k = 0;
    for (const option of modes) {
      if (option === 'above' && singleColumn(page.el)) continue;
      const lines = most(option);
      if (lines > k) { k = lines; mode = option; }
    }
    if (!k) return null;
    arrange(mode);
    const tail = cut(k, textCuts(p));
    if (!tail) {                                         // cannot happen: the same layout as measured; stay safe
      undo();
      return null;
    }
    const rest = row.cloneNode(false);
    rest.removeAttribute('id');
    rest.classList.remove('bare', 'note-left', 'note-right', 'has-accent', 'has-doodle', 'split-head');
    rest.classList.add('split-tail');
    const restP = p.cloneNode(false);
    restP.removeAttribute('id');
    restP.classList.remove('cut');
    restP.append(tail);
    restP.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));   // ids stay with the first part
    const restMain = row.querySelector(':scope > .main').cloneNode(false);
    restMain.append(restP);
    if (side) {
      const restSide = side.cloneNode(false);
      restSide.style.cssText = '';
      if (mode !== 'all') restSide.append(...goers);
      rest.append(restSide);
    }
    rest.append(restMain);
    row.classList.add('split-head');
    settle();
    return rest;
  }

  /* A paragraph that fits at the foot of the page while its margin notes, taller than it, do not: the notes leave the
   * margin and go across the page - a question above the paragraph it asks about, a remark below it - as they would
   * on the next page anyway, so the paragraph does not leave a hole behind it. False if even that does not fit. */
  function widenOwnNotes(row) {
    const side = sideOf(row);
    if (singleColumn(page.el) || !isText(row) || !side || !side.children.length) return false;
    const notes = [...side.children];
    if (notes.some((n) => n.classList.contains('accent'))) return false;
    const made = [];
    let anchor = row;
    // Under a lead-in a remark would stand between it and its list: it goes above it.
    const lead = introducesNext(row);
    for (const note of notes) {
      const wide = wideNote([note], side);
      if (lead || note.textContent.trim().endsWith('?')) aboveOf(row).before(wide);
      else { anchor.after(wide); anchor = wide; }
      made.push(wide);
    }
    if (fits()) return true;
    for (const wide of made) { side.append(...wide.querySelector(':scope > .main').children); wide.remove(); }
    settle();
    return false;
  }

  /* The row's own sheet, code block or terminal ('pre'), or table ('table'), whose `box` splits; null for anything
   * else - a prompt, a callout, a list inside a card. */
  function framed(row, box) {
    const main = row.querySelector(':scope > .main');
    if (!main) return null;
    if (box.tagName === 'TBODY') return box.parentElement.parentElement === main ? 'table' : null;
    const holder = box.tagName === 'PRE' && box.closest('.code, .terminal, .sheet');
    return holder && holder.parentElement === main ? 'pre' : null;
  }

  /* A list of running text or a list of steps: the row's own block, not a list inside a callout or a card. */
  function isList(row, box) {
    const main = row.querySelector(':scope > .main');
    return !!main && (box.parentElement === main || box.parentElement.matches('.steps') &&
                      box.parentElement.parentElement === main) && (box.tagName === 'UL' || box.tagName === 'OL');
  }

  /* A note moved out of the margin into a row of its own across the page. Such a row is not in the stream: if it
   * has to leave the page, its note goes back to the margin it came from (`unplace`), so nothing is lost. */
  const homes = new WeakMap();
  function wideNote(children, home = null) {
    const wide = document.createElement('div');
    wide.className = 'row wide wide-note';
    const main = document.createElement('div');
    main.className = 'main';
    main.append(...children);
    wide.append(main);
    if (home) homes.set(wide, home);
    return wide;
  }

  /* A short paragraph that ends with a colon introduces the list after it: it never stays alone at the foot of a page
   * while its list opens the next one (the lead-in and its list are not torn apart). */
  function leadsInto(prev, row) {
    if (!prev || !row) return false;
    const para = prev.querySelector(':scope > .main > p:only-child');
    const list = row.querySelector(':scope > .main > ul, :scope > .main > ol, :scope > .main > .steps, :scope > .main table');
    return Boolean(para && list && !isHeading(prev) && para.textContent.trim().endsWith(':') &&
                   para.offsetHeight <= 3 * LINE + 1);
  }

  /* A paragraph that ends with a colon: the block after it belongs to it. */
  function introducesNext(row) {
    const para = row && row.querySelector(':scope > .main > p:only-child');
    return Boolean(para && !isHeading(row) && para.textContent.trim().endsWith(':'));
  }

  /* What a note put across the page above `row` stands before: the row itself, or its lead-in if a paragraph ending
   * with a colon introduces it - a note never stands between a lead-in and its list. */
  function aboveOf(row) {
    const prev = row.previousElementSibling;
    return prev && prev.classList.contains('row') && introducesNext(prev) ? prev : row;
  }

  /* Take a row off the page being filled. A row from the stream goes back into it; a note moved across the page
   * returns to its margin. */
  function unplace(row) {
    const home = homes.get(row);
    if (home) home.append(...row.querySelector(':scope > .main').children);
    else cursor--;
    row.remove();
  }

  /* Put the row stream[cursor - 1] on the page. What does not fit goes back into the stream and
   * opens the next page. */
  function place(row) {
    if (!page) startPage();
    // A heading, a table, a list of steps or any block that is not a plain paragraph: notes still hanging far below
    // the text go wide first, so no hole is left beside them.
    if (body && body.children.length && !(row.querySelector(':scope > .main > p:only-child') && !isHeading(row))) {
      widenHangingNotes();
    }
    body.append(row);
    if (fits()) { lighten(row); return; }
    // What does not fit: a long listing splits between its lines; a paragraph whose notes are taller than it stays
    // whole with its notes across the page; a paragraph splits between its lines.
    let rest = split(row);
    if (!rest && widenOwnNotes(row)) return;
    rest = rest || splitText(row) || splitPrompt(row);
    // Still too tall, and moving it on would leave more than a footer of size m can take: the page closes up its
    // gaps a little - the opposite of `spread` - if that lets the row, or a part of it, stay.
    if (!rest && !page.el.classList.contains('tight') && freeWithout(row) > ROOM) {
      page.el.classList.add('tight');
      if (fits()) { lighten(row); return; }
      if (widenOwnNotes(row)) return;
      rest = splitText(row);
      if (!rest) { page.el.classList.remove('tight'); settle(); }
    }
    if (rest) { stream.splice(cursor, 0, { kind: 'row', el: rest }); finishPage(); return; }
    if (isFirstOnPage(row)) {
      warn('too-tall', page, row.textContent, `page ${page.number}: a block is taller than the page and cannot be split: ` +
                    `"${row.textContent.trim().replace(/\s+/g, ' ').slice(0, 60)}"`, row);
      finishPage();
      return;
    }
    unplace(row);
    while (isHeading(body.lastElementChild) ||           // headings go with the block they introduce,
           body.lastElementChild?.classList.contains('keep-next') ||   // a prompt's hint with its monitor,
           leadsInto(body.lastElementChild, row)) {      // and a short lead-in with its list
      if (leadsInto(body.lastElementChild, row)) body.lastElementChild.classList.add('leads-on');
      unplace(body.lastElementChild);
    }
    // A section that would begin at the foot of the page with only a line or two of itself moves on whole.
    const rows = rowsOf(body);
    const last = rows.map(isHeading).lastIndexOf(true);
    if (last > 0 && !sectionFits()) {
      for (const row of rows.slice(last).reverse()) {
        row.querySelectorAll(':scope > .side > .accent').forEach((el) => el.remove());   // the next page decides anew
        row.classList.remove('has-accent', 'has-doodle');
        unplace(row);
      }
    }
    finishPage();
  }

  /* A prompt taller than a page goes on to a second monitor; one that fits a page always moves on whole.
   * The cut falls between its lines or,
   * inside a long line, at the end of a sentence ('. ', '? ', '! ' or ': ' before a capital or a digit); at least
   * PROMPT_MIN lines of the screen stay and as many go on. Of the cuts that keep nearly as much here, one at a blank
   * line or before a numbered item is preferred, then one between lines, then a sentence end. The first monitor is
   * sized anew to the smallest that holds its part; the second, on the next page, holds the rest under the same title
   * marked as continued. The hint stays with the first. The prompt is still exported whole (`book prompts`). */
  const PROMPT_MIN = 3;
  const SENTENCE_END = /[.?!:]\s+(?=[\p{Lu}\d\u00ab"])/gu;   // before a capital, a digit or a quote
  function screenLines(screen) {
    const range = document.createRange();
    range.selectNodeContents(screen);
    const line = parseFloat(getComputedStyle(screen).lineHeight) || LINE;
    return lineIndex([...range.getClientRects()].filter((r) => r.width > 0).map((r) => r.top), line).count;
  }
  /* Keep in `screen` only what comes before the cut (`before`), or only what comes after it. */
  function cutScreen(screen, { line, at }, before) {
    const lines = [...screen.children];
    if (before) {
      lines.slice(at ? line + 1 : line).forEach((el) => el.remove());
      if (at) {
        const range = document.createRange();
        range.setStart(...pointAt(lines[line], at));
        range.setEnd(lines[line], lines[line].childNodes.length);
        range.deleteContents();
      }
    } else {
      lines.slice(0, line).forEach((el) => el.remove());
      if (at) {
        const range = document.createRange();
        range.setStart(lines[line], 0);
        range.setEnd(...pointAt(lines[line], at));
        range.deleteContents();
      }
    }
  }
  function splitPrompt(row) {
    const prompt = row.querySelector(':scope > .main > .prompt');
    // A prompt is never cut in two while it fits a page: it moves on whole to the next page.
    // Only one taller than a page splits.
    if (!prompt || row.getBoundingClientRect().height <= MAX_BODY) return null;
    if (isFirstOnPage(row) || freeWithout(row) <= HOLE_MAX) return null;
    const screen = prompt.querySelector('.screen');
    if (screenLines(screen) < PROMPT_MIN * 2) return null;
    const original = row.cloneNode(true);
    const markup = screen.innerHTML;
    const width = prompt.style.width;
    const size = screen.style.fontSize;
    const reset = () => {
      screen.innerHTML = markup;
      prompt.style.width = width;
      screen.style.fontSize = size;
    };
    // Every cut, in reading order, with its rank: 0 a blank line or a numbered item, 1 between lines, 2 a sentence end.
    const texts = [...screen.children].map((el) => el.textContent);
    const cuts = [];
    texts.forEach((text, line) => {
      if (line > 0) {
        const natural = !text.trim() || !texts[line - 1].trim() || /^\s*\d+[.)]\s/.test(text);
        cuts.push({ line, at: 0, rank: natural ? 0 : 1 });
      }
      for (const match of text.matchAll(SENTENCE_END)) cuts.push({ line, at: match.index + match[0].length, rank: 2 });
    });
    // The rest of the prompt after a cut, on its own monitor; null if it would show fewer than PROMPT_MIN lines.
    const restOf = (cut) => {
      const rest = original.cloneNode(true);
      rest.removeAttribute('id');
      rest.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));
      rest.classList.remove('bare', 'note-left', 'note-right', 'has-accent', 'has-doodle', 'wide');
      rest.classList.add('prompt-cont');
      const restSide = sideOf(rest);
      if (restSide) restSide.innerHTML = '';             // the hint stays with the first monitor
      cutScreen(rest.querySelector('.screen'), cut, false);
      const label = rest.querySelector('.prompt-label');
      if (label) {
        const mark = document.createElement('span');
        mark.className = 'cont-mark';
        mark.textContent = config.continuation || '';
        label.append(mark);
      }
      body.append(rest);                                 // sized for its own lines
      const restPrompt = rest.querySelector('.prompt');
      sizeMonitor(restPrompt);
      const enough = screenLines(rest.querySelector('.screen')) >= PROMPT_MIN;
      rest.classList.toggle('wide', parseFloat(restPrompt.style.width) > MONITOR.narrow);   // stands alone, centred
      rest.remove();
      return enough ? rest : null;
    };
    // The cuts that leave the first monitor on this page, from the last one back, while they keep nearly as much.
    const fitting = [];
    for (let i = cuts.length - 1; i >= 0; i--) {
      reset();
      cutScreen(screen, cuts[i], true);
      sizeMonitor(prompt);
      const kept = screenLines(screen);
      if (fitting.length && kept < fitting[0].kept - 4) break;
      if (kept >= PROMPT_MIN && fits() && sectionFits()) fitting.push({ cut: cuts[i], kept });
    }
    fitting.sort((x, y) => x.cut.rank - y.cut.rank || y.kept - x.kept);
    for (const { cut } of fitting) {
      reset();
      const rest = restOf(cut);
      if (!rest) continue;
      cutScreen(screen, cut, true);
      sizeMonitor(prompt);
      settle();
      return rest;
    }
    reset();
    settle();
    return null;
  }

  /* The free space at the foot of the page without the row being placed (in mm). */
  function freeWithout(row) {
    const next = row.nextSibling;
    row.remove();
    const free = (MAX_BODY - settle()) / PX_PER_MM;
    body.insertBefore(row, next);
    settle();
    return free;
  }

  function placeFullPage(el) {
    finishPage();
    makePage(true).el.append(el);
  }

  /* A prompt's monitor is always a monitor: its screen is 4:3 and never stretches with the text.
   * The text decides the size instead: the smallest monitor its text fits on, from MONITOR_MIN up to
   * the whole width of the page. A monitor wider than the column beside a note stands alone in the middle of the
   * page, its character's words above it. Text that does not fit even the largest monitor is set a little smaller,
   * and only then goes on to a second monitor of the same size. Sized once, before pagination, from the text alone. */
  const MONITOR = { min: mm('--monitor-min'), max: mm('--monitor-max'), narrow: mm('--monitor-narrow'), step: 4,
                    scales: [1, 0.95, 0.9, 0.85] };
  function screenFits(screen) {
    const style = getComputedStyle(screen);
    const room = screen.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
    const used = [...screen.children].reduce((sum, line) => sum + line.offsetHeight, 0);
    return used <= room + 0.5;
  }
  function monitorWidths() {
    const widths = [];
    for (let w = MONITOR.min; w < MONITOR.max; w += MONITOR.step) widths.push(w);
    return [...widths, MONITOR.max];
  }
  function sizeMonitor(prompt) {
    const screen = prompt.querySelector('.screen');
    screen.style.fontSize = '';                          // a copied monitor brings the reduced size of the first
    const base = parseFloat(getComputedStyle(screen).fontSize);
    for (const scale of MONITOR.scales) {
      screen.style.fontSize = scale === 1 ? '' : (base * scale) + 'px';
      for (const w of monitorWidths()) {
        prompt.style.width = w + 'mm';
        if (screenFits(screen)) return true;
      }
    }
    return false;                                        // at the largest size and the smallest type: too long
  }
  function sizeMonitors() {
    for (const row of [...source.querySelectorAll('.row')]) {
      const prompt = row.querySelector(':scope > .main > .prompt');
      if (!prompt) continue;
      let current = row;
      while (!sizeMonitor(current.querySelector('.prompt'))) {
        // Keep as many lines as the largest monitor holds; the rest goes on to the next monitor.
        const screen = current.querySelector('.screen');
        const lines = [...screen.children];
        let keep = lines.length;
        while (keep > 1 && !screenFits(screen)) lines[--keep].style.display = 'none';
        lines.forEach((line) => { line.style.display = ''; });
        if (keep === lines.length) {                     // one line alone is taller than the largest monitor
          warn('monitor', null, lines[0].textContent,
               `a prompt line is too long for the largest monitor: "${lines[0].textContent.slice(0, 50)}"`);
          break;
        }
        const rest = current.cloneNode(true);
        lines.slice(keep).forEach((line) => line.remove());
        [...rest.querySelector('.screen').children].slice(0, keep).forEach((line) => line.remove());
        rest.querySelectorAll('.prompt-label, [id]').forEach((el) => (el.matches('[id]') ? el.removeAttribute('id') : el.remove()));
        const restSide = sideOf(rest);
        if (restSide) restSide.innerHTML = '';             // the hint stays with the first monitor
        current.after(rest);
        current = rest;
      }
      // A large monitor stands alone across the page: what was beside it goes above it.
      for (let r = row; r && r !== current.nextElementSibling; r = r.nextElementSibling) {
        const p = r.querySelector(':scope > .main > .prompt');
        if (!p || parseFloat(p.style.width) <= MONITOR.narrow) continue;
        r.classList.add('wide');
        const side = sideOf(r);
        if (side && side.children.length) {
          const above = wideNote(side.children);           // part of the stream: it is placed like any row
          above.classList.add('keep-next');                // and never stays behind its monitor
          r.before(above);
        }
      }
    }
  }
  sizeMonitors();

  // ---------------------------------------------------------------- lightness
  /* Wall-to-wall text is hard to read. When a paragraph lands on a page after a long
   * run of full-width text with nothing beside it, it gets an accent - a character or an object -
   * and shares its line with it; the rows after it flow on as usual. Two per page at most, only
   * beside a tall paragraph, and only if the page still fits. Never in an empty margin, never
   * just to fill a gap. */
  const hasMargin = (row) => { const side = sideOf(row); return !!side && side.children.length > 0; };
  const isParagraph = (row) => !row.classList.contains('wide') && !isHeading(row) && !hasMargin(row) &&
    row.querySelector(':scope > .main > p:only-child') !== null;
  function lighten(row) {
    if (!accents.length || singleColumn(page.el) || page.accents >= 2) return;
    if (!isParagraph(row) || !row.classList.contains('bare') || row.offsetHeight < ACCENT_FROM) return;
    let solid = 0;                                       // full-width text since the last thing in the margin
    for (const other of rowsOf(body)) {
      if (hasMargin(other)) solid = 0;
      else if (other.classList.contains('bare')) solid += other.offsetHeight;
    }
    if (solid < ACCENT_EVERY) return;
    const item = accents[accentIndex % accents.length];
    const el = document.createElement('div');
    const doodle = !!item.querySelector('.doodle');
    el.className = 'accent' + (doodle ? ' is-doodle' : '');
    el.innerHTML = stockCopy(item);
    const side = sideOf(row);
    side.append(el);
    row.classList.add('has-accent');
    if (doodle) row.classList.add('has-doodle');
    settle();
    side.style.marginTop = Math.max(0, (row.offsetHeight - side.offsetHeight) / 2) + 'px';   // centred on its paragraph
    if (!fits()) {
      el.remove();
      row.classList.remove('has-accent', 'has-doodle');
      side.style.marginTop = '';
      settle();
      return;
    }
    accentIndex++;
    page.accents++;
  }

  /* Notes that hang far below the last line of the page leave a hole beside them where text should be
   * (no empty place where content is expected). The lowest such note leaves
   * the margin and becomes a wide note across the page, under the text; repeated while it helps and fits.
   * A question goes above its own row instead: the paragraph beside it answers it. */
  function widenHangingNotes() {
    if (singleColumn(page.el)) return;
    for (let round = 0; round < 3; round++) {
      const rows = rowsOf(body);
      settle();
      const last = rows[rows.length - 1];
      if (!last || body.offsetHeight - (last.offsetTop + last.offsetHeight) < HANG_MAX) return;
      let lowest = null, owner = null;
      for (const row of rows) {
        const side = sideOf(row);
        if (!side || !side.children.length || row.classList.contains('has-accent')) continue;
        if (!lowest || side.offsetTop + side.offsetHeight > lowest.offsetTop + lowest.offsetHeight) {
          lowest = side; owner = row;
        }
      }
      if (!lowest) return;
      const note = lowest.lastElementChild;
      const wide = wideNote([note], lowest);
      // A question goes above the paragraph it asks about; any other note goes under the text, but never between a
      // lead-in and the list or table it introduces: there it stands above the lead-in.
      const tail = rows[rows.length - 1];
      if (note.textContent.trim().endsWith('?')) aboveOf(owner).before(wide);
      else if (introducesNext(tail)) tail.before(wide);
      else body.append(wide);
      if (!fits()) { lowest.append(note); wide.remove(); settle(); return; }
    }
  }

  // ---------------------------------------------------------------- no blank holes
  /* A page that ends early breathes instead of huddling at the top: its blocks move apart,
   * each by at most SPREAD_MAX. Headings stay tight to what they introduce. */
  function spread(gap) {
    const rows = rowsOf(body).filter((row, i) => i > 0 && !isHeading(row.previousElementSibling));
    if (!rows.length || gap < SPREAD_FROM) return;
    const extra = Math.min(gap * 0.6 / rows.length, SPREAD_MAX);
    for (const row of rows) row.style.marginTop = (parseFloat(getComputedStyle(row).marginTop) + extra) + 'px';
  }

  // ---------------------------------------------------------------- the run
  // One flat stream of rows and markers; a row that does not fit is put back into it.
  for (const section of [...source.children]) {
    if (section.classList.contains('fullpage')) { stream.push({ kind: 'cover', el: section }); continue; }
    stream.push({ kind: 'chapter', el: section });
    for (const el of [...section.children]) {
      const kind = ['fullpage', 'pagebreak', 'set-side'].find((name) => el.classList.contains(name)) || 'row';
      const side = kind === 'row' && sideOf(el);
      if (side) el.prepend(side);                        // a float wraps only the text that comes after it
      stream.push({ kind, el });
    }
    stream.push({ kind: 'end' });
  }
  while (cursor < stream.length) {
    const { kind, el } = stream[cursor];
    if (kind === 'row') { cursor++; place(el); continue; }
    if (kind === 'cover') { chapter = null; placeFullPage(el); }
    else if (kind === 'chapter') {
      accentIndex = 0;                                   // whatever rotates restarts with the chapter
      chapter = { number: el.dataset.num || '', title: el.dataset.title || '',
                  color: el.dataset.color || 'teal', side: el.dataset.side || 'outer', world: el.dataset.world || '',
                  large: 0 };
    } else if (kind === 'end' || kind === 'pagebreak') finishPage();
    else if (kind === 'fullpage') placeFullPage(el);
    else if (kind === 'set-side') {
      // A page has one layout, so switching sides ends a page that already has content.
      if (el.dataset.side !== chapter.side && page && body.children.length) finishPage();
      chapter.side = el.dataset.side;
      if (page) applySide();
    }
    cursor++;
  }
  source.remove();
  stock.remove();   // every ornament in use is a copy; the originals are no longer needed

  // ---------------------------------------------------------------- the first part of a split paragraph
  /* Its last line is justified because the sentence runs on overleaf. Should the finished page have set it short
   * after all, it is set ragged instead: wide gaps across a line are worse than a short line. */
  for (const p of book.querySelectorAll('.main > p.cut')) if (!fullLastLine(p)) p.classList.remove('cut');

  // ---------------------------------------------------------------- no stray lines under a note
  /* After layout, a paragraph whose last line runs out alone under its note to full width is reported:
   * that line reaches into the note's column, the earlier ones do not. */
  for (const record of pages) {
    let hanging = null;                                  // the margin of the last row with a note on this page
    for (const row of record.el.querySelectorAll('.row')) {
      const own = sideOf(row);
      if (own && own.children.length && !row.classList.contains('bare')) hanging = own;
      const side = row.classList.contains('bare') ? hanging : own;
      const text = row.querySelector(':scope > .main > p:last-child');
      if (!side || !text || !side.children.length) continue;
      if (row.getBoundingClientRect().top >= side.getBoundingClientRect().bottom) continue;
      keepTail(row, side);   // the finished page can differ from the one measured while filling it: settle the tail
      const wide = wideLines(text, side);
      if (wide.count === 1 && wide.last) {
        warn('tail-under-note', record, text.textContent.trim().slice(-40),
             `page ${record.number}: a paragraph leaves one line alone under its note: ` +
             `"${text.textContent.trim().slice(-40)}"`, text);
      }
    }
  }

  // ---------------------------------------------------------------- even word gaps
  /* A justified line whose word gaps stay wide after hyphenation (a long word, a bit of code or a no-break pair did
   * not fit at its end) has its letters spaced out by at most --track-max, which takes up part of its gaps. Only
   * whole words of plain text are touched, never code; the lines must break where they did, or the block is put back
   * as it was. Lines set ragged (a paragraph's last) have narrow gaps and are left alone. */
  const TRACK_TARGET = parseFloat(root.getPropertyValue('--track-target'));
  const TRACK_MAX = parseFloat(root.getPropertyValue('--track-max'));
  const BREAKS = /[ \t\n\r]/;                            // a no-break space glues: it is part of a word here
  const GAPS = /[ \t\n\r ]/;
  const charRange = document.createRange();
  function charTop(node, i) {
    charRange.setStart(node, i);
    charRange.setEnd(node, i + 1);
    // The last box: the letter after a soft hyphen that broke the line also gets that hyphen's box on the line above.
    const box = [...charRange.getClientRects()].filter((r) => r.width > 0 || r.height > 0).pop();
    return box ? box.top : null;
  }
  function textsOf(block, plain) {
    const out = [];
    const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const parent = node.parentElement;
      if (!node.data.length || parent.closest('svg') || parent.closest('p, li') !== block) continue;
      if (plain && parent.closest('code, kbd, .lead-in, .flag, sup, sub')) continue;
      out.push(node);
    }
    return out;
  }
  /* The top of the first and the last letter of every word of the block: a block whose tops stay within half a line
   * after a change has kept its line breaks. */
  function lineSignature(block) {
    const out = [];
    for (const node of textsOf(block, false)) {
      const text = node.data;
      for (let i = 0; i < text.length; i++) {
        if (BREAKS.test(text[i]) || (i > 0 && !BREAKS.test(text[i - 1]))) continue;
        let j = i;
        while (j + 1 < text.length && !BREAKS.test(text[j + 1])) j++;
        out.push(charTop(node, i) ?? -1, charTop(node, j) ?? -1);
      }
    }
    return out;
  }
  function track(block) {
    const em = parseFloat(getComputedStyle(block).fontSize);
    const half = (parseFloat(getComputedStyle(block).lineHeight) || em * 1.6) / 2;
    // Runs of whole words on one line inside one text node: what may be spaced out.
    const runs = [];
    for (const node of textsOf(block, true)) {
      const text = node.data;
      let run = null;
      for (let i = 0; i < text.length; i++) {
        if (BREAKS.test(text[i]) || (i > 0 && !BREAKS.test(text[i - 1]))) continue;
        let j = i;
        while (j + 1 < text.length && !BREAKS.test(text[j + 1])) j++;
        const top = charTop(node, i), bottom = charTop(node, j);
        // A word cut by a hyphen, or the first or last piece of a word that runs on into another element, is left out.
        const whole = top !== null && bottom !== null && Math.abs(top - bottom) < half &&
                      (i > 0 || !node.previousSibling) && (j + 1 < text.length || !node.nextSibling);
        if (whole && run && Math.abs(run.top - top) < half) run.end = j + 1;
        else if (whole) { run = { node, start: i, end: j + 1, top, order: runs.length }; runs.push(run); }
        else run = null;
        i = j;
      }
    }
    const lines = [];
    for (const run of runs) {
      let line = lines.find((l) => Math.abs(l.top - run.top) < half);
      if (!line) { line = { top: run.top, runs: [], gaps: 0, width: 0, letters: 0 }; lines.push(line); }
      line.runs.push(run);
      const text = run.node.data.slice(run.start, run.end);
      for (let k = 0; k < text.length; k++) {
        if (text[k] === '\u00ad') continue;            // a soft hyphen is no letter: it takes no spacing
        if (!GAPS.test(text[k])) { line.letters++; continue; }
        charRange.setStart(run.node, run.start + k);
        charRange.setEnd(run.node, run.start + k + 1);
        line.width += charRange.getBoundingClientRect().width;
        line.gaps++;
      }
    }
    const loose = lines.filter((l) => l.gaps && l.letters && l.width / l.gaps / em > TRACK_TARGET);
    if (!loose.length) return;
    const before = lineSignature(block);
    // Wrapped from the last run back, so the offsets of the runs before it in its node stay valid.
    const wraps = [];
    for (const line of loose) {
      const spacing = Math.min(TRACK_MAX, (line.width / line.gaps / em - TRACK_TARGET) * line.gaps / line.letters);
      for (const run of line.runs) wraps.push({ ...run, spacing });
    }
    wraps.sort((a, b) => b.order - a.order);
    const made = [];
    for (const { node, start, end, spacing } of wraps) {
      const range = document.createRange();
      range.setStart(node, start);
      range.setEnd(node, end);
      const span = document.createElement('span');
      span.className = 'tracked';
      range.surroundContents(span);
      made.push({ span, spacing });
    }
    // Rarely, the spacing lets the next line's word be hyphenated up: then less of it, or none.
    for (const share of [1, 0.5, 0.25]) {
      for (const { span, spacing } of made) span.style.letterSpacing = (spacing * share).toFixed(4) + 'em';
      const after = lineSignature(block);
      if (after.length === before.length && after.every((top, k) => Math.abs(top - before[k]) < half)) return;
    }
    for (const { span } of made) span.replaceWith(...span.childNodes);
    block.normalize();
  }
  for (const block of book.querySelectorAll('.p-body .main > p, .p-body .main li, .p-body .main li > p')) {
    if (getComputedStyle(block).textAlign === 'justify') track(block);
  }

  // ---------------------------------------------------------------- nothing runs into a picture
  /* Every line of text and every box on a page is checked against every drawing on it: the footer
   * scene, the character on the running head, accents, the characters of bubbles and quotes. Text
   * inside a drawing is the drawing's own. */
  // On a story opener every object of the picture has an invisible box (`.art-box`, from art/openers.py).
  const PICTURES = '.p-foot, .perch, .accent, .q-who, .say-who, .margin-talk .who, .opener-big, .opener-art .art-box';
  const BOXES = '.quote-card, .bubble, .terminal, .code, .crt, .sheet, .tree, table';
  const overlaps = (a, b) => a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;
  for (const record of pages) {
    if (record.el.classList.contains('full') && !record.el.querySelector('.opener')) continue;   // the cover: art over art
    const pictures = [...record.el.querySelectorAll(PICTURES)];
    const texts = [];
    const walker = document.createTreeWalker(record.el, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.textContent.trim() || node.parentElement.closest('svg')) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const rect of range.getClientRects()) texts.push({ el: node.parentElement, rect });
    }
    for (const box of record.el.querySelectorAll(BOXES)) texts.push({ el: box, rect: box.getBoundingClientRect() });
    // Nothing runs off the sheet: a long word, a wide line of code or table never leaves the paper.
    const sheet = record.el.getBoundingClientRect();
    const off = texts.find((t) => t.rect.width > 0 &&
                                  (t.rect.left < sheet.left + EDGE_MIN || t.rect.right > sheet.right - EDGE_MIN));
    if (off) {
      warn('off-sheet', record, off.el.textContent,
           `page ${record.number}: "${off.el.textContent.trim().replace(/\s+/g, ' ').slice(0, 50)}" ` +
           `runs off the edge of the page`, off.rect);
    }
    for (const picture of pictures) {
      const area = picture.getBoundingClientRect();
      const hit = texts.find((t) => !picture.contains(t.el) && !t.el.contains(picture) && overlaps(area, t.rect));
      if (hit) {
        const kind = picture.className.baseVal !== undefined ? picture.getAttribute('class') : picture.className;
        warn('into-picture', record, hit.el.textContent,
             `page ${record.number}: "${hit.el.textContent.trim().replace(/\s+/g, ' ').slice(0, 50)}" ` +
             `runs into a picture (${kind.split(' ')[0]})`, hit.rect);
      }
    }
  }

  // ---------------------------------------------------------------- a monitor shows all of its text
  for (const record of pages) {
    for (const screen of record.el.querySelectorAll('.screen')) {
      if (!screenFits(screen)) {
        warn('monitor', record, screen.textContent.trim().slice(0, 40),
             `page ${record.number}: a prompt does not fit its monitor and is cut: ` +
             `"${screen.textContent.trim().slice(0, 40)}"`, screen);
      }
    }
  }

  // ---------------------------------------------------------------- a note beside its own block
  /* A margin note is read as a comment on the block it stands beside. If notes above pushed it down past the end
   * of its block, it would seem to comment on something else: report it. */
  for (const record of pages) {
    for (const row of record.el.querySelectorAll('.row.note-left, .row.note-right')) {
      const side = sideOf(row);
      const main = row.querySelector(':scope > .main');
      if (!side || !main || row.classList.contains('has-accent')) continue;
      const lastLine = main.getBoundingClientRect().bottom;
      if (side.getBoundingClientRect().top > lastLine - 4) {
        warn('note-below-block', record, side.textContent,
             `page ${record.number}: a note stands below the block it belongs to: ` +
             `"${side.textContent.trim().replace(/\s+/g, ' ').slice(0, 50)}"`, side);
      }
    }
  }

  // ---------------------------------------------------------------- a lead-in stays with its list
  /* A paragraph ending with a colon introduces the block after it; a note across the page never stands between them.
   * A prompt's hint above its monitor is part of the prompt and may. */
  for (const record of pages) {
    for (const wide of record.el.querySelectorAll('.row.wide-note:not(.keep-next)')) {
      const prev = wide.previousElementSibling;
      if (prev && prev.classList.contains('row') && introducesNext(prev)) {
        warn('note-in-lead-in', record, prev.textContent,
             `page ${record.number}: a note stands between a lead-in and what it introduces: ` +
             `"${prev.textContent.trim().replace(/\s+/g, ' ').slice(0, 50)}"`, wide);
      }
    }
  }

  // Fill in the page numbers of the table of contents.
  for (const cell of book.querySelectorAll('[data-ref]')) {
    const target = document.getElementById(cell.dataset.ref);
    const holder = target && target.closest('.page');
    if (holder) cell.textContent = holder.dataset.page;
    else warn('links', null, cell.dataset.ref, `contents: no heading found for "${cell.dataset.ref}"`);
  }

  /* Every id in the document is unique. Drawings made once and reused (a cached prop, the base of the monitor), and
   * the footers drawn in another process, may bring ids that are already taken; a reference to a taken id would
   * resolve to whichever came first - another drawing's clip path or gradient. So every drawing whose ids are
   * taken gets fresh ones, with its own references renamed alike. */
  let renamed = 0;
  function uniqueIds() {
    const seen = new Set([...document.querySelectorAll('[id]')].filter((el) => !el.closest('svg')).map((el) => el.id));
    const svgs = [...document.querySelectorAll('svg')].filter((svg) => !svg.parentElement.closest('svg'));
    for (const svg of svgs) {
      let ids = [...svg.querySelectorAll('[id]')].map((el) => el.id);
      if (ids.some((id) => seen.has(id))) {
        const suffix = `-u${++renamed}`;
        const fresh = (id) => (ids.includes(id) ? id + suffix : id);
        const holder = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        holder.innerHTML = svg.outerHTML
          .replace(/\bid="([^"]+)"/g, (m, id) => `id="${fresh(id)}"`)
          .replace(/url\(#([^)]+)\)/g, (m, id) => `url(#${fresh(id)})`)
          .replace(/href="#([^"]+)"/g, (m, id) => `href="#${fresh(id)}"`);
        svg.replaceWith(holder.firstElementChild);
        ids = ids.map(fresh);
      }
      ids.forEach((id) => seen.add(id));
    }
  }
  uniqueIds();

  // Footer scenes are drawn by Python: publish the requests, receive the SVG.
  const withFoot = pages.filter((p) => p.foot);
  // Each footer is drawn for its page: Python reads the page's headings and text to pick an episode about them.
  const textOf = (p) => plain((p.el.querySelector('.p-body') || p.el).innerText).replace(/\s+/g, ' ').slice(0, 6000);
  const headsOf = (p) => [...p.el.querySelectorAll('.p-body h1, .p-body h2, .p-body h3')].map((h) => plain(h.innerText)).join(' | ');
  window.__bookScenes = withFoot.map((p) => ({ page: p.number, clear: p.foot.clear, mm: p.foot.height, size: p.foot.size,
                                               chapter: p.chapter, world: p.world, text: textOf(p), heads: headsOf(p),
                                               accent: getComputedStyle(p.el).getPropertyValue('--accent').trim() }));
  window.__setScenes = (list) => {
    list.forEach((svg, i) => withFoot[i].foot.el.insertAdjacentHTML('afterbegin', svg));
    uniqueIds();
    // Ids may repeat only inside one drawing that holds the same cached piece twice - identical definitions.
    const all = [...document.querySelectorAll('svg [id]')];
    const owner = new Map();
    for (const el of all) {
      const top = el.closest('svg:not(svg svg)') || el.ownerSVGElement;
      if (owner.has(el.id) && owner.get(el.id) !== top) return `id "${el.id}" is used by two drawings`;
      owner.set(el.id, top);
    }
    return null;
  };
  // Every footer's size and what ended its page: the build checks that large ones stay rare (render.py).
  const feet = withFoot.map((p) => ({ page: p.number, chapter: p.chapter, mm: p.foot.height, size: p.foot.size,
                                      end: p.foot.end, blocker: p.foot.blocker, free: p.foot.free }));
  const promptParts = document.querySelectorAll('.prompt-cont').length;
  window.__bookReport = { pages: pages.length, warnings, findings, feet, prompt_parts: promptParts };
  window.__bookReady = true;
})().catch((error) => {
  window.__bookError = String(error && error.stack || error);
  window.__bookReady = true;
});
