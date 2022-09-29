import {
  transliterateElement, transliterateHTMLString, $,
} from './core.ts';
import Routes from './routes';

// The key to use when storing the dictionary config in local storage.
const DICTIONARY_CONFIG_KEY = 'dictionary';
// The maximum number of queries to keep in `this.history`.
const HISTORY_SIZE = 10;

export default () => ({
  script: 'devanagari',
  source: 'mw',

  // (transient data)

  // Script value as stored on the <select> widget. We store this separately
  // from `script` since we currently need to know both fields in order to
  // transliterate.
  uiScript: null,
  // The current query.
  query: '',
  // The user's search history, from least to most recent.
  history: [],

  init() {
    // URL settings take priority.
    this.loadSettingsFromURL();
    this.loadSettings();
    this.transliterate('devanagari', this.script);
  },

  /** Load source and query from the URL (if defined). */
  loadSettingsFromURL() {
    const { query, source } = Routes.parseDictionaryURL();
    this.query = query || this.query;
    this.source = source || this.source;
  },

  loadSettings() {
    const settingsStr = localStorage.getItem(DICTIONARY_CONFIG_KEY);
    if (settingsStr) {
      try {
        const settings = JSON.parse(settingsStr);
        this.script = settings.script || this.script;
        this.source = settings.source || this.source;
        this.uiScript = this.script;
      } catch (error) {
        // Old settings are invalid -- rewrite with valid values.
        this.saveSettings();
      }
    }
  },

  saveSettings() {
    const settings = {
      script: this.script,
      source: this.source,
    };
    localStorage.setItem(DICTIONARY_CONFIG_KEY, JSON.stringify(settings));
  },

  async updateSource() {
    this.saveSettings();
    // Return the promise so we can await it in tests.
    return this.searchDictionary(this.query);
  },

  updateScript() {
    this.transliterate(this.script, this.uiScript);
    this.script = this.uiScript;
    this.saveSettings();
  },

  async searchDictionary() {
    if (!this.query) {
      return;
    }

    const url = Routes.ajaxDictionaryQuery(this.source, this.query);
    const $container = $('#dict--response');
    const resp = await fetch(url);

    this.addToSearchHistory(this.query);

    if (resp.ok) {
      const text = await resp.text();
      $container.innerHTML = transliterateHTMLString(text, this.script);

      const newURL = Routes.dictionaryQuery(this.source, this.query);
      window.history.replaceState({}, '', newURL);
    } else {
      $container.innerHTML = '<p>Sorry, this content is not available right now.</p>';
    }
  },

  // Search with the given query.
  async searchFor(q) {
    this.query = q;
    this.searchDictionary();
  },

  addToSearchHistory(query) {
    // If the query is already in the history, remove it.
    this.history = this.history.filter((x) => x !== query).concat(query);

    if (this.history.length > HISTORY_SIZE) {
      this.history.shift();
    }
  },

  transliterate(oldScript, newScript) {
    transliterateElement($('#dict--response'), oldScript, newScript);
  },
});
