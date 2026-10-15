'use strict';
// Dependency-free VM/DOM behavior simulation. This is deliberately not browser,
// accessibility-engine, visual, touch, or mobile-layout verification.
// Standalone: node tests/test_collected_view.cjs
// Optional historical checks: node tests/test_collected_view.cjs --baseline PATH
// or COLLECTION_BASELINE=PATH node tests/test_collected_view.cjs.
// No implicit/untracked historical snapshot is needed. This suite does not admit
// editions: edition_pipeline.py must separately enforce exact mapped promotions,
// unchanged main content/UI, approved additions and the full runtime allowlist.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {webcrypto, createHash} = require('node:crypto');
const root = path.join(__dirname, '../dist');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'catalog.json'), 'utf8'));
const tick = () => new Promise(resolve => setImmediate(resolve));
const clone = value => JSON.parse(JSON.stringify(value));
const descendants = node => node.children.flatMap(child => [child, ...descendants(child)]);
const decode = value => value.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");

function harness({inventory, collectionFetch, catalogFetch, esotericaInventory, esotericaFetch} = {}) {
  const ids = new Map(), calls = [], values = new Map(), routes = [], timers = new Set();
  let document;
  class El {
    constructor(tag = 'div') {
      this.tagName = tag.toUpperCase(); this.children = []; this.parentElement = null;
      this.dataset = {}; this.attributes = {}; this.events = {}; this.style = {setProperty: (key, value) => this.style[key] = value};
      this._text = ''; this._className = ''; this._hidden = false; this.disabled = false; this.scrollTop = 0; this.open = false; this.value = '';
      this.classList = {
        add: (...names) => { this.className = [...new Set([...this.className.split(/\s+/).filter(Boolean), ...names])].join(' '); },
        remove: (...names) => { this.className = this.className.split(/\s+/).filter(value => !names.includes(value)).join(' '); },
        contains: name => this.className.split(/\s+/).includes(name),
        toggle: (name, force) => { const set = force ?? !this.classList.contains(name); this.classList[set ? 'add' : 'remove'](name); return set; }
      };
    }
    set textContent(value) { this._text = String(value); this.detachChildren(); }
    get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
    set innerHTML(value) { throw Error('Unsafe or unsupported innerHTML assignment in the collection behavior simulation: ' + value); }
    get innerHTML() { throw Error('HTML serialization is not implemented by this behavior harness'); }
    set className(value) { this._className = String(value); this.attributes.class = this._className; }
    get className() { return this._className; }
    set hidden(value) { this._hidden = !!value; if (this._hidden) this.attributes.hidden = ''; else delete this.attributes.hidden; }
    get hidden() { return this._hidden; }
    set id(value) { this._id = String(value); this.attributes.id = this._id; ids.set(this._id, this); }
    get id() { return this._id || ''; }
    get isConnected() { return this === document.documentElement || !!this.parentElement?.isConnected; }
    get options() { return this.children.filter(child => child.tagName === 'OPTION'); }
    detachChildren() { this.children.forEach(child => {child.parentElement = null;}); this.children = []; }
    append(...nodes) { nodes.forEach(node => { if (typeof node !== 'object') {const text = new El('#text'); text.textContent = node; node = text;} if (node.parentElement) node.parentElement.children = node.parentElement.children.filter(child => child !== node); node.parentElement = this; this.children.push(node); }); }
    appendChild(node) { this.append(node); return node; }
    replaceChildren(...nodes) { this._text = ''; this.detachChildren(); this.append(...nodes); }
    remove() { if (this.parentElement) this.parentElement.children = this.parentElement.children.filter(child => child !== this); this.parentElement = null; }
    setAttribute(name, value) { value = String(value); this.attributes[name] = value; if (name === 'id') this.id = value; else if (name === 'class') this.className = value; else if (name === 'hidden') this.hidden = true; else if (name === 'disabled') this.disabled = true; else if (name === 'value') this.value = value; else if (name.startsWith('data-')) this.dataset[name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase())] = value; else if (['href', 'target', 'rel', 'type', 'tabIndex'].includes(name)) this[name] = value; }
    getAttribute(name) { return Object.hasOwn(this.attributes, name) ? this.attributes[name] : null; }
    hasAttribute(name) { return Object.hasOwn(this.attributes, name); }
    removeAttribute(name) { delete this.attributes[name]; if (name === 'hidden') this._hidden = false; if (name === 'disabled') this.disabled = false; }
    addEventListener(name, fn) { (this.events[name] ||= []).push(fn); }
    dispatchEvent(event) { event.target ||= this; event.currentTarget = this; event.preventDefault ||= () => { event.defaultPrevented = true; }; const outputs = []; if (typeof this['on' + event.type] === 'function') outputs.push(this['on' + event.type](event)); for (const fn of this.events[event.type] || []) outputs.push(fn(event)); return outputs; }
    click() { if (this.disabled) return []; return this.dispatchEvent({type: 'click'}); }
    focus() { document.activeElement = this; }
    showModal() { this.open = true; }
    close() { this.open = false; }
    matches(selector) { const tag = selector.match(/^[a-z][\w-]*/i)?.[0]; if (tag && this.tagName !== tag.toUpperCase()) return false; const id = selector.match(/#([\w-]+)/)?.[1]; if (id && this.id !== id) return false; for (const match of selector.matchAll(/\.([\w-]+)/g)) if (!this.classList.contains(match[1])) return false; for (const match of selector.matchAll(/\[([^\]=]+)(?:=["']?([^\]"']+)["']?)?\]/g)) { if (!this.hasAttribute(match[1])) return false; if (match[2] !== undefined && this.getAttribute(match[1]) !== match[2]) return false; } return true; }
    querySelectorAll(selector) { return descendants(this).filter(node => selector.split(',').some(part => node.matches(part.trim()))); }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
    closest(selector) { for (let node = this; node; node = node.parentElement) if (node.matches(selector)) return node; return null; }
    getBoundingClientRect() { if (this === ids.get('reading-scroll')) return {top: 58, bottom: 764, height: 706}; const index = this.parentElement?.children.indexOf(this) || 0, top = 100 + index * 100 - ids.get('reading-scroll').scrollTop; return {top, bottom: top + 100, height: 100}; }
  }
  const documentElement = new El('html');
  document = {documentElement, activeElement: null, hidden: false, events: {}, getElementById: id => ids.get(id) || null, createElement: tag => new El(tag), createTextNode: text => {const node = new El('#text'); node.textContent = text; return node;}, addEventListener(name, fn) {(this.events[name] ||= []).push(fn);}, querySelectorAll: selector => documentElement.querySelectorAll(selector), querySelector: selector => documentElement.querySelector(selector)};
  const stack = [documentElement], voids = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']);
  for (const token of html.matchAll(/<!--[\s\S]*?-->|<![^>]*>|<[^>]+>|[^<]+/g)) {
    const part = token[0]; if (part.startsWith('<!')) continue;
    if (part.startsWith('</')) { const tag = part.slice(2, -1).trim().toUpperCase(); while (stack.length > 1 && stack.pop().tagName !== tag) {} continue; }
    if (part.startsWith('<')) {const tag = part.match(/^<([\w-]+)/)?.[1]; if (!tag) continue; if (tag === 'html') continue; const node = new El(tag); for (const match of part.slice(tag.length + 1, -1).matchAll(/([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) node.setAttribute(match[1], decode(match[2] ?? match[3] ?? match[4] ?? '')); stack.at(-1).append(node); if (tag === 'body') document.body = node; if (!voids.has(tag) && !part.endsWith('/>')) stack.push(node); }
    else if (part) stack.at(-1).append(document.createTextNode(decode(part)));
  }
  document.activeElement = document.body;
  const location = {hash: '', pathname: '/', search: ''};
  const responseFor = file => ({ok: fs.existsSync(file), json: async () => JSON.parse(fs.readFileSync(file, 'utf8')), arrayBuffer: async () => Uint8Array.from(fs.readFileSync(file)).buffer});
  const context = {console, document, location, history: {pushState(data, title, url) {routes.push(url); location.hash = url.startsWith('#') ? url : '';}, replaceState(data, title, url) {location.hash = url;}}, localStorage: {getItem: key => values.get(key) || null, setItem: (key, value) => values.set(key, value)}, fetch: async url => {calls.push(url); if (url === 'collections.json') {if (collectionFetch) return collectionFetch(calls.filter(call => call === url).length); if (inventory) return {ok: true, json: async () => clone(inventory)};} if (url === 'esoterica-register.json') {if (esotericaFetch) return esotericaFetch(calls.filter(call => call === url).length); if (esotericaInventory) return {ok: true, json: async () => clone(esotericaInventory)};} if (url === 'catalog.json' && catalogFetch) return catalogFetch(calls.filter(call => call === url).length); return responseFor(path.join(root, url));}, window: {addEventListener() {}}, requestAnimationFrame: fn => fn(), URL, URLSearchParams, TextEncoder, TextDecoder, crypto: webcrypto, Intl, Uint8Array, setTimeout(fn, delay) {const timer = setTimeout(() => {timers.delete(timer); fn();}, delay); timer.unref(); timers.add(timer); return timer;}, clearTimeout(timer) {timers.delete(timer); clearTimeout(timer);}};
  vm.createContext(context);
  for (const file of ['reader-core.js', 'app.js', 'collection.js']) vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), context, {filename: file});
  const get = id => {const node = ids.get(id); assert(node, 'Missing DOM node #' + id); return node;};
  return {get, document, calls, values, routes, location, timers, run: code => vm.runInContext(code, context), async settle() {await tick(); await tick(); await tick();}, async click(node) {await Promise.all(node.click()); await this.settle();}, async change(id, value, type = 'change') {get(id).value = value; await Promise.all(get(id).dispatchEvent({type})); await this.settle();}};
}

// The scenarios below intentionally inspect the rendered controls and exercise
// app.js's actual reader state rather than replacing openBook with a stub.
const inventory = JSON.parse(fs.readFileSync(path.join(root, 'collections.json'), 'utf8'));
const esoterica = JSON.parse(fs.readFileSync(path.join(root, 'esoterica-register.json'), 'utf8'));
const args = process.argv.slice(2);
assert(args.length === 0 || (args.length === 2 && args[0] === '--baseline' && args[1]),
  'Usage: node tests/test_collected_view.cjs [--baseline PATH]');
const baselinePath = args[1] || process.env.COLLECTION_BASELINE;
const baseline = baselinePath ? JSON.parse(fs.readFileSync(path.resolve(baselinePath), 'utf8')) : null;
const sourceIntegrity = {assets: 0, priorReaders: 0, priorSourceFiles: 0};
const overlapReaderIds = ['plato-apology', 'plato-republic', 'plato-symposium'];
const secondarySummary = '37 registered file slots · 3 already-readable editions (also in the main collection) · 34 source files not recovered';
const counts = Object.fromEntries(['readable', 'needs-source-review', 'quarantined', 'missing'].map(status => [status, inventory.entries.filter(entry => entry.status === status).length]));
const cards = env => env.get('collection-results').children.filter(node => node.classList.contains('collection-card'));
const actions = card => descendants(card).filter(node => node.classList.contains('collection-action'));
const links = node => descendants(node).filter(child => child.tagName === 'A');
const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
const seen = env => cards(env).map(card => card.dataset.entryId);
const assertions = [];
async function check(label, fn) {await fn(); assertions.push(label); console.log('PASS: ' + label);}
async function openCollection(env) {await env.settle(); await env.click(env.get('view-collected'));}
async function openEsoterica(env) {await openCollection(env); await env.change('collection-register-filter', 'esoterica');}
function beginChange(env, id, value) {env.get(id).value = value; return env.get(id).dispatchEvent({type: 'change'});}
function response(data) {return {ok: true, json: async () => clone(data)};}
function requestCount(env, url) {return env.calls.filter(call => call === url).length;}
function assertMain(env) {
  assert.equal(env.get('collection-register-filter').value, 'main');
  assert.deepEqual(seen(env), inventory.entries.map(entry => entry.id));
  assert.equal(env.get('collection-summary').textContent, `${inventory.entries.length} catalog entries · ${counts.readable} reading editions · ${counts['needs-source-review']} need source review · ${counts.quarantined} quarantined · ${counts.missing} missing text`);
  assert.equal(env.get('collection-load-status').textContent, 'Showing 135 of 135 catalog entries.');
  assert.equal(env.get('collection-retry').hidden, true);
}
function assertEsoterica(env) {
  assert.equal(env.get('collection-register-filter').value, 'esoterica');
  assert.deepEqual(seen(env), esoterica.entries.map(entry => entry.id));
  assert.equal(env.get('collection-summary').textContent, secondarySummary);
  assert.equal(env.get('collection-load-status').textContent, 'Showing 37 of 37 registered file slots.');
  assert.equal(env.get('collection-retry').hidden, true);
}
async function badSecondaryThenRetry(label, mutation) {
  const broken = clone(esoterica); mutation(broken);
  const env = harness({esotericaFetch: async count => response(count === 1 ? broken : esoterica)});
  await openEsoterica(env); assertFailure(env, label);
  assert.match(env.get('collection-load-status').textContent, /esoterica register/i, label + ': failure is scoped');
  await env.click(env.get('collection-retry')); assertEsoterica(env);
  assert.equal(requestCount(env, 'esoterica-register.json'), 2);
  await env.change('collection-register-filter', 'main'); assertMain(env);
  assert.equal(requestCount(env, 'collections.json'), 1, label + ': valid main cache survives');
}
function assertFailure(env, label) {
  assert.match(env.get('collection-load-status').textContent, /could not be loaded/i, label);
  assert.equal(env.get('collection-summary').textContent, '', label + ': no unverified totals');
  assert.equal(env.get('collection-results').children.length, 0, label + ': no stale or unsafe cards');
  assert.equal(env.get('collection-retry').hidden, false, label + ': explicit retry available');
  assert.equal(env.get('reader').hidden, true, label + ': does not open an unverified source');
  assert.equal(env.get('shelves').children.flatMap(group => group.children[1].children).length, catalog.length, label + ': existing shelf survives');
}
async function badThenRetry(label, mutation) {
  const broken = clone(inventory); mutation(broken);
  const env = harness({collectionFetch: async count => ({ok: true, json: async () => count === 1 ? broken : clone(inventory)})});
  await openCollection(env); assertFailure(env, label);
  await env.click(env.get('collection-retry'));
  assert.deepEqual(seen(env), inventory.entries.map(entry => entry.id), label + ': retry restores full inventory');
  assert.equal(env.get('collection-retry').hidden, true);
  assert.equal(env.calls.filter(url => url === 'collections.json').length, 2);
}

(async () => {
  const env = harness();
  await check('reading shelf remains the initial view and inventory is not fetched at startup', async () => {
    await env.settle();
    assert.deepEqual(env.calls, ['catalog.json', 'sections.json']);
    assert.equal(env.get('reading-shelf-panel').hidden, false);
    assert.equal(env.get('collected-panel').hidden, true);
    assert.equal(env.get('reader').hidden, true);
    assert.equal(env.get('view-reading').getAttribute('aria-pressed'), 'true');
    assert.equal(env.get('view-collected').getAttribute('aria-pressed'), 'false');
    assert.equal(env.get('edition-count').textContent, catalog.length + ' reading editions');
    assert.equal(env.get('shelves').children.flatMap(group => group.children[1].children).length, catalog.length);
    assert.equal(env.get('collection-results').children.filter(node => node.tagName !== '#TEXT').length, 0);
    assert.equal(env.get('skip-library').href, '#shelves');
    assert.deepEqual([...env.values.keys()].filter(key => key.includes('bookmark:') || key.endsWith(':last')), []);
  });
  await check('view controls are native keyboard-focusable buttons with panel/pressed relationships', async () => {
    for (const [id, panel] of [['view-reading', 'reading-shelf-panel'], ['view-collected', 'collected-panel']]) {
      const button = env.get(id); assert.equal(button.tagName, 'BUTTON'); assert.equal(button.type, 'button'); assert.equal(button.disabled, false); assert.notEqual(button.getAttribute('tabindex'), '-1'); assert.equal(button.getAttribute('aria-controls'), panel);
      button.focus(); assert.equal(env.document.activeElement, button);
      // A click models activation after native keyboard handling; this test does
      // not claim to simulate a browser's Enter/Space default actions.
      await env.click(button); assert.equal(env.document.activeElement, button, 'View activation retains focus');
      assert.equal(button.getAttribute('aria-pressed'), 'true');
    }
    assert.equal(env.get('reading-shelf-panel').hidden, true); assert.equal(env.get('collected-panel').hidden, false);
    assert.equal(env.get('view-reading').getAttribute('aria-pressed'), 'false');
    assert.equal(env.get('skip-library').href, '#collection-search');
    for (const id of ['collection-search', 'collection-status-filter', 'collection-tradition-filter']) assert(env.document.querySelector('label[for="' + id + '"]'), id + ' has a visible label');
    assert.equal(env.get('collection-load-status').getAttribute('aria-live'), 'polite');
  });
  await check('all inventory entries appear with truthful per-status totals and exactly the existing reader IDs', async () => {
    assert.equal(inventory.entries.length, inventory.summary.entries);
    assert.deepEqual(seen(env), inventory.entries.map(entry => entry.id));
    assert.equal(cards(env).length, inventory.summary.entries);
    assert.equal(counts.readable, catalog.length);
    assert.equal(env.get('collection-summary').textContent, `${inventory.entries.length} catalog entries · ${counts.readable} reading editions · ${counts['needs-source-review']} need source review · ${counts.quarantined} quarantined · ${counts.missing} missing text`);
    assert.equal(env.get('collection-load-status').textContent, `Showing ${inventory.entries.length} of ${inventory.entries.length} catalog entries.`);
    assert.deepEqual(env.calls, ['catalog.json', 'sections.json', 'collections.json', 'catalog.json']);
    assert(!env.calls.some(url => url.startsWith('books/')), 'Inventory browsing must not fetch reading sources');
    const labels = {readable: 'Reading edition available', 'needs-source-review': 'Needs source review', quarantined: 'Quarantined source', missing: 'Source missing'};
    for (const entry of inventory.entries) {
      const card = cards(env).find(card => card.dataset.entryId === entry.id); assert(card);
      assert.equal(card.dataset.status, entry.status); assert.equal(card.querySelector('h3').textContent, entry.title);
      assert.equal(card.querySelector('.collection-badge').textContent, labels[entry.status]);
      assert.equal(card.querySelector('.collection-source-note').textContent, entry.source_note);
      assert.equal(actions(card).length, entry.status === 'readable' ? 1 : 0, entry.id + ' must not manufacture a readable edition');
      if (entry.status === 'readable') assert.equal(actions(card)[0].dataset.readerId, entry.reader_id);
      for (const link of links(card)) {assert.match(link.href, /^https:\/\//); assert.equal(new URL(link.href).username, ''); assert.equal(new URL(link.href).password, ''); assert.equal(link.target, '_blank'); assert.match(link.rel, /noopener/);}
    }
    assert.deepEqual(cards(env).flatMap(actions).map(button => button.dataset.readerId).sort(), catalog.map(book => book.id).sort());
    assert(!/\/workspace\/|\/tmp\/|file:\/\/|source-audit\/|[A-Z]:\\/i.test(env.get('collection-results').textContent));
  });
  await check('status and tradition selectors cover every entry without turning missing/quarantined sources into read actions', async () => {
    assert.deepEqual(env.get('collection-tradition-filter').children.map(option => option.value), ['all', ...new Set(inventory.entries.map(entry => entry.tradition).sort((a, b) => a.localeCompare(b)))]);
    for (const status of Object.keys(counts)) {
      await env.change('collection-status-filter', status);
      assert.deepEqual(seen(env), inventory.entries.filter(entry => entry.status === status).map(entry => entry.id));
      if (status !== 'readable') assert.equal(cards(env).flatMap(actions).length, 0);
    }
    await env.change('collection-status-filter', 'all');
    for (const tradition of new Set(inventory.entries.map(entry => entry.tradition))) {
      await env.change('collection-tradition-filter', tradition);
      assert.deepEqual(seen(env), inventory.entries.filter(entry => entry.tradition === tradition).map(entry => entry.id));
    }
    await env.change('collection-tradition-filter', 'all');
  });
  await check('combined filters are an intersection; search supports titles, aliases, authors and accent/case-insensitive terms', async () => {
    const probes = ['  PLATO   REPUBLIC  ', 'Panchatantra', 'Babbitt', 'Anansi Tales', 'Enuma Elis', 'never-a-real-title-97931'];
    for (const query of probes) {
      await env.change('collection-search', query, 'input');
      const terms = normalize(query).trim().split(/\s+/).filter(Boolean);
      const expected = inventory.entries.filter(entry => {const text = normalize([entry.title, entry.original_catalog_title, entry.author, entry.edition, entry.tradition, ...entry.aliases].filter(Boolean).join(' ')); return terms.every(term => text.includes(term));});
      if (!query.startsWith('never-a-real-title')) assert(expected.length > 0, 'Positive search fixture must find a catalog entry: ' + query);
      assert.deepEqual(seen(env), expected.map(entry => entry.id), query);
      assert.equal(env.get('collection-load-status').textContent, `Showing ${expected.length} of ${inventory.entries.length} catalog entries.`);
    }
    assert.match(env.get('collection-results').textContent, /No entries match/);
    for (const status of Object.keys(counts)) {
      const target = inventory.entries.find(entry => entry.status === status), query = target.title.split(/\s+/)[0];
      await env.change('collection-search', query, 'input'); await env.change('collection-status-filter', status); await env.change('collection-tradition-filter', target.tradition);
      const expected = inventory.entries.filter(entry => entry.status === status && entry.tradition === target.tradition && normalize([entry.title, entry.original_catalog_title, entry.author, entry.edition, entry.tradition, ...entry.aliases].join(' ')).includes(normalize(query)));
      assert.deepEqual(seen(env), expected.map(entry => entry.id), 'combined filters for ' + status);
      assert(seen(env).includes(target.id));
    }
    await env.change('collection-search', '', 'input'); await env.change('collection-status-filter', 'all'); await env.change('collection-tradition-filter', 'all');
    assert.deepEqual(seen(env), inventory.entries.map(entry => entry.id));
    assert.equal(env.calls.filter(url => url === 'collections.json').length, 1, 'Filtering never refetches inventory');
  });
  await check('repeated view toggles reuse inventory, retain filter values and preserve native focus', async () => {
    await env.change('collection-search', 'Plato', 'input'); await env.change('collection-status-filter', 'readable'); await env.change('collection-tradition-filter', 'philosophy');
    const before = seen(env), requests = [...env.calls];
    for (let i = 0; i < 3; i++) {
      env.get('view-reading').focus(); await env.click(env.get('view-reading')); assert.equal(env.get('reading-shelf-panel').hidden, false); assert.equal(env.get('collected-panel').hidden, true); assert.equal(env.get('skip-library').href, '#shelves'); assert.equal(env.document.activeElement, env.get('view-reading'));
      env.get('view-collected').focus(); await env.click(env.get('view-collected')); assert.deepEqual(seen(env), before); assert.equal(env.document.activeElement, env.get('view-collected'));
    }
    assert.deepEqual(env.calls, requests); assert.equal(env.get('collection-search').value, 'Plato'); assert.equal(env.get('collection-status-filter').value, 'readable'); assert.equal(env.get('collection-tradition-filter').value, 'philosophy');
    await env.change('collection-search', '', 'input'); await env.change('collection-status-filter', 'all'); await env.change('collection-tradition-filter', 'all');
  });
  await check('each readable inventory action opens its exact existing edition and returns to the same collected card', async () => {
    for (const entry of inventory.entries.filter(entry => entry.status === 'readable')) {
      const card = cards(env).find(card => card.dataset.entryId === entry.id), button = actions(card)[0]; button.focus(); await env.click(button);
      assert.equal(env.run('state.active.id'), entry.reader_id); assert.equal(env.run('state.ready'), true); assert.equal(env.get('reader').hidden, false); assert.equal(env.get('library').hidden, true); assert(env.get('book-text').textContent.trim().length > 0);
      await env.click(env.get('back')); assert.equal(env.get('reader').hidden, true); assert.equal(env.get('library').hidden, false); assert.equal(env.get('collected-panel').hidden, false); assert.equal(env.get('reading-shelf-panel').hidden, true); assert.equal(env.document.activeElement, button); assert.equal(env.location.hash, '');
    }
  });
  await check('reader page and within-passage bookmarks survive close, view changes and collected-view reopen', async () => {
    let button = cards(env).flatMap(actions).find(node => node.dataset.readerId === 'plato-republic'); button.focus(); await env.click(button); env.run('turnPage(1)'); const offset = env.run('state.pages[state.page].start'); env.get('reading-scroll').scrollTop = 170; env.run('savePosition()'); const saved = env.values.get('mythic:bookmark:v2:plato-republic'); assert(saved);
    await env.click(env.get('back')); assert.equal(env.document.activeElement, button); const afterClose = env.values.get('mythic:bookmark:v2:plato-republic'); assert.equal(afterClose, saved);
    await env.click(env.get('view-reading')); await env.click(env.get('view-collected')); assert.equal(env.values.get('mythic:bookmark:v2:plato-republic'), saved, 'Collection navigation does not alter reading anchors');
    button = cards(env).flatMap(actions).find(node => node.dataset.readerId === 'plato-republic'); button.focus(); await env.click(button); assert.equal(env.run('state.pages[state.page].start'), offset); assert.equal(env.get('reading-scroll').scrollTop, 170); assert.equal(env.values.get('mythic:bookmark:v2:plato-republic'), saved); await env.click(env.get('back')); assert.equal(env.document.activeElement, button);
  });
  await check('overlapping collection opens share one request and late completion never overrides a newer shelf choice', async () => {
    let release; const pending = new Promise(resolve => release = resolve), delayed = harness({collectionFetch: () => pending}); await delayed.settle();
    const first = delayed.get('view-collected').click(); await delayed.settle(); assert.match(delayed.get('collection-load-status').textContent, /Loading/); assert.equal(delayed.get('collection-retry').hidden, true);
    const repeated = delayed.get('view-collected').click(); await delayed.settle(); assert.equal(delayed.calls.filter(url => url === 'collections.json').length, 1);
    await delayed.click(delayed.get('view-reading')); release({ok: true, json: async () => clone(inventory)}); await Promise.all([...first, ...repeated]); await delayed.settle();
    assert.equal(delayed.get('reading-shelf-panel').hidden, false); assert.equal(delayed.get('collected-panel').hidden, true); assert.equal(delayed.get('view-reading').getAttribute('aria-pressed'), 'true'); assert.equal(delayed.get('skip-library').href, '#shelves');
    await delayed.click(delayed.get('view-collected')); assert.equal(cards(delayed).length, inventory.entries.length); assert.equal(delayed.calls.filter(url => url === 'collections.json').length, 1);
  });
  await check('a collected read attempted during slow reader startup gives feedback and opens after startup', async () => {
    let release; const pending = new Promise(resolve => release = resolve);
    const starting = harness({catalogFetch: async count => count === 1 ? pending : {ok: true, json: async () => clone(catalog)}});
    await openCollection(starting); const button = cards(starting).flatMap(actions).find(node => node.dataset.readerId === 'plato-apology'); assert(button); button.focus();
    await starting.click(button); assert.equal(starting.run('state.active'), null); assert.equal(starting.get('reader').hidden, true);
    assert.match(starting.get('collection-load-status').textContent, /loading.*try.*ready/i, 'An early read must give explicit retry feedback');
    release({ok: true, json: async () => clone(catalog)}); await starting.settle(); assert.equal(starting.document.activeElement, button);
    await starting.click(button); assert.equal(starting.run('state.active.id'), 'plato-apology'); assert.equal(starting.run('state.ready'), true); assert.equal(starting.get('reader').hidden, false);
    await starting.click(starting.get('back')); assert.equal(starting.get('collected-panel').hidden, false); assert.equal(starting.document.activeElement, button); assert.equal(starting.timers.size, 0);
  });
  await check('a failed original reader startup keeps inventory visible and explains why reading is unavailable', async () => {
    const unavailable = harness({catalogFetch: async count => count === 1 ? {ok: false} : {ok: true, json: async () => clone(catalog)}});
    await openCollection(unavailable); assert.equal(cards(unavailable).length, inventory.entries.length);
    await unavailable.click(cards(unavailable).flatMap(actions)[0]); assert.match(unavailable.get('collection-load-status').textContent, /reading shelf is unavailable.*reload/i);
    assert.equal(unavailable.run('state.active'), null); assert.equal(unavailable.get('reader').hidden, true); assert.equal(unavailable.timers.size, 0);
  });
  await check('HTTP, network and JSON failures show a clear retry while retaining the reading shelf', async () => {
    const failures = [() => ({ok: false}), () => {throw Error('network unavailable');}, () => ({ok: true, json: async () => {throw Error('invalid JSON');}})];
    for (const [index, fail] of failures.entries()) {
      const failed = harness({collectionFetch: async count => count === 1 ? fail() : {ok: true, json: async () => clone(inventory)}}); await openCollection(failed); assertFailure(failed, 'fetch failure ' + index); await failed.click(failed.get('view-reading')); assert.equal(failed.get('reading-shelf-panel').hidden, false); await failed.click(failed.get('view-collected')); assert.deepEqual(seen(failed), inventory.entries.map(entry => entry.id)); assert.equal(failed.get('collection-retry').hidden, true);
    }
    const catalogFailure = harness({catalogFetch: async count => count === 2 ? {ok: false} : {ok: true, json: async () => clone(catalog)}}); await openCollection(catalogFailure); assertFailure(catalogFailure, 'reader catalog cross-check failure'); await catalogFailure.click(catalogFailure.get('collection-retry')); assert.equal(cards(catalogFailure).length, inventory.entries.length);
  });
  await check('invalid/unknown status, duplicate IDs, invalid/missing reader IDs and dishonest totals fail closed and retry cleanly', async () => {
    const scenarios = [
      ['unknown source state', data => data.entries.find(entry => entry.status !== 'readable').status = 'unknown'],
      ['duplicate inventory ID', data => data.entries[1].id = data.entries[0].id],
      ['nonexistent reader ID', data => data.entries.find(entry => entry.status === 'readable').reader_id = 'not-an-existing-edition'],
      ['duplicate reader ID', data => {const entries = data.entries.filter(entry => entry.status === 'readable'); entries[1].reader_id = entries[0].reader_id;}],
      ['missing reader ID', data => data.entries.find(entry => entry.status === 'readable').reader_id = null],
      ['unreviewed source action', data => data.entries.find(entry => entry.status === 'needs-source-review').reader_id = catalog[0].id],
      ['quarantined source action', data => data.entries.find(entry => entry.status === 'quarantined').reader_id = catalog[0].id],
      ['missing source action', data => data.entries.find(entry => entry.status === 'missing').reader_id = catalog[0].id],
      ['dishonest total', data => data.summary.entries++],
      ['dishonest readable total', data => data.summary.readable_editions++],
      ['missing existing edition', data => {data.entries = data.entries.filter(entry => entry.reader_id !== catalog[0].id); data.summary.entries--; data.summary.readable_editions--;}],
      ['invalid aliases', data => data.entries[0].aliases = [null]],
      ['unsupported schema', data => data.schema_version = 99]
    ];
    for (const [label, mutation] of scenarios) await badThenRetry(label, mutation);
  });
  await check('all display metadata is text-only and unsafe/local source URLs do not become links', async () => {
    const injected = clone(inventory), nonreadable = injected.entries.filter(entry => entry.status !== 'readable');
    const unsafe = ['javascript:alert(1)', 'data:text/html,<script>alert(1)</script>', 'http://example.com/source', '//example.com/source', '../private-source.txt', '/home/agent/secret.txt', 'https://user:secret@example.com/source', 'https://localhost/source', 'https://127.0.0.1/source', 'https://[::1]/source'];
    unsafe.forEach((url, index) => nonreadable[index].source_url = url);
    const fixture = nonreadable[0], payload = '<img src=x onerror="globalThis.injected=true"><script>globalThis.injected=true</script>';
    fixture.title = payload; fixture.author = payload; fixture.edition = payload; fixture.source_note = payload; fixture.aliases = [payload]; fixture.original_catalog_title = payload + ' catalog';
    const safe = harness({inventory: injected}); await openCollection(safe); assert.equal(cards(safe).length, inventory.entries.length);
    for (let index = 0; index < unsafe.length; index++) assert.equal(links(cards(safe).find(card => card.dataset.entryId === nonreadable[index].id)).length, 0, unsafe[index]);
    const card = cards(safe).find(card => card.dataset.entryId === fixture.id); assert(card.textContent.includes(payload)); assert.equal(descendants(card).filter(node => ['IMG', 'SCRIPT', 'IFRAME'].includes(node.tagName)).length, 0); assert.equal(safe.run('globalThis.injected'), undefined);
  });
  await check('private workspace/file locations are rejected before any inventory metadata is displayed', async () => {
    for (const value of ['/workspace/private/source.txt', '/tmp/private/source.txt', 'file:///home/agent/source.txt', 'source-audit/private.json', 'C:\\Users\\reader\\private.txt']) await badThenRetry('private location ' + value, data => data.entries[0].source_note = value);
  });
  await check('read actions use the verified reader_id even when an inventory ID differs', async () => {
    const mapped = clone(inventory), entry = mapped.entries.find(entry => entry.reader_id === 'plato-apology'); entry.id = 'collected-alias-that-is-not-a-reader-id';
    const mappedEnv = harness({inventory: mapped}); await openCollection(mappedEnv); const button = actions(cards(mappedEnv).find(card => card.dataset.entryId === entry.id))[0]; button.focus(); await mappedEnv.click(button); assert.equal(mappedEnv.run('state.active.id'), 'plato-apology'); assert.equal(mappedEnv.run('state.ready'), true); await mappedEnv.click(mappedEnv.get('back')); assert.equal(mappedEnv.document.activeElement, button);
  });
  const mainScenarioCount = assertions.length;
  assert.equal(mainScenarioCount, 16, 'All original main-register scenario groups remain present');
  await check('register selector starts on main and secondary metadata is fetched only after explicit selection', async () => {
    const selected = harness(); await selected.settle();
    const selector = selected.get('collection-register-filter');
    assert.equal(selector.tagName, 'SELECT'); assert.equal(selector.disabled, false);
    assert(selected.document.querySelector('label[for="collection-register-filter"]'));
    assert.deepEqual(selector.options.map(option => option.value), ['main', 'esoterica']);
    assert.equal(selector.value, 'main');
    assert.equal(requestCount(selected, 'collections.json'), 0);
    assert.equal(requestCount(selected, 'esoterica-register.json'), 0);
    await openCollection(selected); assertMain(selected);
    assert.equal(requestCount(selected, 'esoterica-register.json'), 0);
    selector.focus(); await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
    assert.equal(selected.document.activeElement, selector, 'Native select retains focus after register change');
    assert.equal(requestCount(selected, 'collections.json'), 1);
    assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
    assert(!selected.calls.some(url => url.startsWith('books/')), 'Selecting either register never fetches a reading file');
    assert.deepEqual([...selected.values.keys()].filter(key => key.includes('bookmark:') || key.endsWith(':last')), []);
  });
  await check('secondary counts stay scoped to 37 slots with three actual Plato overlaps and 34 non-readable missing cards', async () => {
    const selected = harness(); await openEsoterica(selected);
    assert.equal(inventory.entries.length, 135); assert.equal(catalog.length, counts.readable);
    assert.equal(esoterica.entries.length, 37);
    assert.deepEqual(esoterica.summary, {registered_file_slots: 37, overlapping_readable_editions: 3, not_recovered_file_slots: 34});
    assert.equal(new Set(esoterica.entries.map(entry => entry.register_id)).size, 37);
    assert.deepEqual(esoterica.entries.filter(entry => entry.status === 'readable').map(entry => entry.reader_id).sort(), overlapReaderIds);
    assert.equal(esoterica.entries.filter(entry => entry.status === 'missing').length, 34);
    assertEsoterica(selected);
    assert.match(selected.get('collection-scope').textContent, /separate historical shelf register.*file slot rather than unique work/i);
    assert.match(selected.get('collection-scope-note').textContent, /not fresh completeness or rights verification/i);
    assert.match(selected.get('collection-scope-note').textContent, /never added to the main collection total/i);
    for (const entry of esoterica.entries) {
      const card = cards(selected).find(node => node.dataset.entryId === entry.id); assert(card);
      assert.equal(card.querySelector('h3').textContent, entry.title);
      assert.equal(card.querySelector('.collection-source-note').textContent, entry.source_note);
      assert.equal(card.dataset.status, entry.status);
      assert.equal(card.querySelector('.collection-badge').textContent, entry.status === 'readable' ? 'Already-readable edition' : 'File not recovered');
      if (entry.status === 'readable') {
        assert.equal(entry.overlaps_main_catalog, true); assert.equal(entry.overlap_reader_id, entry.reader_id);
        assert.equal(actions(card).length, 1); assert.equal(actions(card)[0].dataset.readerId, entry.reader_id);
        assert.match(actions(card)[0].textContent, /existing reading edition/i);
        assert(inventory.entries.some(main => main.reader_id === entry.reader_id && main.status === 'readable'));
      } else {
        assert.equal(entry.reader_id, null); assert.equal(entry.overlap_reader_id, null); assert.equal(entry.overlaps_main_catalog, false);
        assert.equal(actions(card).length, 0); assert.equal(descendants(card).filter(node => node.tagName === 'BUTTON').length, 0);
        assert(!links(card).some(link => /#book=|books\//.test(link.href)), 'Missing slots must not create reading links');
      }
    }
    assert.deepEqual(cards(selected).flatMap(actions).map(button => button.dataset.readerId).sort(), overlapReaderIds);
    assert.equal(selected.get('edition-count').textContent, `${catalog.length} reading editions`);
    await selected.change('collection-register-filter', 'main'); assertMain(selected);
    assert(!selected.get('collection-summary').textContent.includes(`${inventory.entries.length + esoterica.entries.length} catalog entries`), 'Separate register slots are never added to main entries');
    assert(!selected.get('collection-summary').textContent.includes(`${catalog.length + overlapReaderIds.length} reading editions`), 'Overlapping readers are never counted twice');
  });
  await check('secondary search and filters are intersections, register changes reset them, and view toggles retain them', async () => {
    const selected = harness(); await openCollection(selected);
    await selected.change('collection-search', 'Plato', 'input'); await selected.change('collection-status-filter', 'readable'); await selected.change('collection-tradition-filter', 'philosophy');
    await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
    for (const [id, value] of [['collection-search', ''], ['collection-status-filter', 'all'], ['collection-tradition-filter', 'all']]) assert.equal(selected.get(id).value, value, id + ' resets on register change');
    assert.deepEqual(selected.get('collection-tradition-filter').options.map(option => option.value), ['all', ...new Set(esoterica.entries.map(entry => entry.tradition).sort((a, b) => a.localeCompare(b)))]);
    const alias = esoterica.entries.find(entry => entry.status === 'missing').aliases[0];
    for (const query of ['  PLATO   REPUBLIC ', 'Egypt', 'Underhill', alias, 'never-an-esoterica-title-7813']) {
      await selected.change('collection-search', query, 'input');
      const terms = normalize(query).trim().split(/\s+/).filter(Boolean);
      const expected = esoterica.entries.filter(entry => {const text = normalize([entry.title, entry.original_catalog_title, entry.author, entry.edition, entry.tradition, ...entry.aliases].filter(Boolean).join(' ')); return terms.every(term => text.includes(term));});
      if (!query.startsWith('never-')) assert(expected.length > 0, 'Positive secondary fixture: ' + query);
      assert.deepEqual(seen(selected), expected.map(entry => entry.id));
      assert.equal(selected.get('collection-load-status').textContent, `Showing ${expected.length} of 37 registered file slots.`);
      assert.equal(selected.get('collection-summary').textContent, secondarySummary, 'Filtering does not change scoped totals');
    }
    assert.match(selected.get('collection-results').textContent, /No entries match/);
    await selected.change('collection-search', '', 'input');
    for (const status of Object.keys(counts)) {
      await selected.change('collection-status-filter', status);
      assert.deepEqual(seen(selected), esoterica.entries.filter(entry => entry.status === status).map(entry => entry.id));
      if (status !== 'readable') assert.equal(cards(selected).flatMap(actions).length, 0);
    }
    const target = esoterica.entries.find(entry => entry.status === 'missing');
    await selected.change('collection-search', target.aliases[0], 'input'); await selected.change('collection-status-filter', 'missing'); await selected.change('collection-tradition-filter', target.tradition);
    const before = seen(selected), requests = [...selected.calls]; assert(before.includes(target.id));
    await selected.click(selected.get('view-reading')); await selected.click(selected.get('view-collected'));
    assert.deepEqual(seen(selected), before); assert.deepEqual(selected.calls, requests);
    assert.equal(selected.get('collection-register-filter').value, 'esoterica'); assert.equal(selected.get('collection-search').value, target.aliases[0]); assert.equal(selected.get('collection-status-filter').value, 'missing'); assert.equal(selected.get('collection-tradition-filter').value, target.tradition);
    await selected.change('collection-register-filter', 'main'); assertMain(selected);
    for (const [id, value] of [['collection-search', ''], ['collection-status-filter', 'all'], ['collection-tradition-filter', 'all']]) assert.equal(selected.get(id).value, value);
    assert.deepEqual(selected.get('collection-tradition-filter').options.map(option => option.value), ['all', ...new Set(inventory.entries.map(entry => entry.tradition).sort((a, b) => a.localeCompare(b)))]);
    await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
    assert.equal(requestCount(selected, 'collections.json'), 1); assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
  });
  await check('successful register caches stay independent across repeated switches without reading or bookmark side effects', async () => {
    const selected = harness(); await openEsoterica(selected); const requests = [...selected.calls], stored = [...selected.values];
    for (let index = 0; index < 4; index++) {
      await selected.change('collection-register-filter', 'main'); assertMain(selected);
      await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
      await selected.click(selected.get('view-reading')); await selected.click(selected.get('view-collected')); assertEsoterica(selected);
    }
    assert.deepEqual(selected.calls, requests); assert.deepEqual([...selected.values], stored);
    assert.equal(requestCount(selected, 'collections.json'), 1); assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
    assert.equal(requestCount(selected, 'catalog.json'), 3, 'Startup and one independent catalog verification per register');
  });
  await check('all secondary read actions open the existing Plato editions and share exact bookmarks with main', async () => {
    const selected = harness(); await openEsoterica(selected);
    for (const entry of esoterica.entries.filter(entry => entry.status === 'readable')) {
      let button = cards(selected).flatMap(actions).find(node => node.dataset.readerId === entry.reader_id); button.focus(); await selected.click(button);
      assert.equal(selected.run('state.active.id'), entry.reader_id); assert.equal(selected.run('state.ready'), true); assert.equal(selected.get('reader').hidden, false);
      selected.run('turnPage(1)'); const offset = selected.run('state.pages[state.page].start'); selected.get('reading-scroll').scrollTop = 170; selected.run('savePosition()');
      const key = 'mythic:bookmark:v2:' + entry.reader_id, saved = selected.values.get(key); assert(saved);
      await selected.click(selected.get('back')); assert.equal(selected.document.activeElement, button); assert.equal(selected.get('collection-register-filter').value, 'esoterica');
      await selected.change('collection-register-filter', 'main'); assert.equal(selected.values.get(key), saved);
      button = cards(selected).flatMap(actions).find(node => node.dataset.readerId === entry.reader_id); button.focus(); await selected.click(button);
      assert.equal(selected.run('state.active.id'), entry.reader_id); assert.equal(selected.run('state.pages[state.page].start'), offset); assert.equal(selected.get('reading-scroll').scrollTop, 170); assert.equal(selected.values.get(key), saved);
      await selected.click(selected.get('back')); assert.equal(selected.document.activeElement, button);
      await selected.change('collection-register-filter', 'esoterica'); assert.equal(selected.values.get(key), saved);
    }
    const fetchedBooks = [...new Set(selected.calls.filter(url => url.startsWith('books/')))];
    assert.deepEqual(fetchedBooks.sort(), catalog.filter(book => overlapReaderIds.includes(book.id)).map(book => book.path).sort());
    assert(![...selected.values.keys()].some(key => /bookmark:.*esoterica:/.test(key)), 'Register slots never create separate bookmark identities');
    assertEsoterica(selected);
  });
  await check('slow secondary responses never overwrite a newer main selection, and in-flight reselection deduplicates', async () => {
    for (const returnToSecondary of [false, true]) {
      let release; const pending = new Promise(resolve => release = resolve), selected = harness({esotericaFetch: () => pending}); await openCollection(selected);
      const first = beginChange(selected, 'collection-register-filter', 'esoterica'); await selected.settle();
      assert.match(selected.get('collection-load-status').textContent, /Loading the esoterica register/); assert.equal(selected.get('collection-summary').textContent, ''); assert.equal(cards(selected).length, 0);
      await selected.change('collection-register-filter', 'main'); assertMain(selected);
      let repeated = [];
      if (returnToSecondary) {repeated = beginChange(selected, 'collection-register-filter', 'esoterica'); await selected.settle();}
      assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
      release(response(esoterica)); await Promise.all([...first, ...repeated]); await selected.settle();
      if (returnToSecondary) assertEsoterica(selected); else assertMain(selected);
      await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
      assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
    }
  });
  await check('a slow main response never overwrites the selected secondary register and is cached independently', async () => {
    let release; const pending = new Promise(resolve => release = resolve), selected = harness({collectionFetch: () => pending}); await selected.settle();
    const first = selected.get('view-collected').click(); await selected.settle();
    await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
    release(response(inventory)); await Promise.all(first); await selected.settle(); assertEsoterica(selected);
    assert.match(selected.get('collection-scope').textContent, /separate historical shelf register/i);
    await selected.change('collection-register-filter', 'main'); assertMain(selected);
    assert.equal(requestCount(selected, 'collections.json'), 1); assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
  });
  await check('late secondary success does not reopen collected works after choosing the reading shelf', async () => {
    let release; const pending = new Promise(resolve => release = resolve), selected = harness({esotericaFetch: () => pending}); await openCollection(selected);
    const first = beginChange(selected, 'collection-register-filter', 'esoterica'); await selected.settle();
    await selected.click(selected.get('view-reading')); release(response(esoterica)); await Promise.all(first); await selected.settle();
    assert.equal(selected.get('reading-shelf-panel').hidden, false); assert.equal(selected.get('collected-panel').hidden, true); assert.equal(selected.get('view-reading').getAttribute('aria-pressed'), 'true'); assert.equal(selected.get('skip-library').href, '#shelves');
    await selected.click(selected.get('view-collected')); assertEsoterica(selected); assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
  });
  await check('secondary HTTP, network, JSON and catalog-check failures retry without invalidating main', async () => {
    const failures = [() => ({ok: false}), () => {throw Error('secondary network unavailable');}, () => ({ok: true, json: async () => {throw Error('invalid secondary JSON');}})];
    for (const [index, fail] of failures.entries()) {
      const selected = harness({esotericaFetch: async count => count === 1 ? fail() : response(esoterica)});
      await openEsoterica(selected); assertFailure(selected, 'secondary fetch failure ' + index); assert.match(selected.get('collection-load-status').textContent, /esoterica register/i);
      await selected.change('collection-register-filter', 'main'); assertMain(selected); assert.equal(requestCount(selected, 'collections.json'), 1);
      await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected); assert.equal(requestCount(selected, 'esoterica-register.json'), 2);
    }
    const selected = harness({catalogFetch: async count => count === 3 ? {ok: false} : response(catalog)});
    await openEsoterica(selected); assertFailure(selected, 'secondary catalog cross-check failure');
    await selected.click(selected.get('collection-retry')); assertEsoterica(selected);
    await selected.change('collection-register-filter', 'main'); assertMain(selected); assert.equal(requestCount(selected, 'collections.json'), 1);
  });
  await check('main failure and retry do not invalidate a healthy secondary register', async () => {
    const selected = harness({collectionFetch: async count => count === 1 ? {ok: false} : response(inventory)});
    await openCollection(selected); assertFailure(selected, 'main failure with independent secondary');
    await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
    await selected.change('collection-register-filter', 'main'); assertMain(selected);
    await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);
    assert.equal(requestCount(selected, 'collections.json'), 2); assert.equal(requestCount(selected, 'esoterica-register.json'), 1);
  });
  await check('inactive late failures cannot replace a healthy register or expose its retry control', async () => {
    for (const failedRegister of ['main', 'esoterica']) {
      let reject; const pending = new Promise((resolve, fail) => reject = fail);
      const selected = harness(failedRegister === 'main' ? {collectionFetch: count => count === 1 ? pending : response(inventory)} : {esotericaFetch: count => count === 1 ? pending : response(esoterica)});
      await selected.settle(); let first;
      if (failedRegister === 'main') {first = selected.get('view-collected').click(); await selected.settle(); await selected.change('collection-register-filter', 'esoterica'); assertEsoterica(selected);}
      else {await openCollection(selected); first = beginChange(selected, 'collection-register-filter', 'esoterica'); await selected.settle(); await selected.change('collection-register-filter', 'main'); assertMain(selected);}
      const before = [selected.get('collection-summary').textContent, selected.get('collection-load-status').textContent, selected.get('collection-scope').textContent];
      reject(Error('late inactive register failure')); await Promise.all(first); await selected.settle();
      assert.deepEqual([selected.get('collection-summary').textContent, selected.get('collection-load-status').textContent, selected.get('collection-scope').textContent], before);
      assert.equal(selected.get('collection-retry').hidden, true);
      await selected.change('collection-register-filter', failedRegister);
      if (failedRegister === 'main') assertMain(selected); else assertEsoterica(selected);
      assert.equal(requestCount(selected, failedRegister === 'main' ? 'collections.json' : 'esoterica-register.json'), 2);
    }
  });
  await check('secondary malformed entries, dishonest scoped totals and unconfirmed overlaps fail closed and retry', async () => {
    const scenarios = [
      ['unsupported secondary schema', data => data.schema_version = 99],
      ['duplicate secondary ID', data => data.entries[1].id = data.entries[0].id],
      ['missing register slot', data => delete data.entries[0].register_id],
      ['duplicate register slot', data => data.entries[1].register_id = data.entries[0].register_id],
      ['invalid aliases', data => data.entries[0].aliases = [null]],
      ['unknown status', data => data.entries[0].status = 'unknown'],
      ['unsupported source-review status', data => data.entries[0].status = 'needs-source-review'],
      ['unsupported quarantine status', data => data.entries[0].status = 'quarantined'],
      ['nonexistent overlap reader', data => {const entry = data.entries.find(entry => entry.status === 'readable'); entry.reader_id = entry.overlap_reader_id = 'not-a-reading-edition';}],
      ['duplicate overlap reader', data => {const readable = data.entries.filter(entry => entry.status === 'readable'); readable[1].reader_id = readable[1].overlap_reader_id = readable[0].reader_id;}],
      ['missing overlap reader', data => data.entries.find(entry => entry.status === 'readable').reader_id = null],
      ['missing file gets a read action', data => data.entries.find(entry => entry.status === 'missing').reader_id = 'plato-republic'],
      ['readable overlap flag false', data => data.entries.find(entry => entry.status === 'readable').overlaps_main_catalog = false],
      ['readable overlap ID mismatch', data => data.entries.find(entry => entry.status === 'readable').overlap_reader_id = 'plato-apology'],
      ['missing overlap flag true', data => data.entries.find(entry => entry.status === 'missing').overlaps_main_catalog = true],
      ['missing overlap ID assigned', data => data.entries.find(entry => entry.status === 'missing').overlap_reader_id = 'plato-republic'],
      ['dishonest slot total', data => data.summary.registered_file_slots++],
      ['dishonest overlap total', data => data.summary.overlapping_readable_editions++],
      ['dishonest missing total', data => data.summary.not_recovered_file_slots++],
      ['main summary substituted for secondary', data => data.summary = clone(inventory.summary)],
      ['private metadata location', data => data.entries[0].source_note = '/workspace/private/esoterica.txt']
    ];
    for (const [label, mutation] of scenarios) await badSecondaryThenRetry(label, mutation);
  });
  await check('secondary display metadata remains text-only and unsafe source URLs cannot become links', async () => {
    const injected = clone(esoterica), missing = injected.entries.filter(entry => entry.status === 'missing');
    const unsafe = ['javascript:alert(1)', 'data:text/html,<script>alert(1)</script>', 'http://example.com/source', '//example.com/source', '../private-source.txt', 'https://user:secret@example.com/source', 'https://localhost/source', 'https://127.0.0.1/source', 'https://[::1]/source'];
    unsafe.forEach((url, index) => missing[index].source_url = url);
    const payload = '<img src=x onerror="globalThis.secondaryInjected=true"><script>globalThis.secondaryInjected=true</script>';
    missing[0].title = payload; missing[0].author = payload; missing[0].edition = payload; missing[0].source_note = payload; missing[0].aliases = [payload];
    const selected = harness({esotericaInventory: injected}); await openEsoterica(selected);
    assert.equal(cards(selected).length, 37);
    for (const [index, url] of unsafe.entries()) assert.equal(links(cards(selected).find(card => card.dataset.entryId === missing[index].id)).length, 0, url);
    const card = cards(selected).find(card => card.dataset.entryId === missing[0].id); assert(card.textContent.includes(payload)); assert.equal(descendants(card).filter(node => ['IMG', 'SCRIPT', 'IFRAME'].includes(node.tagName)).length, 0); assert.equal(selected.run('globalThis.secondaryInjected'), undefined);
    assert.equal(actions(card).length, 0);
  });
  const registerScenarioCount = assertions.length - mainScenarioCount;
  assert.equal(registerScenarioCount, 13, 'All secondary-register behavior groups remain present');
  await check('current readers, manifests and declared sources agree; explicit baseline preserves prior reader prefixes and source pins', async () => {
    const sections = JSON.parse(fs.readFileSync(path.join(root, 'sections.json'), 'utf8'));
    const specs = JSON.parse(fs.readFileSync(path.join(root, '../scripts/edition_specs.json'), 'utf8'));
    const readerIds = catalog.map(book => book.id), declaredBooks = new Set();
    assert.equal(new Set(readerIds).size, readerIds.length, 'Reader IDs remain unique');
    assert.deepEqual(Object.keys(sections.books).sort(), [...readerIds].sort(), 'Every reader has exactly one section manifest');
    assert.deepEqual(Object.keys(specs.editions).sort(), [...readerIds].sort(), 'Every reader has exactly one source specification');
    const checkSource = (relativePath, expected, label) => {
      assert.equal(typeof relativePath, 'string', label + ': source path required');
      assert(relativePath.startsWith('books/') && path.posix.normalize(relativePath) === relativePath && !relativePath.includes('\\'), label + ': safe relative books path');
      assert(Number.isInteger(expected.bytes) && expected.bytes > 0, label + ': positive source byte pin');
      assert.match(expected.sha256, /^[a-f0-9]{64}$/, label + ': SHA-256 pin');
      const bytes = fs.readFileSync(path.join(root, relativePath));
      assert.equal(bytes.length, expected.bytes, label + ': source byte length');
      assert.equal(createHash('sha256').update(bytes).digest('hex'), expected.sha256, label + ': source SHA-256');
      declaredBooks.add('dist/' + relativePath);
    };
    for (const book of catalog) {
      const manifest = sections.books[book.id], spec = specs.editions[book.id];
      checkSource(book.path, book, book.id);
      assert.equal(manifest.path, book.path, book.id + ': manifest path');
      assert.equal(manifest.source, book.path, book.id + ': manifest source');
      assert.equal(manifest.sha256, book.sha256, book.id + ': manifest SHA-256');
      assert.equal(manifest.sourceBytes, book.bytes, book.id + ': manifest source bytes');
      assert.equal(spec.sha256, book.sha256, book.id + ': source specification SHA-256');
      for (const [catalogKey, specKey] of [['preservation_archive', 'preservationArchive'], ['source_scan', 'sourceScan']]) {
        if (!book[catalogKey]) continue;
        assert.deepEqual(spec[specKey], book[catalogKey], book.id + ': ' + catalogKey + ' metadata');
        checkSource(book[catalogKey].path, book[catalogKey], book.id + ': ' + catalogKey);
      }
      if (book.notices) {
        assert.equal(manifest.originalSource?.path, book.notices, book.id + ': original notice source');
        assert.equal(manifest.originalSource.sha256, spec.originalSourceSha256, book.id + ': original notice SHA-256');
        checkSource(book.notices, {bytes: manifest.originalSource.sourceBytes, sha256: manifest.originalSource.sha256}, book.id + ': original notices');
      }
    }
    const walk = directory => fs.readdirSync(directory, {withFileTypes: true}).flatMap(item => item.isDirectory() ? walk(path.join(directory, item.name)) : [path.join(directory, item.name)]);
    const actualBooks = walk(path.join(root, 'books')).map(file => path.relative(path.join(root, '..'), file)).sort();
    assert.deepEqual(actualBooks, [...declaredBooks].sort(), 'Every reading asset is declared; none is missing or orphaned');
    sourceIntegrity.assets = declaredBooks.size;
    if (baseline) {
      assert.equal(baseline.schema_version, 1, 'Supported explicit baseline schema');
      assert(Array.isArray(baseline.catalog) && baseline.catalog.length > 0, 'Explicit baseline has prior readers');
      const priorIds = baseline.catalog.map(book => book.id);
      assert.equal(new Set(priorIds).size, priorIds.length, 'Explicit baseline reader IDs are unique');
      assert.deepEqual(catalog.slice(0, priorIds.length), baseline.catalog, 'Prior catalog metadata/order remain an exact prefix');
      const envelope = (data, key) => Object.fromEntries(Object.entries(data).filter(([name]) => name !== key));
      assert.deepEqual(envelope(sections, 'books'), envelope(baseline.sections, 'books'), 'Prior manifest envelope preserved');
      assert.deepEqual(envelope(specs, 'editions'), envelope(baseline.specs, 'editions'), 'Prior source-specification envelope preserved');
      for (const id of priorIds) {
        assert.deepEqual(sections.books[id], baseline.sections.books[id], id + ': prior sections and bookmark anchors preserved');
        assert.deepEqual(specs.editions[id], baseline.specs.editions[id], id + ': prior source specification preserved');
      }
      const priorSourcePaths = Object.keys(baseline.files).filter(file => file.startsWith('dist/books/'));
      assert(priorSourcePaths.length >= priorIds.length, 'Explicit baseline includes prior source-file pins');
      for (const book of baseline.catalog) {
        for (const sourcePath of [book.path, book.notices, book.preservation_archive?.path, book.source_scan?.path].filter(Boolean)) {
          assert(Object.hasOwn(baseline.files, 'dist/' + sourcePath), book.id + ': explicit baseline pins ' + sourcePath);
        }
      }
      for (const file of priorSourcePaths) {
        assert(declaredBooks.has(file), file + ': prior source is still declared');
        checkSource(file.slice('dist/'.length), baseline.files[file], file + ': preserved baseline source');
      }
      sourceIntegrity.priorReaders = priorIds.length;
      sourceIntegrity.priorSourceFiles = priorSourcePaths.length;
    }
  });
  assert.equal(assertions.length, 30, 'All 30 scenario groups remain present');
  const preservationReport = baseline
    ? `${sourceIntegrity.priorReaders} prior readers and ${sourceIntegrity.priorSourceFiles} prior source files preserved against the explicit baseline`
    : 'no historical baseline requested (historical preservation was not claimed)';
  console.log(`PASS: ${assertions.length} collected-view scenario groups (${mainScenarioCount} main behavior + ${registerScenarioCount} register behavior + 1 source integrity); ${inventory.entries.length} main catalog entries; ${esoterica.entries.length} separately scoped slots; ${counts.readable} current readers with ${overlapReaderIds.length} secondary overlaps; ${sourceIntegrity.assets} verified declared source files; ${preservationReport}. Admission, exact main promotions and unchanged UI require the separate edition pipeline gate. DOM behavior simulation only. Native keyboard activation, browser layout, mobile/touch, screen readers, and deployment were not verified.`);
})().catch(error => {console.error(error); process.exitCode = 1;});
