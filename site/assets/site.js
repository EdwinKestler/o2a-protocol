const form = document.querySelector('.demo fieldset');
if (form) {
  const result = document.querySelector('.result');
  const title = document.querySelector('#result-title');
  const detail = document.querySelector('#result-detail');
  function evaluateExample() {
    const inputs = Object.fromEntries([...form.querySelectorAll('input')].map(input => [input.name, input.checked]));
    const missing = ['artist', 'venue', 'promoter'].filter(name => !inputs[name]);
    if (inputs.challenge) {
      result.dataset.state = 'challenged';
      title.textContent = 'Challenge needs resolution';
      detail.textContent = 'This sample policy withholds a positive result while a challenge is unresolved, even when all participants agree.';
    } else if (missing.length) {
      result.dataset.state = 'incomplete';
      title.textContent = 'More evidence needed';
      detail.textContent = `Missing: ${missing.join(', ')}. This sample requires all three statements and no unresolved challenge.`;
    } else {
      result.dataset.state = 'supported';
      title.textContent = 'Sample booking policy satisfied';
      detail.textContent = 'All three statements are present, with no challenge in this example. This supports the sample booking claim, not proof that a performance occurred.';
    }
  }
  form.addEventListener('change', evaluateExample);
  evaluateExample();
}
