import { $ } from '@/core.ts';
import Reader from '@/reader';

const sampleHTML = `
<div>
  <div id="text--content">
    <p lang="sa">granthaH</p>
  </div>
  <form id="dict--form">
    <input type="text" name="q"></input>
  </form>
  <div id="sidebar"><span lang="sa">padam</span> English</div>
</div>
`;

window.Sanscript = {
  t: jest.fn((s, from, to) => `${s}:${to}`),
}

beforeEach(() => {
  window.localStorage.clear();
});

test('Reader can be created', () => {
  const r = Reader()
  r.init();
  expect(r.script).toBe(r.uiScript);
});

test('saveSettings and loadSettings', () => {
  const oldReader = Reader()
  oldReader.fontSize = "test font size";
  oldReader.script = "test script";
  oldReader.parseLayout = "test parse layout";
  oldReader.saveSettings();

  const r = Reader()
  r.loadSettings();
  expect(r.fontSize).toBe("test font size");
  expect(r.script).toBe("test script");
  expect(r.parseLayout).toBe("test parse layout");
});

test('updateScript transliterates and updates settings', () => {
  document.write(sampleHTML);

  const r = Reader()
  r.init();
  r.uiScript = 'kannada';
  r.updateScript();

  expect($('#text--content').textContent.trim()).toBe('granthaH:kannada');
  expect($('#sidebar').textContent).toBe('padam:kannada English');
});
