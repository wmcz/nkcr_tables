/**
 * NKČR → Wikidata: pair or create items straight from the
 * "Wikidata:WikiProject Czech Republic/New authorities" tables, one wbeditentity edit per row.
 *
 * Install: put this file on User:<name>/nkcr-parovani.js and add to User:<name>/common.js:
 *   mw.loader.load('/w/index.php?title=User:<name>/nkcr-parovani.js&action=raw&ctype=text/javascript');
 */
(function () {
	'use strict';

	var PAGE_PREFIX = 'Wikidata:WikiProject_Czech_Republic/New_authorities/';
	var STORE_PREFIX = 'nkcr-parovani:';
	var GREGORIAN = 'http://www.wikidata.org/entity/Q1985727';

	// Anything outside the whitelist rejects the row – the page is publicly editable.
	var TERM_KEYS = /^(L|D|A)(cs|mul|en|de)$/;
	var CLAIM_TYPES = { P31: 'item', P21: 'item', P691: 'string', P569: 'time', P570: 'time' };
	var QUAL_TYPES = { P1810: 'string' };
	var REF_TYPES = { S248: 'item', S691: 'string', S813: 'time' };
	var AUT_RE = /^[a-z]{2,5}\d{4,13}$/;
	var ALLOWED_VALUES = { P31: ['Q5'], P21: ['Q6581097', 'Q6581072'], S248: ['Q13550863'] };
	// template, category, disambiguation, list, module, project page…
	var SKIP_P31 = ['Q11266439', 'Q4167836', 'Q4167410', 'Q13406463', 'Q15184295', 'Q14204246', 'Q17362920', 'Q11753321'];

	// Pure functions below are also loaded by the Node tests.

	function extractV1(href) {
		var m = /^https:\/\/(?:tools\.wmflabs\.org\/quickstatements\/#\/?|quickstatements\.toolforge\.org\/#\/?|qs-dev\.toolforge\.org\/batch\/new\/\?)v1=(.*)$/.exec(href || '');
		if (!m) return null;
		try {
			return decodeURIComponent(m[1]);
		} catch (e) {
			return null;
		}
	}

	function splitV1(raw) {
		var lines = [], fields = [], cur = '', inQuote = false, i, ch;
		raw = raw.replace(/\r?\n/g, '||');
		for (i = 0; i < raw.length; i++) {
			ch = raw[i];
			if (ch === '"') {
				inQuote = !inQuote;
				cur += ch;
			} else if (ch === '|' && !inQuote) {
				if (raw[i + 1] === '|') {
					fields.push(cur);
					lines.push(fields);
					fields = [];
					cur = '';
					i++;
				} else {
					fields.push(cur);
					cur = '';
				}
			} else {
				cur += ch;
			}
		}
		if (cur !== '' || fields.length) {
			fields.push(cur);
			lines.push(fields);
		}
		return lines.filter(function (f) { return !(f.length === 1 && f[0].trim() === ''); })
			.map(function (f) { return f.map(function (x) { return x.trim(); }); });
	}

	function unquote(v) {
		if (v.length >= 2 && v[0] === '"' && v[v.length - 1] === '"') return v.slice(1, -1);
		return null;
	}

	function checkAllowed(key, v) {
		if (ALLOWED_VALUES[key] && ALLOWED_VALUES[key].indexOf(v) === -1) throw new Error('nepovolená hodnota ' + key + ' = ' + v);
		if ((key === 'P691' || key === 'S691') && !AUT_RE.test(unquote(v) || '')) throw new Error('divné NKČR ID: ' + v);
	}

	function parseValue(type, v) {
		if (type === 'string') {
			var s = unquote(v);
			if (s === null || s === '') throw new Error('očekáván řetězec v uvozovkách: ' + v);
			return { type: 'string', value: s };
		}
		if (type === 'item') {
			if (!/^Q\d+$/.test(v)) throw new Error('očekáváno Q-ID: ' + v);
			return { type: 'wikibase-entityid', value: { 'entity-type': 'item', 'numeric-id': parseInt(v.slice(1), 10), id: v } };
		}
		if (type === 'time') {
			var m = /^([+-]\d{4,}-\d{2}-\d{2}T00:00:00Z)\/(9|10|11)$/.exec(v);
			if (!m) throw new Error('neznámý formát data: ' + v);
			return {
				type: 'time',
				value: { time: m[1], timezone: 0, before: 0, after: 0, precision: parseInt(m[2], 10), calendarmodel: GREGORIAN }
			};
		}
		throw new Error('neznámý typ ' + type);
	}

	function snak(prop, dv) {
		return { snaktype: 'value', property: prop, datavalue: dv };
	}

	function parseCommands(raw) {
		var lines = splitV1(raw);
		var model = { target: null, labels: {}, descriptions: {}, aliases: {}, claims: [], aut: null, name: null, birthYear: null, deathYear: null, human: false };
		lines.forEach(function (f) {
			if (f.length === 1 && f[0] === 'CREATE') {
				if (model.target) throw new Error('víc než jedna cílová položka');
				model.target = 'CREATE';
				return;
			}
			if (f.length < 3) throw new Error('neúplný příkaz: ' + f.join('|'));
			var item = f[0];
			if (item === 'LAST') {
				if (model.target !== 'CREATE') throw new Error('LAST bez CREATE');
			} else if (/^Q\d+$/.test(item)) {
				if (model.target && model.target !== item) throw new Error('víc cílových položek');
				model.target = item;
			} else {
				throw new Error('neznámá položka: ' + item);
			}
			var key = f[1];
			var tm = TERM_KEYS.exec(key);
			if (tm) {
				if (f.length !== 3) throw new Error('label/popis/alias s nadbytečnými poli: ' + f.join('|'));
				var val = unquote(f[2]);
				if (val === null) throw new Error('text bez uvozovek: ' + f.join('|'));
				if (val === '') return;
				var lang = tm[2];
				if (tm[1] === 'L') model.labels[lang] = val;
				else if (tm[1] === 'D') model.descriptions[lang] = val;
				else (model.aliases[lang] = model.aliases[lang] || []).push(val);
				return;
			}
			if (!CLAIM_TYPES[key]) throw new Error('nepodporovaná vlastnost: ' + key);
			checkAllowed(key, f[2]);
			var claim = { mainsnak: snak(key, parseValue(CLAIM_TYPES[key], f[2])), type: 'statement', rank: 'normal' };
			var refSnaks = null, i = 3;
			if ((f.length - 3) % 2 !== 0) throw new Error('lichý počet polí: ' + f.join('|'));
			for (; i < f.length; i += 2) {
				var p = f[i], v = f[i + 1];
				checkAllowed(p, v);
				if (QUAL_TYPES[p]) {
					if (refSnaks) throw new Error('kvalifikátor za referencí');
					claim.qualifiers = claim.qualifiers || {};
					(claim.qualifiers[p] = claim.qualifiers[p] || []).push(snak(p, parseValue(QUAL_TYPES[p], v)));
				} else if (REF_TYPES[p]) {
					var rp = 'P' + p.slice(1);
					refSnaks = refSnaks || {};
					(refSnaks[rp] = refSnaks[rp] || []).push(snak(rp, parseValue(REF_TYPES[p], v)));
				} else {
					throw new Error('nepodporovaný kvalifikátor/reference: ' + p);
				}
			}
			if (refSnaks) claim.references = [{ snaks: refSnaks }];
			model.claims.push(claim);
			if (key === 'P691') model.aut = claim.mainsnak.datavalue.value;
			if (key === 'P31' && f[2] === 'Q5') model.human = true;
			if (key === 'P569') model.birthYear = yearOf(claim.mainsnak.datavalue.value.time);
			if (key === 'P570') model.deathYear = yearOf(claim.mainsnak.datavalue.value.time);
		});
		if (!model.target) throw new Error('chybí cílová položka');
		if (!model.aut) throw new Error('chybí P691');
		model.name = model.labels.cs || model.labels.mul || model.labels.en || null;
		return model;
	}

	function yearOf(time) {
		var m = /^([+-])0*(\d+)-/.exec(time || '');
		if (!m) return null;
		return (m[1] === '-' ? '-' : '') + m[2];
	}

	function termsList(map) {
		var out = {};
		Object.keys(map).forEach(function (lang) {
			out[lang] = { language: lang, value: map[lang] };
		});
		return out;
	}

	function buildCreateData(model) {
		if (!model.name) throw new Error('záznam nemá label – zakládat bez jména nebudu');
		var data = { labels: termsList(model.labels), claims: model.claims };
		if (Object.keys(model.descriptions).length) data.descriptions = termsList(model.descriptions);
		var aliases = [];
		Object.keys(model.aliases).forEach(function (lang) {
			model.aliases[lang].forEach(function (v) { aliases.push({ language: lang, value: v }); });
		});
		if (aliases.length) data.aliases = aliases;
		return data;
	}

	function claimValueKey(dv) {
		if (!dv) return null;
		if (dv.type === 'wikibase-entityid') return dv.value.id || ('Q' + dv.value['numeric-id']);
		if (dv.type === 'time') return dv.value.time + '/' + dv.value.precision;
		return String(dv.value);
	}

	// Same rules as the Python generator for existing items (only fill what is missing).
	function buildMergeData(model, entity) {
		var skipped = [];
		var data = {};
		var labels = entity.labels || {}, descs = entity.descriptions || {}, claims = entity.claims || {};
		var existingAliases = {};
		Object.keys(entity.aliases || {}).forEach(function (lang) {
			existingAliases[lang] = (entity.aliases[lang] || []).map(function (a) { return a.value.toLowerCase(); });
		});

		if (model.labels.cs) {
			if (!labels.cs) data.labels = { cs: { language: 'cs', value: model.labels.cs } };
			else skipped.push('label cs už je („' + labels.cs.value + '“)');
		}
		if (model.descriptions.cs) {
			if (!descs.cs) data.descriptions = { cs: { language: 'cs', value: model.descriptions.cs } };
			else skipped.push('popis cs už je');
		}
		var aliases = [];
		Object.keys(model.aliases).forEach(function (lang) {
			var have = (existingAliases[lang] || []).slice();
			if (labels[lang]) have.push(labels[lang].value.toLowerCase());
			if (lang === 'cs' && data.labels && data.labels.cs) have.push(data.labels.cs.value.toLowerCase());
			model.aliases[lang].forEach(function (v) {
				if (have.indexOf(v.toLowerCase()) === -1) {
					aliases.push({ language: lang, value: v, add: '' });
					have.push(v.toLowerCase());
				}
			});
		});
		if (aliases.length) data.aliases = aliases;

		var newClaims = [];
		model.claims.forEach(function (c) {
			var p = c.mainsnak.property;
			var existing = claims[p] || [];
			var key = claimValueKey(c.mainsnak.datavalue);
			var keys = existing.map(function (e) { return claimValueKey(e.mainsnak && e.mainsnak.datavalue); });
			if (p === 'P691') {
				if (keys.indexOf(key) !== -1) { skipped.push('P691 ' + key + ' už je'); return; }
				if (keys.length) throw new Error('položka už má jiné NKČR ID (' + keys.join(', ') + ') – nepárovat');
			} else if (p === 'P569' || p === 'P570' || p === 'P31' || p === 'P21') {
				if (existing.length) { skipped.push(p + ' už je (' + keys.join(', ') + ')'); return; }
			} else if (keys.indexOf(key) !== -1) {
				skipped.push(p + ' ' + key + ' už je');
				return;
			}
			newClaims.push(c);
		});
		if (newClaims.length) data.claims = newClaims;
		return { data: data, skipped: skipped, empty: Object.keys(data).length === 0 };
	}

	function rankCandidates(model, cands) {
		var names = [model.name].concat(flatAliases(model)).filter(Boolean).map(function (s) { return s.toLowerCase(); });
		cands.forEach(function (c) {
			var score = c.hits;
			if (model.birthYear && c.birth === model.birthYear) score += 100;
			else if (model.birthYear && c.birth && c.birth !== model.birthYear) score -= 20;
			if (model.deathYear && c.death === model.deathYear) score += 30;
			if (c.allNames.some(function (n) { return names.indexOf(n) !== -1; })) score += 20;
			if (c.aut) score -= 50;
			c.score = score;
		});
		return cands.sort(function (a, b) { return b.score - a.score; });
	}

	function flatAliases(model) {
		var out = [];
		Object.keys(model.aliases).forEach(function (l) { out = out.concat(model.aliases[l]); });
		return out;
	}

	function dvText(dv) {
		if (dv.type === 'wikibase-entityid') return dv.value.id;
		if (dv.type === 'time') {
			var t = dv.value.time.replace(/^\+/, '').slice(0, 10).split('-');
			return dv.value.precision === 9 ? t[0] : dv.value.precision === 10 ? t[1] + '/' + t[0] : t[2] + '. ' + t[1] + '. ' + t[0];
		}
		return '„' + dv.value + '“';
	}

	function describeData(data) {
		var out = [];
		['labels', 'descriptions'].forEach(function (k) {
			Object.keys(data[k] || {}).forEach(function (l) {
				out.push((k === 'labels' ? 'label ' : 'popis ') + l + ': ' + data[k][l].value);
			});
		});
		(data.aliases || []).forEach(function (a) { out.push('alias ' + a.language + ': ' + a.value); });
		(data.claims || []).forEach(function (c) {
			var line = c.mainsnak.property + ' = ' + dvText(c.mainsnak.datavalue);
			Object.keys(c.qualifiers || {}).forEach(function (q) {
				line += ', ' + q + ' ' + c.qualifiers[q].map(function (sn) { return dvText(sn.datavalue); }).join(', ');
			});
			if (c.references && c.references.length) line += ' [ref: ' + Object.keys(c.references[0].snaks).join(', ') + ']';
			out.push(line);
		});
		return out;
	}

	var core = {
		extractV1: extractV1, splitV1: splitV1, parseCommands: parseCommands,
		buildCreateData: buildCreateData, buildMergeData: buildMergeData, rankCandidates: rankCandidates,
		describeData: describeData
	};
	if (typeof window === 'undefined') {
		module.exports = core;
		return;
	}

	var pageName = mw.config.get('wgPageName');
	if (pageName.indexOf(PAGE_PREFIX) !== 0 && pageName !== PAGE_PREFIX.replace(/\/$/, '')) return;
	if (!mw.config.get('wgUserName')) return;

	mw.loader.using(['mediawiki.api', 'mediawiki.util']).then(start);

	function start() {
		var api = new mw.Api();
		var pageTitle = mw.config.get('wgPageName').replace(/_/g, ' ');

		function storeGet(key) {
			try { return JSON.parse(localStorage.getItem(STORE_PREFIX + key)); } catch (e) { return null; }
		}
		function storeSet(key, val) {
			try { localStorage.setItem(STORE_PREFIX + key, JSON.stringify(val)); } catch (e) { /* no storage: results are just not remembered */ }
		}
		function isDryRun() {
			var v = storeGet('dryrun');
			return v === null ? true : !!v;
		}

		function el(tag, attrs, children) {
			var e = document.createElement(tag);
			Object.keys(attrs || {}).forEach(function (k) {
				if (k === 'text') e.textContent = attrs[k];
				else if (k === 'class') e.className = attrs[k];
				else if (k === 'onclick') e.addEventListener('click', attrs[k]);
				else e.setAttribute(k, attrs[k]);
			});
			(children || []).forEach(function (c) { if (c) e.appendChild(c); });
			return e;
		}
		// Icon in its own span so it can be nudged vertically.
		function setBtn(btn, icon, text) {
			btn.textContent = '';
			btn.appendChild(el('span', { class: 'nkcrp-ico', text: icon }));
			btn.appendChild(document.createTextNode(' ' + text));
		}
		function extLink(href, text) {
			return el('a', { href: href, target: '_blank', rel: 'noopener', text: text });
		}
		function itemLink(q, text) {
			return extLink('https://www.wikidata.org/wiki/' + q, text || q);
		}

		mw.util.addCSS([
			'.nkcrp-bar{margin:.5em 0;padding:.4em .6em;border:1px solid #a2a9b1;background:#f8f9fa;font-size:90%}',
			'.nkcrp{margin-top:6px;font-size:90%;line-height:1.4}',
			'.nkcrp button{font-size:inherit;padding:.5px 8px 1.5px;margin:2px 4px 2px 0;cursor:pointer;line-height:1.4}',
			'.nkcrp button[disabled]{cursor:default;opacity:.6}',
			'.nkcrp-ico{position:relative;top:1px}',
			'.nkcrp-panel{margin-top:4px;padding:4px 6px;border-left:3px solid #a2a9b1;background:#f8f9fa}',
			'.nkcrp-cand{padding:2px 0}',
			'.nkcrp-cand.is-year{background:#e6f4ea}',
			'.nkcrp-warn{color:#b32424}',
			'.nkcrp-muted{color:#54595d}',
			'.nkcrp-ok{color:#14866d;font-weight:bold}',
			'.nkcrp input{width:8em;font-size:inherit}',
			'.nkcrp ul{margin:2px 0 2px 1.4em;padding:0}',
			'.nkcrp pre{white-space:pre-wrap;max-height:20em;overflow:auto;font-size:85%;margin:4px 0}'
		].join('\n'));

		function searchTerms(model) {
			var seen = {}, out = [];
			var al = flatAliases(model);
			var nonLatin = al.filter(function (t) { return /[^\u0000-\u024F\u1E00-\u1EFF\s.,'‘’\-()]/.test(t); });
			var latin = al.filter(function (t) { return nonLatin.indexOf(t) === -1; });
			[model.labels.cs].concat(nonLatin, [model.labels.mul, model.labels.en], latin).forEach(function (t) {
				if (!t) return;
				var k = t.toLowerCase();
				if (seen[k]) return;
				seen[k] = 1;
				out.push(t);
			});
			return out.slice(0, 6);
		}

		function findCandidates(model) {
			var terms = searchTerms(model);
			var hits = {};
			var calls = [];
			var failed = 0;
			function fail() { failed++; }
			terms.forEach(function (t) {
				calls.push(api.get({ action: 'wbsearchentities', search: t, language: 'cs', uselang: 'cs', type: 'item', limit: 7 })
					.then(function (r) { (r.search || []).forEach(function (x) { hits[x.id] = (hits[x.id] || 0) + 1; }); }, fail));
				calls.push(api.get({
					action: 'query', list: 'search', srnamespace: 0, srlimit: 7, srprop: '',
					// No phrase quotes: NKČR mixes scripts ("Ольга Кіc" ends with a Latin c) and phrase search then finds nothing.
					srsearch: t.replace(/["~*:]/g, ' ') + (model.human ? ' haswbstatement:P31=Q5' : '')
				}).then(function (r) { ((r.query && r.query.search) || []).forEach(function (x) { hits[x.title] = (hits[x.title] || 0) + 1; }); }, fail));
			});
			calls = calls.map(function (c) { return c.then(null, function () { return $.Deferred().resolve().promise(); }); });
			return $.when.apply($, calls).then(function () {
				if (failed && failed === calls.length) return $.Deferred().reject('search', { error: { info: 'všechna hledání selhala (' + failed + '×)' } }).promise();
				return withEntities().then(function (list) { list.failed = failed; list.total = calls.length; return list; });
			});
			function withEntities() {
				var hasTarget = /^Q\d+$/.test(model.target);
				var ids = Object.keys(hits).filter(function (q) { return q !== model.target; }).slice(0, 49);
				if (!ids.length) return $.Deferred().resolve([]).promise();
				// The row's own target tells whether a pairing row is about a person.
				return api.get({ action: 'wbgetentities', ids: ids.concat(hasTarget ? [model.target] : []).join('|'), props: 'labels|descriptions|aliases|claims', uselang: 'cs' })
					.then(function (r) {
						var out = [];
						var tgt = hasTarget && r.entities && r.entities[model.target];
						var human = model.human || !!(tgt && allItems(tgt, 'P31').indexOf('Q5') !== -1);
						Object.keys(r.entities || {}).forEach(function (q) {
							if (q === model.target) return;
							var e = r.entities[q];
							if (e.missing !== undefined || e.redirects) return;
							var p31 = allItems(e, 'P31');
							if (p31.some(function (t) { return SKIP_P31.indexOf(t) !== -1; })) return;
							if (human && p31.length && p31.indexOf('Q5') === -1) return;
							var lab = pickTerm(e.labels), desc = pickTerm(e.descriptions);
							if (/^(Template|Šablona|Category|Kategorie|Module|Modul|Wikipedia|Wikipedie|Portal|Portál|Help|Nápověda):/i.test(lab)) return;
							var allNames = [];
							Object.keys(e.labels || {}).forEach(function (l) { allNames.push(e.labels[l].value.toLowerCase()); });
							Object.keys(e.aliases || {}).forEach(function (l) { e.aliases[l].forEach(function (a) { allNames.push(a.value.toLowerCase()); }); });
							out.push({
								id: q, label: lab, desc: desc, hits: hits[q] || 0, allNames: allNames,
								birth: claimYear(e, 'P569'), death: claimYear(e, 'P570'),
								aut: firstString(e, 'P691'), p31: firstItem(e, 'P31')
							});
						});
						return rankCandidates(model, out).slice(0, 8);
					});
			}
		}

		function pickTerm(terms) {
			terms = terms || {};
			var t = terms.cs || terms.mul || terms.en || terms[Object.keys(terms)[0]];
			return t ? t.value : '';
		}
		function claimYear(e, p) {
			try { return yearOf(e.claims[p][0].mainsnak.datavalue.value.time); } catch (x) { return null; }
		}
		function firstString(e, p) {
			try { return e.claims[p].map(function (c) { return c.mainsnak.datavalue.value; }).join(', '); } catch (x) { return null; }
		}
		function allItems(e, p) {
			return ((e.claims && e.claims[p]) || []).map(function (c) {
				return c.mainsnak && c.mainsnak.datavalue ? c.mainsnak.datavalue.value.id : null;
			});
		}
		function firstItem(e, p) {
			try { return e.claims[p][0].mainsnak.datavalue.value.id; } catch (x) { return null; }
		}

		function nkcrAlreadyOnWikidata(aut) {
			return api.get({ action: 'query', list: 'search', srnamespace: 0, srlimit: 1, srprop: '', srsearch: 'haswbstatement:P691=' + aut })
				.then(function (r) { var s = (r.query && r.query.search) || []; return s.length ? s[0].title : null; });
		}

		function summaryFor(model) {
			return 'NKČR ' + model.aut + ' → Wikidata ([[' + pageTitle + ']])';
		}

		function save(model, target) {
			if (target === 'CREATE') {
				var data = buildCreateData(model);
				return nkcrAlreadyOnWikidata(model.aut).then(function (found) {
					if (found) throw new Error('NKČR ' + model.aut + ' už má ' + found + ' – spáruj místo zakládání');
					var params = { action: 'wbeditentity', 'new': 'item', data: JSON.stringify(data), summary: summaryFor(model) };
					if (isDryRun()) return { dry: true, params: params, data: data };
					return api.postWithEditToken(params).then(function (r) {
						return { q: r.entity.id, rev: r.entity.lastrevid, skipped: [] };
					});
				});
			}
			return api.get({ action: 'wbgetentities', ids: target, props: 'info|labels|descriptions|aliases|claims' }).then(function (r) {
				var e = r.entities && r.entities[target];
				if (!e || e.missing !== undefined) throw new Error(target + ' neexistuje');
				if (e.redirects) throw new Error(target + ' je přesměrování na ' + e.redirects.to);
				var res = buildMergeData(model, e);
				if (res.empty) return { q: target, rev: null, skipped: res.skipped, nothing: true };
				var params = { action: 'wbeditentity', id: target, baserevid: e.lastrevid, data: JSON.stringify(res.data), summary: summaryFor(model) };
				if (isDryRun()) return { dry: true, params: params, data: res.data, skipped: res.skipped };
				return api.postWithEditToken(params).then(function (r2) {
					return { q: r2.entity.id, rev: r2.entity.lastrevid, skipped: res.skipped };
				});
			});
		}

		function apiErrorText(code, result) {
			if (result && result.error && result.error.info) return result.error.info;
			if (code instanceof Error) return code.message;
			return String(code);
		}

		function renderDone(box, done) {
			box.textContent = '';
			box.appendChild(el('span', { class: 'nkcrp-ok', text: '✓ ' }));
			box.appendChild(itemLink(done.q));
			if (done.rev) {
				box.appendChild(document.createTextNode(' · '));
				box.appendChild(extLink('https://www.wikidata.org/wiki/Special:Diff/' + done.rev, 'diff'));
			}
			if (done.nothing) box.appendChild(el('span', { class: 'nkcrp-muted', text: ' (nebylo co doplnit)' }));
			if (done.skipped && done.skipped.length) box.appendChild(el('div', { class: 'nkcrp-muted', text: 'vynecháno: ' + done.skipped.join('; ') }));
		}

		function setupRow(link) {
			var raw = extractV1(link.href);
			if (raw === null) return;
			var anchor = link.closest('span') || link;
			var box = el('div', { class: 'nkcrp' });
			anchor.parentNode.insertBefore(box, anchor.nextSibling);

			var model;
			try {
				model = parseCommands(raw);
			} catch (e) {
				box.appendChild(el('span', { class: 'nkcrp-warn', text: '⚠ odkaz nezpracuji: ' + e.message }));
				return;
			}

			var done = storeGet('done:' + model.aut);
			if (done) { renderDone(box, done); return; }

			var state = { target: model.target, busy: false, open: false };
			var mainBtn = el('button', { type: 'button' });
			var candBtn = el('button', { type: 'button' });
			var unpairBtn = el('button', { type: 'button' });
			setBtn(candBtn, '🔍', 'kandidáti ▾');
			setBtn(unpairBtn, '×', 'zrušit párování');
			var status = el('div');
			var panel = el('div', { class: 'nkcrp-panel' });
			panel.style.display = 'none';

			function refresh() {
				var t = state.target;
				setBtn(mainBtn, '⚡', (t === 'CREATE' ? 'Vytvořit novou' : 'Doplnit do ' + t) + (isDryRun() ? ' (nanečisto)' : ''));
				mainBtn.disabled = state.busy || (t === 'CREATE' && !model.name);
				mainBtn.title = (t === 'CREATE' && !model.name) ? 'záznam nemá jméno' : '';
				unpairBtn.style.display = (t !== model.target) ? '' : 'none';
				candBtn.disabled = state.busy;
			}

			function pair(q) {
				state.target = q;
				status.textContent = '';
				refresh();
			}

			unpairBtn.addEventListener('click', function () { pair(model.target); });

			mainBtn.addEventListener('click', function () {
				if (state.busy) return;
				state.busy = true;
				refresh();
				status.textContent = '… ukládám';
				var target = state.target;
				var res;
				try {
					res = save(model, target);
				} catch (e) {
					res = $.Deferred().reject(e).promise();
				}
				$.when(res).then(function (r) {
					state.busy = false;
					status.textContent = '';
					if (r.dry) {
						status.appendChild(el('div', { class: 'nkcrp-muted', text: 'Nanečisto – tohle by se poslalo (' + (r.params['new'] ? 'nová položka' : r.params.id) + '):' }));
						if (r.skipped && r.skipped.length) status.appendChild(el('div', { class: 'nkcrp-muted', text: 'vynecháno: ' + r.skipped.join('; ') }));
						status.appendChild(el('ul', {}, describeData(r.data).map(function (line) { return el('li', { text: line }); })));
						status.appendChild(el('details', {}, [el('summary', { text: 'JSON' }), el('pre', { text: JSON.stringify(r.data, null, 1) })]));
						refresh();
						return;
					}
					var d = { q: r.q, rev: r.rev, skipped: r.skipped, nothing: r.nothing, ts: Date.now() };
					storeSet('done:' + model.aut, d);
					renderDone(box, d);
				}, function (code, result) {
					state.busy = false;
					status.textContent = '';
					status.appendChild(el('span', { class: 'nkcrp-warn', text: '⚠ ' + apiErrorText(code, result) }));
					refresh();
				});
			});

			candBtn.addEventListener('click', function () {
				state.open = !state.open;
				panel.style.display = state.open ? '' : 'none';
				setBtn(candBtn, '🔍', state.open ? 'kandidáti ▴' : 'kandidáti ▾');
				if (!state.open || panel.getAttribute('data-loaded')) return;
				panel.setAttribute('data-loaded', '1');
				panel.textContent = '… hledám';
				findCandidates(model).then(function (cands) {
					panel.textContent = '';
					if (cands.failed) {
						panel.removeAttribute('data-loaded');
						panel.appendChild(el('div', { class: 'nkcrp-warn', text: '⚠ ' + cands.failed + ' z ' + cands.total + ' hledání selhalo – výsledek je neúplný, zavři a otevři kandidáty znovu' }));
					}
					if (!cands.length) panel.appendChild(el('div', { class: 'nkcrp-muted', text: 'Nic nenalezeno (hledáno: ' + searchTerms(model).join(' · ') + ')' }));
					cands.forEach(function (c) {
						var years = (c.birth || c.death) ? ' (' + (c.birth || '?') + '–' + (c.death || '') + ')' : '';
						var row = el('div', { class: 'nkcrp-cand' + (model.birthYear && c.birth === model.birthYear ? ' is-year' : '') }, [
							el('button', { type: 'button', text: 'párovat', onclick: function () { pair(c.id); } }),
							itemLink(c.id),
							document.createTextNode(' ' + (c.label || '(bez labelu)') + years),
							c.desc ? el('span', { class: 'nkcrp-muted', text: ' – ' + c.desc }) : null,
							c.aut ? el('span', { class: 'nkcrp-warn', text: ' · už má NKČR ' + c.aut }) : null
						]);
						panel.appendChild(row);
					});
					var input = el('input', { type: 'text', placeholder: 'Q…' });
					var go = el('button', { type: 'button', text: 'párovat s QID' });
					go.addEventListener('click', function () {
						var q = (input.value || '').trim().toUpperCase().replace(/^.*\/(Q\d+)$/, '$1');
						if (!/^Q\d+$/.test(q)) { input.focus(); return; }
						pair(q);
					});
					panel.appendChild(el('div', { class: 'nkcrp-cand' }, [input, go]));
				}, function (code, result) {
					panel.textContent = '';
					panel.removeAttribute('data-loaded');
					panel.appendChild(el('span', { class: 'nkcrp-warn', text: '⚠ hledání selhalo: ' + apiErrorText(code, result) }));
				});
			});

			box.appendChild(candBtn);
			box.appendChild(mainBtn);
			box.appendChild(unpairBtn);
			box.appendChild(panel);
			box.appendChild(status);
			refresh();
			box.nkcrpRefresh = refresh;
		}

		function setupBar(content) {
			var bar = el('div', { class: 'nkcrp-bar' });
			var cb = el('input', { type: 'checkbox', id: 'nkcrp-dry' });
			cb.checked = isDryRun();
			cb.addEventListener('change', function () {
				storeSet('dryrun', cb.checked);
				document.querySelectorAll('.nkcrp').forEach(function (b) { if (b.nkcrpRefresh) b.nkcrpRefresh(); });
			});
			bar.appendChild(el('strong', { text: 'NKČR párování: ' }));
			bar.appendChild(cb);
			bar.appendChild(el('label', { 'for': 'nkcrp-dry', text: ' nanečisto (nic neukládat, jen ukázat JSON)' }));
			var first = content.querySelector('table');
			if (first) first.parentNode.insertBefore(bar, first);
			else content.insertBefore(bar, content.firstChild);
		}

		mw.hook('wikipage.content').add(function ($content) {
			var content = $content[0];
			if (!content || content.getAttribute('data-nkcrp')) return;
			var links = content.querySelectorAll('a[href*="v1="]');
			if (!links.length) return;
			content.setAttribute('data-nkcrp', '1');
			setupBar(content);
			Array.prototype.forEach.call(links, setupRow);
		});
	}
}());
